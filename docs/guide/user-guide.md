---
layout: default
title: User Guide
parent: Developer Guide
nav_order: 7
---

# User Guide

A complete guide to using the TFG Pedagogical Chatbot web interface.

---

## Getting Started

### Accessing the Application

Open [http://localhost:3000](http://localhost:3000) in your browser.

### User Roles

| Role | Capabilities |
|------|--------------|
| **Student** | Chat with assistant, take tests, view own progress, configure test preferences |
| **Professor** | Dashboard access, manage students, upload documents, view analytics, configure test defaults for students |
| **Admin** | All features + user management, subject management, system configuration |

> **Note**: The chat interface is exclusively for students. Professors access the system via their dashboard.

---

## Authentication

### Login

1. Navigate to [http://localhost:3000/login](http://localhost:3000/login)
2. Enter your **username** and **password**
3. Click **Iniciar sesión**

### Register (if enabled)

1. Click **Registrarse** on the login page
2. Fill in:
   - Email address
   - Username
   - Password (min 6 characters)
3. Click **Crear cuenta**

### Demo Accounts

For development, use the seeded accounts:

| Username | Password | Role |
|----------|----------|------|
| `admin` | `admin123` | Admin |
| `profesor` | `admin123` | Professor |
| `estudiante` | `admin123` | Student |

---

## Chat Interface

The main chat interface is where students interact with the pedagogical assistant.

### Creating a Conversation

1. Click **Nueva conversación** button
2. Enter a **title** (e.g., "Dudas sobre Docker")
3. Select a **subject** (e.g., "ISE")
4. Click **Crear**

### Chatting

1. Type your message in the input field at the bottom
2. Press **Enter** or click the send button
3. Wait for the assistant's response

### Features

- **Markdown Support**: Responses include formatted code, lists, and links
- **Code Highlighting**: Code blocks are syntax-highlighted
- **Message History**: Scroll up to see previous messages
- **Persistent Sessions**: Conversations are saved automatically

### Example Interactions

**Ask a question:**
```
¿Qué es Docker y para qué se usa?
```

**Request code examples:**
```
Muéstrame un ejemplo de docker-compose.yml
```

**Ask for explanations:**
```
Explícame la diferencia entre imágenes y contenedores
```

---

## Taking Tests

The chatbot can generate interactive tests to assess your knowledge.

### Starting a Test

Type a request like:
```
Genera un test de 5 preguntas sobre contenedores Docker
```

### During the Test

1. The assistant presents questions one at a time
2. Type your answer in the chat input
3. Receive immediate feedback
4. Continue until all questions are answered

### Test Results

After completing a test, you'll see:
- **Score**: Correct answers / Total questions
- **Feedback**: Detailed explanation for each answer
- **Areas to improve**: Suggestions for further study

---

## Session Management

### Switching Conversations

1. Click the **session selector** dropdown in the header
2. Select a previous conversation
3. Messages load automatically

### Deleting a Conversation

1. Hover over a conversation in the selector
2. Click the **trash icon**
3. Confirm deletion

---

## Professor Dashboard

Professors have access to additional features via the Dashboard.

### Accessing the Dashboard

Click **Dashboard** in the navigation menu (visible only to professors/admins).

### Overview

The dashboard shows:
- **Your subjects**: Cards for each subject you teach
- **Quick stats**: Total students, conversations, documents

### Managing Students

1. Click **Ver estudiantes** on a subject card
2. View enrolled students and their activity
3. Click **Matricular estudiante** to add new students

### Viewing Student Progress

1. Click **Ver progreso** on a subject card
2. See:
   - Conversation history
   - Test scores over time
   - Question difficulty distribution
   - Areas where students struggle

### Document Management

Upload teaching materials for RAG:

1. Click **Gestionar documentos** on a subject card
2. Click **Subir documento**
3. Select a PDF, TXT, or Markdown file
4. The document is indexed for semantic search

**Supported formats**: PDF, TXT, MD, DOCX

---

## Admin Panel

Administrators have full system control.

### Accessing Admin Panel

Click **Administración** in the navigation menu (visible only to admins).

### User Management

**View all users:**
- See username, email, role, and subjects
- Filter by role

**Promote a user:**
1. Click the **shield icon** next to a user
2. Select new role (Student → Professor → Admin)
3. Confirm promotion

**Assign subjects:**
1. Click the **book icon** next to a user
2. Select subjects to assign
3. Save changes

### Subject Management

**Create a new subject:**
1. Click **Crear asignatura**
2. Enter subject code (e.g., "ISE")
3. Enter subject name (e.g., "Infraestructura de Servidores")
4. Click **Crear**

**View subject statistics:**
- Total enrolled students
- Total conversations
- Document count

---

## Settings

Access personal settings via **Configuración** in the menu.

### Profile

View your account information:
- Email
- Username
- Role
- Assigned subjects

### Test Preferences

Configure default settings for generated tests:
- **Default number of questions**: 1-20 questions per test
- **Default difficulty**: Easy, Medium, or Hard
- **Language**: Spanish or English for test questions

These preferences are used as defaults when generating tests. You can always override them by specifying parameters in your test request.

### System Information

View the current LLM model being used by the chatbot (e.g., `gemini-2.0-flash-lite`, `Qwen/Qwen2.5-7B-Instruct`).

**Note**: Only students can access the chat feature. Professors should use their dashboard to view student progress and manage documents.

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Enter` | Send message |
| `Shift + Enter` | New line in message |
| `Esc` | Close dialogs |

---

## Tips for Effective Use

### For Students

1. **Be specific**: "¿Cómo funciona Docker networking?" vs "¿Qué es Docker?"
2. **Ask follow-ups**: Build on previous answers
3. **Request examples**: Ask for code samples and practical use cases
4. **Take tests**: Regular self-assessment helps retention

### For Professors

1. **Upload relevant materials**: PDFs of lecture notes, assignments
2. **Monitor progress**: Check dashboard weekly
3. **Review questions**: See what students struggle with

### For Admins

1. **Regular backups**: Export MongoDB data
2. **Monitor logs**: Check Grafana for errors
3. **User audits**: Review user roles periodically

---

## Troubleshooting

### Can't log in

1. Check username/password are correct
2. Clear browser cookies
3. Try incognito mode

### Chat not responding

1. Check if services are running: `docker compose ps`
2. Look for errors in browser console (F12)
3. Check chatbot logs: `docker logs tfg-chatbot`

### Documents not appearing in search

1. Wait 30 seconds for indexing
2. Check RAG service logs: `docker logs tfg-rag-service`
3. Verify Ollama is running: `docker logs ollama-service`

### Slow responses

1. First message may be slow (model loading)
2. Check Phoenix for LLM latency
3. Consider using Gemini instead of local vLLM

---

## Mobile Usage

The interface is responsive and works on mobile devices:

- **Portrait mode**: Sidebar collapses, tap to expand
- **Landscape mode**: Full interface visible
- **Touch**: Tap to select, swipe for navigation

---

## Browser Support

| Browser | Support |
|---------|---------|
| Chrome (latest) | ✅ Full |
| Firefox (latest) | ✅ Full |
| Safari (latest) | ✅ Full |
| Edge (latest) | ✅ Full |
| IE 11 | ❌ Not supported |
