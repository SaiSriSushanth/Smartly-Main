# Smartly Repository Review + Hardening Plan (Claude CLI Handoff)

## Context
This repository is a Django application for document and YouTube transcript processing with multi-provider LLM routing.

Use this document as the execution plan for:
1. Full prioritized code review.
2. Security + performance hardening implementation.
3. Router-focused review and fixes.

---

## Scope
- Project root: `Smartly-Main`
- Primary code areas:
  - `smartly/settings.py`
  - `smartly/urls.py`
  - `docprocessor/models.py`
  - `docprocessor/views.py`
  - `docprocessor/utils.py`
  - `docprocessor/services.py`
  - `docprocessor/tasks.py`
  - `requirements.txt`

---

## 1) Prioritized Code Review Checklist

### P0 — likely runtime defects
- [ ] **Fix stale file-path references** where code uses `d.file.path` / `doc.file.path` even though documents are stored in DB via `file_content`.
  - Known locations:
    - `process_multi_documents`
    - `library_view`
    - `library_recommend_projects`
- [ ] Ensure all extraction paths follow one of:
  - temp file from `file_content` + extractor utility, or
  - direct text extraction abstraction that supports binary payloads.

### P1 — security / production gaps
- [ ] Remove hardcoded `SECRET_KEY` and source from environment.
- [ ] Replace permissive `ALLOWED_HOSTS = ["*"]` with environment-driven hosts.
- [ ] Ensure production-safe defaults for `DEBUG`, cookies, CSRF/session security, and HSTS policy.
- [ ] Review auth-bound endpoints for ownership checks consistency.

### P1 — reliability / behavior consistency
- [ ] Unify model fallback policy:
  - `settings.ALLOW_MODEL_FALLBACKS` should drive fallback behavior in router logic.
- [ ] Normalize provider error messages and keep user-safe wording.
- [ ] Add robust JSON parsing/validation for model responses in library topic/project generation.

### P2 — maintainability
- [ ] Refactor oversized `views.py` into modules (e.g., `views_chat.py`, `views_docs.py`, `views_library.py`, `views_youtube.py`).
- [ ] Create shared helper for "extract text from Document (binary-backed)" to avoid repeated temp-file code.
- [ ] Add unit tests around extraction paths and chat routing.

---

## 2) Router-Specific Review (Important)

### URL router (Django)
- [ ] Confirm root URL includes app router cleanly and no conflicting names.
- [ ] Validate auth requirements for all state-changing routes.

### AI provider router (`_route_chat` in `docprocessor/utils.py`)
- [ ] Verify deterministic provider selection rules:
  - Anthropic branch
  - Gemini branch
  - Hugging Face/provider router branch
  - OpenAI default branch
- [ ] Ensure fallback behavior obeys environment policy (strict vs permissive).
- [ ] Add tests for routing by model string examples:
  - `claude-*`
  - `gemini-*`
  - `org/repo[:provider]`
  - default GPT model
- [ ] Validate output normalization (`content` extraction, list segments, `<think>` stripping).

---

## 3) Security + Performance Hardening Patch Set

### Security tasks
- [ ] Settings hardening:
  - `SECRET_KEY` from env.
  - `ALLOWED_HOSTS` from env list.
  - `DEBUG` defaults to False unless explicitly enabled for dev.
- [ ] Add/verify:
  - `CSRF_COOKIE_SECURE`
  - `SESSION_COOKIE_SECURE`
  - `SECURE_SSL_REDIRECT` (env toggled)
  - HSTS settings (prod env toggled)
- [ ] Ensure sensitive errors are not exposed to end users.

### Performance tasks
- [ ] Remove repeated extraction overhead by introducing caching/abstraction layer for extracted text snippets.
- [ ] Bound context sizes consistently across chat + YouTube chat.
- [ ] Move expensive recommendation/categorization operations to async tasks where feasible.
- [ ] Audit query efficiency and add `select_related/prefetch_related` where needed.

### Dependency hygiene
- [ ] Deduplicate `requirements.txt` entries.
- [ ] Pin critical infrastructure dependencies for reproducible deploys.

---

## 4) Implementation Guidance

### Suggested order
1. Fix P0 file-path/runtime defects.
2. Harden settings/security defaults.
3. Wire fallback policy consistently in router.
4. Clean dependency file.
5. Add regression tests.
6. Optional modular refactor of views.

### Coding constraints
- Preserve existing UX/routes unless explicitly changing behavior.
- Prefer minimal-risk patches first, then refactors.
- Keep migration impact minimal unless schema change is required.

---

## 5) Required Deliverables

### A. Review Report (`REVIEW_REPORT.md`)
Must include:
- Severity table (P0/P1/P2)
- Impact and reproduction notes
- Exact file/line references
- Proposed fix summary per issue

### B. Hardening PR
Must include:
- Code changes for P0 + security baseline
- Router fallback policy consistency
- Requirements cleanup
- Tests for critical paths

### C. Validation Output
Include command outputs for:
- `python manage.py check`
- `python manage.py test` (or targeted tests)
- Any lint/type checks used

---

## 6) Acceptance Criteria

- [ ] No stale `*.file.path` usages remain for `Document` model extraction paths.
- [ ] Production settings are env-driven and secure by default.
- [ ] Router behavior is deterministic and policy-controlled.
- [ ] Tests cover routing + extraction regressions.
- [ ] Dependency file has no duplicate package entries.

---

## 7) Copy/Paste Prompt for Claude CLI

Use this exact prompt:

```text
You are reviewing and hardening a Django codebase named Smartly.

Follow the plan in CLAUDE_HANDOFF_REVIEW_HARDENING.md exactly.

Deliver:
1) REVIEW_REPORT.md with prioritized issues (P0/P1/P2), exact file references, and fix strategy.
2) Implement code fixes for all P0 and core P1 security/router issues.
3) Add/adjust tests for extraction paths and _route_chat provider routing.
4) Deduplicate requirements.txt and keep dependency intent intact.
5) Provide verification command outputs (manage.py check/tests).

Constraints:
- Keep behavior stable unless fix requires change.
- Prefer minimal-risk patches first.
- Use env-driven settings for secrets/hosts/security toggles.
- Ensure fallback policy is centralized and consistent.
```

---

## 8) Notes
- Prioritize correctness and production safety over refactor depth.
- If time is limited: complete P0 + settings hardening + router fallback consistency first.
