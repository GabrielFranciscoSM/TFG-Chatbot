"""
Subject management router.

Provides CRUD operations for subjects. Subjects must be created explicitly
before they can be assigned to professors or students.
"""

from datetime import UTC, datetime

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from backend.config import settings
from backend.dependencies import (
    get_subjects_collection,
    get_users_collection,
    require_admin_or_professor,
)
from backend.models import UserInDB, UserRole

router = APIRouter(prefix="/admin/subjects", tags=["subjects"])


# --- Request/Response Models ---


class CreateSubjectRequest(BaseModel):
    name: str  # URL-safe identifier, e.g., "infraestructura-virtual"
    display_name: str  # Human-readable, e.g., "Infraestructura Virtual"
    guia_url: str | None = None  # Optional URL to guia docente HTML


class SubjectInfo(BaseModel):
    name: str
    display_name: str
    guia_url: str | None
    guia_indexed: bool
    created_at: datetime
    created_by: str
    student_count: int = 0
    professor_count: int = 0


class SubjectListResponse(BaseModel):
    subjects: list[SubjectInfo]
    total: int


class SubjectPublic(BaseModel):
    """Minimal subject info for public/unauthenticated access."""

    name: str
    display_name: str


# Create a second router for public endpoints (no auth required)
public_router = APIRouter(prefix="/subjects", tags=["subjects"])


# --- Helper ---


def require_admin(user: UserInDB):
    if user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")


# --- Endpoints ---


@router.post("", response_model=SubjectInfo, status_code=status.HTTP_201_CREATED)
async def create_subject(
    request: CreateSubjectRequest,
    user: UserInDB = Depends(require_admin_or_professor),
    subjects_collection=Depends(get_subjects_collection),
    users_collection=Depends(get_users_collection),
):
    """
    Create a new subject. Admin only.

    If a guia_url is provided, the system will attempt to scrape and index
    the guia docente after creating the subject.
    """
    require_admin(user)

    # Normalize name to lowercase with dashes
    subject_name = request.name.lower().replace(" ", "-").strip()

    # Check if subject already exists
    existing = subjects_collection.find_one({"name": subject_name})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Subject '{subject_name}' already exists",
        )

    # Create subject document
    now = datetime.now(UTC)
    subject_doc = {
        "name": subject_name,
        "display_name": request.display_name.strip(),
        "guia_url": request.guia_url,
        "guia_indexed": False,
        "created_at": now,
        "created_by": user.username,
    }

    # Insert into database
    subjects_collection.insert_one(subject_doc)

    # If guia_url provided, try to scrape it
    if request.guia_url:
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                # First, fetch the HTML from the guia URL
                html_response = await client.get(request.guia_url)
                html_response.raise_for_status()
                html_content = html_response.text

                # Send to chatbot service for scraping
                scrape_response = await client.post(
                    f"{settings.chatbot_service_url}/scrape_guia",
                    json={
                        "html_content": html_content,
                        "url": request.guia_url,
                        "subject_override": subject_name,
                    },
                )

                if scrape_response.status_code == 200:
                    subjects_collection.update_one(
                        {"name": subject_name}, {"$set": {"guia_indexed": True}}
                    )
                    subject_doc["guia_indexed"] = True

        except Exception:
            # Guia indexing failed, but subject was still created
            pass

    return SubjectInfo(
        name=subject_doc["name"],
        display_name=subject_doc["display_name"],
        guia_url=subject_doc["guia_url"],
        guia_indexed=subject_doc["guia_indexed"],
        created_at=subject_doc["created_at"],
        created_by=subject_doc["created_by"],
        student_count=0,
        professor_count=0,
    )


@router.get("", response_model=SubjectListResponse)
async def list_subjects(
    user: UserInDB = Depends(require_admin_or_professor),
    subjects_collection=Depends(get_subjects_collection),
    users_collection=Depends(get_users_collection),
):
    """
    List all subjects with enrollment counts.
    """
    subjects = list(subjects_collection.find())

    result = []
    for s in subjects:
        student_count = users_collection.count_documents(
            {"role": UserRole.STUDENT, "subjects": s["name"]}
        )
        professor_count = users_collection.count_documents(
            {"role": UserRole.PROFESSOR, "subjects": s["name"]}
        )

        result.append(
            SubjectInfo(
                name=s["name"],
                display_name=s["display_name"],
                guia_url=s.get("guia_url"),
                guia_indexed=s.get("guia_indexed", False),
                created_at=s["created_at"],
                created_by=s["created_by"],
                student_count=student_count,
                professor_count=professor_count,
            )
        )

    return SubjectListResponse(subjects=result, total=len(result))


@router.delete("/{subject_name}", status_code=status.HTTP_200_OK)
async def delete_subject(
    subject_name: str,
    force: bool = False,
    user: UserInDB = Depends(require_admin_or_professor),
    subjects_collection=Depends(get_subjects_collection),
    users_collection=Depends(get_users_collection),
):
    """
    Delete a subject. Admin only.

    If there are users enrolled in the subject, returns a warning unless
    force=True is provided. When force=True, the subject is removed from
    all users before deletion.
    """
    require_admin(user)

    # Check subject exists
    subject = subjects_collection.find_one({"name": subject_name})
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    # Count enrolled users
    enrolled_count = users_collection.count_documents({"subjects": subject_name})

    if enrolled_count > 0 and not force:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot delete subject with {enrolled_count} enrolled users. Use force=true to override.",
        )

    # Remove subject from all users if force
    if force and enrolled_count > 0:
        users_collection.update_many(
            {"subjects": subject_name}, {"$pull": {"subjects": subject_name}}
        )

    # Delete subject
    subjects_collection.delete_one({"name": subject_name})

    return {
        "status": "deleted",
        "subject": subject_name,
        "users_affected": enrolled_count if force else 0,
    }


@router.post("/{subject_name}/reindex-guia", response_model=SubjectInfo)
async def reindex_guia(
    subject_name: str,
    guia_url: str | None = None,
    user: UserInDB = Depends(require_admin_or_professor),
    subjects_collection=Depends(get_subjects_collection),
    users_collection=Depends(get_users_collection),
):
    """
    Re-scrape and index the guia docente for a subject.

    If guia_url is provided, updates the stored URL before scraping.
    """
    require_admin(user)

    # Check subject exists
    subject = subjects_collection.find_one({"name": subject_name})
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    # Use provided URL or existing one
    url_to_scrape = guia_url or subject.get("guia_url")
    if not url_to_scrape:
        raise HTTPException(
            status_code=400, detail="No guia URL provided and none stored"
        )

    # Update URL if new one provided
    if guia_url:
        subjects_collection.update_one(
            {"name": subject_name}, {"$set": {"guia_url": guia_url}}
        )

    # Scrape guia
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            # Fetch HTML
            html_response = await client.get(url_to_scrape)
            html_response.raise_for_status()
            html_content = html_response.text

            # Send to chatbot service
            scrape_response = await client.post(
                f"{settings.chatbot_service_url}/scrape_guia",
                json={
                    "html_content": html_content,
                    "url": url_to_scrape,
                    "subject_override": subject_name,
                },
            )

            if scrape_response.status_code != 200:
                raise HTTPException(
                    status_code=502,
                    detail=f"Chatbot service returned {scrape_response.status_code}",
                )

            subjects_collection.update_one(
                {"name": subject_name}, {"$set": {"guia_indexed": True}}
            )

    except httpx.RequestError as e:
        raise HTTPException(
            status_code=502, detail=f"Failed to fetch guia: {str(e)}"
        ) from e

    # Fetch updated subject
    updated = subjects_collection.find_one({"name": subject_name})
    student_count = users_collection.count_documents(
        {"role": UserRole.STUDENT, "subjects": subject_name}
    )
    professor_count = users_collection.count_documents(
        {"role": UserRole.PROFESSOR, "subjects": subject_name}
    )

    return SubjectInfo(
        name=updated["name"],
        display_name=updated["display_name"],
        guia_url=updated.get("guia_url"),
        guia_indexed=updated.get("guia_indexed", False),
        created_at=updated["created_at"],
        created_by=updated["created_by"],
        student_count=student_count,
        professor_count=professor_count,
    )


# --- Public Endpoints (no auth required) ---


@public_router.get("", response_model=list[SubjectPublic])
async def list_subjects_public(
    subjects_collection=Depends(get_subjects_collection),
):
    """
    List all available subjects (public endpoint, no authentication required).

    Returns minimal subject information for use in dropdowns and selection.
    """
    subjects = list(subjects_collection.find({}, {"name": 1, "display_name": 1}))

    return [
        SubjectPublic(name=s["name"], display_name=s["display_name"]) for s in subjects
    ]
