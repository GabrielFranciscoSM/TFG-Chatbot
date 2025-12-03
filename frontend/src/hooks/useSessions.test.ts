import { act, renderHook, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useSessions } from "@/hooks/useSessions";

// Mock the api module
vi.mock("@/lib/api", () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    delete: vi.fn(),
  },
}));

import api from "@/lib/api";

describe("useSessions", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("should fetch sessions on mount", async () => {
    const mockSessions = [
      {
        id: "session-1",
        title: "Test Session",
        subject: "iv",
        created_at: "2024-01-01T00:00:00Z",
        last_active: "2024-01-02T00:00:00Z",
      },
    ];

    vi.mocked(api.get).mockResolvedValue({ data: mockSessions });

    const { result } = renderHook(() => useSessions());

    expect(result.current.isLoading).toBe(true);

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.sessions).toEqual(mockSessions);
    expect(result.current.error).toBeNull();
    expect(api.get).toHaveBeenCalledWith("/sessions");
  });

  it("should handle fetch error", async () => {
    vi.mocked(api.get).mockRejectedValue(new Error("Network error"));

    const { result } = renderHook(() => useSessions());

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.error).toBe("Error al cargar las sesiones");
    expect(result.current.sessions).toEqual([]);
  });

  it("should create a new session", async () => {
    const existingSessions = [
      {
        id: "session-1",
        title: "Old Session",
        subject: "tfg",
        created_at: "2024-01-01T00:00:00Z",
        last_active: "2024-01-01T00:00:00Z",
      },
    ];

    const newSession = {
      id: "session-2",
      title: "New Session",
      subject: "iv",
      created_at: "2024-01-02T00:00:00Z",
      last_active: "2024-01-02T00:00:00Z",
    };

    vi.mocked(api.get).mockResolvedValue({ data: existingSessions });
    vi.mocked(api.post).mockResolvedValue({ data: newSession });

    const { result } = renderHook(() => useSessions());

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    let createdSession: unknown;
    await act(async () => {
      createdSession = await result.current.createSession("New Session", "iv");
    });

    expect(createdSession).toEqual(newSession);
    expect(result.current.sessions).toContainEqual(newSession);
    expect(api.post).toHaveBeenCalledWith("/sessions", {
      title: "New Session",
      subject: "iv",
    });
  });

  it("should delete a session", async () => {
    const mockSessions = [
      {
        id: "session-1",
        title: "Session 1",
        subject: "iv",
        created_at: "2024-01-01T00:00:00Z",
        last_active: "2024-01-01T00:00:00Z",
      },
      {
        id: "session-2",
        title: "Session 2",
        subject: "tfg",
        created_at: "2024-01-02T00:00:00Z",
        last_active: "2024-01-02T00:00:00Z",
      },
    ];

    vi.mocked(api.get).mockResolvedValue({ data: mockSessions });
    vi.mocked(api.delete).mockResolvedValue({});

    const { result } = renderHook(() => useSessions());

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.sessions).toHaveLength(2);

    let success: boolean | undefined;
    await act(async () => {
      success = await result.current.deleteSession("session-1");
    });

    expect(success).toBe(true);
    expect(result.current.sessions).toHaveLength(1);
    expect(result.current.sessions[0].id).toBe("session-2");
    expect(api.delete).toHaveBeenCalledWith("/sessions/session-1");
  });

  it("should sort sessions by last_active descending", async () => {
    const mockSessions = [
      {
        id: "session-old",
        title: "Old",
        subject: "iv",
        created_at: "2024-01-01T00:00:00Z",
        last_active: "2024-01-01T00:00:00Z",
      },
      {
        id: "session-new",
        title: "New",
        subject: "iv",
        created_at: "2024-01-02T00:00:00Z",
        last_active: "2024-01-03T00:00:00Z",
      },
    ];

    vi.mocked(api.get).mockResolvedValue({ data: mockSessions });

    const { result } = renderHook(() => useSessions());

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    // Should be sorted with newest first
    expect(result.current.sessions[0].id).toBe("session-new");
    expect(result.current.sessions[1].id).toBe("session-old");
  });
});
