# CyberQuest

CyberQuest is a beginner-friendly, gamified cybersecurity learning platform.

This repository currently contains **Day 1: Project Foundation**, **Day 2: Database Architecture and Initial Models**, **Day 3: User Authentication System**, **Day 4: Student Dashboard**, **Day 5: Database-Backed Learning Paths**, **Day 7: Interactive Phishing Detective Challenge**, **Days 8–10: Password Guardian, Privacy Protector and Network Navigator**, and the **Multimedia Lesson Classroom**. The public homepage surfaces real published paths and mission links, plus local-only interactive previews. Permanent XP tracking, badge awarding, leaderboards and a real conversational QuestMate AI model are intentionally not implemented yet. Lesson progress is saved per signed-in learner, and QuestMate is an animated tutor with local browser narration, not an AI model.

## What is included

- Day 1: Django project, six registered apps, Bootstrap 5 homepage, static files, base template, and homepage tests. The homepage was later refreshed with a responsive dark theme, real content previews and local-only interactions.
- Day 2: PostgreSQL-ready database configuration, custom user model, `LearningPath` and `Lesson` models, admin registration, migrations, and model tests.
- Day 3: Registration, login, POST-only logout, protected account page, responsive dark auth UI, navigation, and authentication tests.
- Day 4: Authenticated student dashboard, responsive sidebar, overview cards, demo progress, badges, QuestMate preview, and dashboard tests.
- Day 5: Six database-backed learning paths, 18 seeded introductory lessons, catalog and detail pages, admin content management, and dashboard integration.
- Day 7: Interactive Phishing Detective mission with five simulated email scenarios, server-side scoring, session state, safe link handling and a completion screen.
- Days 8–10: A four-mission challenge hub plus Password Guardian, Privacy Protector and Network Navigator, each with isolated session scoring and local-only simulations.
- Multimedia Lesson Classroom: a dedicated page for every lesson with an HTML5 video player, animated QuestMate tutor, local Web Speech narration, visual explanations, structured notes, key takeaways, server-checked questions and saved per-user progress.

## Project structure

```text
CyberQuest/
├── .venv/                  # Local virtual environment (not committed)
├── .env.example            # Environment variable template
├── manage.py               # Django command-line entry point
├── requirements.txt        # Python dependencies
├── cyberquest/             # Project settings and root URL configuration
├── apps/
│   ├── core/               # Public homepage and authenticated dashboard
│   ├── accounts/           # Custom User model, forms, auth views and tests
│   ├── learning/           # LearningPath/Lesson models, classroom views, validators, seeds and tests
│   ├── challenges/         # Phishing Detective mission, views, URLs and tests
│   ├── gamification/       # Reserved for future XP, badges, streaks and levels
│   └── mentor/             # Reserved for future QuestMate AI
├── templates/
│   ├── base.html             # Shared Bootstrap 5 layout
│   ├── core/home.html        # Homepage
│   ├── core/dashboard.html   # Authenticated student dashboard
│   ├── accounts/             # Registration, login, logout and account pages
│   ├── learning/             # Path catalog, path detail and multimedia lesson classroom
│   └── challenges/           # Challenge landing page and mission interface
└── static/
    ├── css/                # Project styles
    ├── js/                 # Project JavaScript
    └── images/             # Project images
```

## Requirements

- Windows PowerShell
- Python 3.12 or newer (Python 3.14 is used in the commands below)
- PostgreSQL is optional for local development; SQLite is the fallback
- `psycopg` is already listed in `requirements.txt`

## First-time setup

From the project root:

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Open `.env` and replace `replace-with-a-long-random-secret-key` with a fresh random secret:

```powershell
.\.venv\Scripts\python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Never commit `.env` or share the secret value.

## Environment variables

| Variable | Purpose | Default |
| --- | --- | --- |
| `DJANGO_SECRET_KEY` | Django cryptographic secret | Required when `DJANGO_DEBUG=False` |
| `DJANGO_DEBUG` | Enables Django debug mode | `True` |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated allowed hostnames | `localhost,127.0.0.1,[::1]` |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Comma-separated trusted origins | Empty |
| `LESSON_VIDEO_ALLOWED_HOSTS` | Optional host allowlist for external lesson videos (configured in settings) | Empty (any HTTP(S) direct video URL) |
| `POSTGRES_DB` | PostgreSQL database name | Unset; enables SQLite fallback |
| `POSTGRES_USER` | PostgreSQL login role | Empty |
| `POSTGRES_PASSWORD` | PostgreSQL password | Empty |
| `POSTGRES_HOST` | PostgreSQL host | `127.0.0.1` |
| `POSTGRES_PORT` | PostgreSQL port | `5432` |
| `DATABASE_URL` | Single database URL | Unset |

`DATABASE_URL` takes priority over the individual `POSTGRES_*` variables.

## Local development database

If no database variables are set, Django uses:

```text
BASE_DIR/db.sqlite3
```

That means you can keep developing without installing PostgreSQL.

## PostgreSQL setup on Windows

PostgreSQL was not installed when Day 2 was implemented, so the project continues to use the SQLite fallback until you configure it.

### 1. Install PostgreSQL

1. Download the Windows installer from <https://www.postgresql.org/download/windows/>.
2. Run the installer as administrator.
3. Keep the default port `5432` unless you have a reason to change it.
4. Set a strong password for the `postgres` superuser and store it safely.
5. Complete the installer and accept the default components.

### 2. Create a CyberQuest role and database

Open **SQL Shell (psql)** from the PostgreSQL start menu and connect as `postgres`. Then run:

```sql
CREATE ROLE cyberquest LOGIN CREATEDB PASSWORD 'choose-a-strong-password';
CREATE DATABASE cyberquest OWNER cyberquest;
```

`CREATEDB` is needed because Django creates a separate test database when running tests.

If the role already exists, update it instead:

```sql
ALTER ROLE cyberquest CREATEDB;
```

### 3. Configure `.env`

Add these lines to `.env`:

```text
POSTGRES_DB=cyberquest
POSTGRES_USER=cyberquest
POSTGRES_PASSWORD=choose-a-strong-password
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432
```

Use the same password you chose in SQL. Special characters can be used directly with the `POSTGRES_*` variables; the older `DATABASE_URL` option requires URL-encoding them.

### 4. Verify the database connection

```powershell
.\.venv\Scripts\python manage.py shell -c "from django.db import connection; connection.ensure_connection(); print('Database:', connection.vendor)"
```

Expected output when PostgreSQL is configured:

```text
Database: postgresql
```

Expected output with the fallback:

```text
Database: sqlite
```

## Initial models

### `accounts.User`

A custom user model based on Django's `AbstractUser`. It keeps standard username/password authentication and adds:

- `display_name` — optional public name
- `created_at`
- `updated_at`

`AUTH_USER_MODEL = "accounts.User"` is configured in `cyberquest/settings.py`.

### `learning.LearningPath`

Represents a course-like pathway, for example "Security Basics".

Fields include:

- `title`, `slug`, `description`
- `difficulty` — Beginner, Intermediate, or Advanced
- `estimated_duration` in minutes
- `is_published`, `created_at`, `updated_at`

The slug is unique across all learning paths.

### `learning.Lesson`

Represents one lesson inside a learning path.

Fields include:

- `learning_path` — foreign key to `LearningPath`
- `title`, `slug`, `description`, `content`
- `video_file`, `video_url`, `captions_vtt`
- `narration_text`, `transcript`, `key_takeaways`, `visual_focus`
- `order`, `estimated_minutes`, `is_published`
- `created_at`, `updated_at`

A lesson slug must be unique inside its learning path. The same slug may be reused in a different learning path. Lessons are ordered by their parent path, then `order`, then title. Choose either `video_file` or `video_url`, not both. The new classroom models are `LessonQuestion`, `LessonResponse` and `LessonProgress`; existing Day 1–10 challenge state is unchanged.

## Authentication system

### URLs

| URL | Name | Purpose |
| --- | --- | --- |
| `/accounts/register/` | `register` | Create a new account |
| `/accounts/login/` | `login` | Log in |
| `/accounts/logout/` | `logout` | Log out (POST only) |
| `/accounts/account/` | `account_home` | Temporary protected account page |
| `/learning/` | `learning_paths` | Placeholder learning catalog link |

### Registration flow

1. The user enters display name, username, email, password, and confirmation.
2. `CyberQuestUserCreationForm` validates all fields using Django's built-in validation.
3. Passwords are checked with the configured `AUTH_PASSWORD_VALIDATORS`.
4. Django hashes the password before saving it.
5. A success message is displayed.
6. The user is redirected to the login page and is **not** logged in automatically.

### Login flow

1. The user submits username and password.
2. Django's `AuthenticationForm` verifies the credentials.
3. Invalid credentials produce one generic error, so the site does not reveal whether a username exists.
4. A successful login creates a secure session.
5. The user is redirected to the account page, or to a safe `next` URL.

### Logout flow

Logout is available through a POST form with CSRF protection. GET requests to `/accounts/logout/` return HTTP 405. After logout, the user is redirected to the homepage with an informational message.

### Protected account page

`/accounts/account/` uses `@login_required`. Unauthenticated users are redirected to login with a `next` parameter. Authenticated users see their display name or username and a logout action.

### Security notes

- CSRF protection is enabled on every form.
- Passwords are never stored in plaintext.
- Sessions use HTTP-only cookies and `SameSite=Lax`.
- Secure cookie flags and HTTPS redirects are enabled when `DJANGO_DEBUG=False`.
- No social authentication, OAuth, two-factor authentication, or password reset workflow is included.

### How to test authentication

```powershell
.\.venv\Scripts\python manage.py test apps.accounts
.\.venv\Scripts\python manage.py test
```

The auth tests cover registration validation, password hashing, login, logout, safe redirects, protected-page access, and navigation.

## Student dashboard

### Dashboard features

- Authenticated-only student dashboard at `/dashboard/`.
- Responsive dark navy theme with neon green and cyan accents.
- Collapsible sidebar on mobile and a fixed sidebar on desktop.
- Welcome section using the logged-in user's display name or username.
- Four overview cards: XP, Level, Daily Streak and Badges.
- Six published learning path cards loaded from the database.
- Daily quest preview with a disabled start action.
- Learning progress overview with a responsive CSS progress ring.
- Sample badge collection.
- Static QuestMate AI conversation preview.
- Recent activity and leaderboard previews.
- POST-only logout with CSRF protection.

### Dashboard URL and access

| URL | Name | Access |
| --- | --- | --- |
| `/dashboard/` | `dashboard` | Login required |

Unauthenticated visitors are redirected to:

```text
/accounts/login/?next=/dashboard/
```

The dashboard uses the existing `accounts.User` model. No new user model, migration or authentication system was added.

After login, Day 3 still redirects to the account page at `/accounts/account/`. That page now includes an **Open Dashboard** button, so the existing authentication flow and its tests remain intact.

### Demo data explanation

Everything on the dashboard that looks like progress is clearly labelled **DEMO** or **preview**:

- XP, level, streak and badge counts are sample numbers.
- Learning paths and lessons are real database content, but no learner progress is stored.
- The daily quest is not a real challenge.
- The progress ring is not connected to real tracking.
- Badges are not awarded by the system.
- Leaderboard rows are sample learners.
- QuestMate replies are static text, not live AI output.

Real XP, challenges, badges, progress and AI integration belong to later development phases.

### How to run and verify the dashboard

```powershell
cd C:\Users\Hp\OneDrive\Desktop\CyberQuest

.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py test
.\.venv\Scripts\python.exe manage.py runserver
```

Then:

1. Open `http://127.0.0.1:8000/accounts/login/`.
2. Log in with an existing account.
3. Open `http://127.0.0.1:8000/accounts/account/`.
4. Click **Open Dashboard**.
5. Confirm the welcome name, sidebar, cards and **DEMO** labels.
6. Resize the browser to confirm the mobile menu and responsive cards.
7. Click **Logout** in the sidebar.

## Learning paths system

### What was added in Day 5

- Database-backed learning path catalog at `/learning/`.
- Database-backed path detail pages at `/learning/<slug>/`.
- Six published introductory paths with 18 published lessons.
- A repeatable Django management command that seeds content safely.
- Published-only filtering on both catalog and detail views.
- A 404 response for draft paths and unknown slugs.
- Useful Django admin list views for `LearningPath` and `Lesson`.
- Dashboard learning path cards that link to the real detail pages.

The Day 2 `LearningPath` and `Lesson` models were reused and later extended for the multimedia classroom. No duplicate apps or competing lesson systems were created.

### Initial learning paths and lessons

| Path | Slug | Lessons |
| --- | --- | --- |
| Phishing Detective | `phishing-detective` | What Is Phishing?, Spot the Warning Signs, Verify Before You Click |
| Password Guardian | `password-guardian` | Password Security Basics, Create Strong Passphrases, Multifactor Authentication |
| Privacy Protector | `privacy-protector` | Your Digital Footprint, Privacy Settings, Protect Personal Information |
| Network Navigator | `network-navigator` | Networking Fundamentals, Wi-Fi Security, Safe Network Habits |
| Mobile Defender | `mobile-defender` | Mobile Security Basics, Understanding App Permissions, Secure Your Smartphone |
| Data Defender | `data-defender` | Understanding Data Security, Backup Basics, Handle Data Responsibly |

Each lesson contains beginner-friendly explanations, headings and bullet points stored in the database. The path preview still uses Django's `linebreaks` filter. The classroom uses a small template filter that escapes every line before adding markup; arbitrary HTML is not trusted.

### Seeding the content

From the project root, run:

```powershell
.\.venv\Scripts\python.exe manage.py seed_learning_paths
```

The command uses `get_or_create`, so it can be run again without creating duplicate paths, lessons or questions. It now adds narration, transcript text, key takeaways, an animation type and two knowledge-check questions per lesson. It reports how many paths, lessons and questions were created and what the database currently contains. No videos are fabricated or downloaded.

### URLs

| URL | Name | Description |
| --- | --- | --- |
| `/learning/` | `learning_paths` | Published learning path catalog |
| `/learning/<slug>/` | `learning_path_detail` | Details and inline previews for one path |
| `/learning/<path_slug>/<lesson_slug>/` | `lesson_detail` | Multimedia classroom for one lesson |
| `/learning/<path_slug>/<lesson_slug>/answer/` | `lesson_question_answer` | Login-required, POST-only answer submission |
| `/learning/<path_slug>/<lesson_slug>/complete/` | `lesson_complete` | Login-required, POST-only completion save |
| `/dashboard/` | `dashboard` | Login-required dashboard with real path cards |

The catalog, path detail and classroom reading are public so existing public lessons still open. Answer submission and saved progress require login. Only published paths and published lessons are shown. Draft paths and invalid slugs return HTTP 404.

### Django admin content management

Open <http://127.0.0.1:8000/admin/> and sign in with a superuser account. Both models are registered:

- **Learning paths** can be searched by title, slug and description, filtered by difficulty/publication status, and ordered by title.
- **Lessons** can be searched by title, slug, description and path title, filtered by path/publication status, and ordered by path and lesson order.
- Timestamps are read-only in the admin.
- Slugs are prepopulated from titles while editing.

Unpublishing a path hides it from `/learning/`, its detail page, and the dashboard. Unpublishing a lesson hides it from the path detail page.

### How to verify Day 5

```powershell
cd C:\Users\Hp\OneDrive\Desktop\CyberQuest

.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\.venv\Scripts\python.exe manage.py test
.\.venv\Scripts\python.exe manage.py seed_learning_paths
.\.venv\Scripts\python.exe manage.py runserver
```

Then manually check:

1. Open `http://127.0.0.1:8000/learning/` and confirm six paths appear.
2. Open **Phishing Detective** and confirm three lessons appear in order.
3. Open the other five paths and confirm their three lessons appear.
4. Log in, open `/dashboard/`, and confirm the path cards link to the real detail pages.
5. In Django admin, unpublish a path and confirm it disappears from the public pages.
6. Open an unpublished path slug directly and confirm a 404 page.
7. Run the seed command again and confirm no duplicates are created.

## Multimedia lesson classroom

### What was added

- A dedicated classroom for every published lesson at `/learning/<path_slug>/<lesson_slug>/`.
- The original inline lesson preview on the path detail page is preserved; each lesson now also has an **Open classroom** link.
- Responsive HTML5 video area with native play/pause, volume and fullscreen controls, plus custom playback speed, fullscreen, loading and error states.
- Animated SVG QuestMate tutor with idle, speaking, happy, thinking and encouraging states. It is presentation-only, not a conversational AI model.
- Browser voice narration with play, pause, resume, stop, speed, voice selection, highlighted caption lines and a full transcript fallback.
- Six CSS/SVG educational animations chosen by `visual_focus`: Phishing, Password, Privacy, Network, Mobile and Data Defender.
- Structured lesson notes, key takeaways, server-checked knowledge questions and saved per-user lesson progress.
- No new npm packages, Python packages, paid APIs, speech services or external video-generation services.

### Classroom layout

Each classroom page contains:

1. **Video classroom** — uploaded video, licensed external video, or a clear no-video fallback that keeps the text lesson usable.
2. **Visual explanation** — an accessible animation for the lesson topic.
3. **QuestMate** — animated tutor plus narration controls and captions.
4. **Lesson notes** — escaped plain text rendered as headings, paragraphs, lists and callouts.
5. **Key takeaways** — one point per line in the admin.
6. **Knowledge check** — four-option questions validated on the server.
7. **Lesson navigation** — previous lesson, back to path and next lesson.

### Adding media in Django admin

1. Run `manage.py migrate`, then open <http://127.0.0.1:8000/admin/> and sign in as a superuser.
2. Open **Learning > Lessons** and edit a lesson.
3. In **Video classroom**, choose one source:
   - **Video file**: upload your own MP4, WebM or Ogg file up to 250 MB.
   - **External URL**: use a direct HTTP(S) link to an MP4, WebM or Ogg file you own or are licensed to use.
4. Optionally upload a WebVTT `.vtt` caption file. It must begin with `WEBVTT` and be 1 MB or smaller.
5. In **QuestMate narration**, add a short narration script and a fuller transcript. If only one is supplied, it is used for both.
6. In **Learning activities**, add one key takeaway per line and select an animation.
7. Use the **Lesson questions** inline editor to add up to four choices per question, mark the correct choice and add an explanation. Question order must be a positive integer and is unique within a lesson.
8. Keep **Published** checked only when the lesson is ready. Unpublishing hides it from all public learning pages.

Validation rules are enforced by `apps/learning/validators.py`:

- Videos must have a supported extension, plausible video MIME type, valid magic header and size of at most 250 MB.
- External URLs must use HTTP(S), contain no credentials and point directly to a supported video file. Set `LESSON_VIDEO_ALLOWED_HOSTS` in `cyberquest/settings.py` to restrict hosts.
- Caption files must use `.vtt`, include a WebVTT header and be 1 MB or smaller.
- A lesson cannot have both an uploaded video and an external video URL.
- Uploaded media is written to `MEDIA_ROOT` (`media/`) and served from `MEDIA_URL` (`/media/`) in development. Production deployments must serve that path from the web server or object storage.

### Narration, privacy and progress

Narration uses only the learner's browser Web Speech API and locally installed voices. CyberQuest does not send lesson text, answers or student data to an external speech service. `static/js/lesson.js` makes same-origin POST requests with CSRF tokens only for knowledge checks and completion. It uses no browser storage.

Lesson reading stays public. Knowledge-check answers and completion saves require login and return the learner to login with a `?next=` parameter when signed out. Scores are recalculated from validated server-side `LessonResponse` rows; client-supplied scores are never accepted. Re-answering updates one saved response. There is still no XP, badge, streak or leaderboard award.

### Manual testing checklist

Run the server and work through these 12 areas:

```powershell
.\.venv\Scripts\python.exe manage.py runserver
```

1. Open `/learning/phishing-detective/`; confirm the inline preview still works and **Open classroom** appears.
2. Open a lesson with no video assigned; confirm the text fallback, notes, takeaways and QuestMate still display normally.
3. In admin, upload a valid MP4/WebM/Ogg video; then try a wrong extension, wrong header and oversized file and confirm each is rejected.
4. In admin, try an external URL with `javascript:`, a web page path and credentials; confirm each is rejected. If an allowlist is configured, confirm a non-allowlisted host is rejected.
5. Try both a video file and an external URL on one lesson; confirm admin rejects the conflict.
6. Play the lesson video and check native play/pause and volume, custom speed, fullscreen and captions when a VTT file is assigned.
7. Point a lesson at a broken video URL and confirm the loading state clears, an error message appears and the transcript remains usable.
8. Press narration play, pause, resume and stop; change speed and voice; confirm the current sentence is highlighted and the transcript is available.
9. Watch QuestMate during narration and quiz events; confirm idle, speaking, thinking and happy/encouraging states are visually distinct.
10. Open lessons from all six paths and confirm the matching Phishing, Password, Privacy, Network, Mobile or Data animation renders.
11. Submit a knowledge check while signed out and confirm the sign-in notice. Sign in, answer correctly and incorrectly, review explanations, re-answer once and confirm progress updates without duplicate scoring.
12. Mark a lesson complete, use previous/next lesson links, then check desktop and mobile widths, keyboard navigation and `prefers-reduced-motion`; confirm no horizontal overflow or unwanted animation.

Run only the classroom tests with:

```powershell
.\.venv\Scripts\python.exe manage.py test apps.learning
```

## Interactive homepage

The public homepage at `/` is now a responsive landing page rather than a Day 1 placeholder.

- Hero with a local "Habit Check" preview, CTA buttons and animated console visuals.
- Four mission cards generated from the real challenge definitions and linked to their briefings.
- Three real published learning paths with accurate published-lesson counts.
- Quick safety check tabs with locally revealed guidance; no scoring and no answers stored.
- Scroll-reveal and card-tilt effects that respect `prefers-reduced-motion`.
- Authentication-aware actions: visitors see Login/Register, signed-in users see Challenge Lab and Dashboard links.

Homepage interactions live in `static/js/home.js` and scoped styles live in `static/css/site.css`. The script makes no network requests, uses no browser storage and never collects passwords or personal data. No models, migrations or permanent progress records were added.

## Phishing Detective challenge

### What was added in Day 7

- Shared challenge hub at `/challenges/`.
- Phishing briefing at `/challenges/phishing-detective/briefing/`.
- Interactive mission at `/challenges/phishing-detective/`.
- Five simulated email investigations with expandable clue panels.
- Server-side answer validation and scoring.
- Session-only mission state using Django's server-side sessions.
- Feedback after each answer with explanations and warning signs.
- Completion screen with final score, accuracy and answer review.
- Restart and Back to Learning Paths actions.
- Integration with the existing navigation, dashboard sidebar and Phishing Detective learning path.

No challenge models or migrations were added. Scenario content lives in `apps/challenges/scenarios.py`.

### Five simulated scenarios

| # | Scenario | Correct answer |
| --- | --- | --- |
| 1 | Suspicious account verification email | Phishing |
| 2 | Fake delivery notification | Phishing |
| 3 | Legitimate course announcement | Legitimate |
| 4 | Fake prize notification | Phishing |
| 5 | Password reset confirmation | Legitimate |

All senders use reserved `example` addresses. Simulated destinations use `.invalid` and are rendered only as plain text. They are never clickable, fetched or opened.

### Scoring

- Correct answer: 100 points
- Incorrect answer: 0 points
- Maximum: 500 points
- Scores are recalculated on the server from submitted answers.
- Repeated submissions for the same scenario are rejected.
- No permanent XP, badges, streaks or leaderboard points are awarded.

### URLs

| URL | Name | Access |
| --- | --- | --- |
| `/challenges/` | `challenge_home` | Login required |
| `/challenges/phishing-detective/briefing/` | `phishing_briefing` | Login required |
| `/challenges/phishing-detective/` | `phishing_challenge` | Login required |
| `/challenges/phishing-detective/restart/` | `phishing_restart` | Login required, POST only |

Anonymous visitors are redirected to login with a `?next=` parameter.

### How to launch and test

```powershell
cd C:\Users\Hp\OneDrive\Desktop\CyberQuest

.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py test
.\.venv\Scripts\python.exe manage.py runserver
```

Then:

1. Log in at `http://127.0.0.1:8000/accounts/login/`.
2. Open `http://127.0.0.1:8000/challenges/`.
3. Click **Start Mission**.
4. Expand each investigation clue, choose an answer and submit.
5. Continue through all five scenarios.
6. Confirm the final score, accuracy, review panel and restart button.

Run only the challenge tests:

```powershell
.\.venv\Scripts\python.exe manage.py test apps.challenges
```

## Password Guardian, Privacy Protector and Network Navigator (Days 8–10)

### What was added

- `/challenges/` is now a four-mission hub. It does not fabricate completion states.
- Three new mission briefings and gameplay flows built on the existing challenges app.
- A shared, database-free mission engine in `apps/challenges/missions.py`.
- Separate server-side session state for each new mission.
- Server-side validation and scoring; answer keys are never sent before submission.
- Interactive simulations in `static/js/challenges.js` with no storage or network requests.
- Scoped challenge styles in `static/css/site.css`; no changes to unrelated pages.
- No new models, migrations, XP, badges, streaks or leaderboard points.

### Mission overview

| Mission | Exercises | Scored questions | Maximum |
| --- | --- | --- | --- |
| Password Guardian | Password Strength Lab, Passphrase Builder | 5 | 500 |
| Privacy Protector | Digital Footprint Investigator, Privacy Settings Detective | 6 | 600 |
| Network Navigator | Network Fundamentals diagram, Wi-Fi Security Investigator | 7 | 700 |

**Password Guardian** teaches password reuse risks, multi-factor authentication and password-manager habits. The Password Strength Lab uses fictional samples only. It runs entirely in the browser: typed characters have no `name`, are never submitted, are not stored and are not sent anywhere. The Passphrase Builder generates a sample from an educational word list and clears it when the page is hidden.

**Privacy Protector** uses a fictional profile (`Alex Learner`) with invented details such as `example.invalid`, plus simulated privacy settings. It covers digital footprints, location permissions, photo sharing and unnecessary data requests. No social media account is connected.

**Network Navigator** uses a static diagram and four fictional Wi-Fi networks. It explains routers, IP addresses and servers, then covers public Wi-Fi, look-alike hotspots and certificate warnings. It never scans networks, contacts devices or reads device network information.

Only question steps are scored. Activities are educational and award no points. Each correct answer is worth 100 points; incorrect answers score 0. Scores are recalculated from validated answers stored in the server-side session, and duplicate submissions, arbitrary step IDs and client-supplied scores are ignored or rejected.

### URLs

| URL | Name | Access |
| --- | --- | --- |
| `/challenges/` | `challenge_home` | Login required |
| `/challenges/password-guardian/` | `password_guardian_home` | Login required |
| `/challenges/password-guardian/play/` | `password_guardian_play` | Login required |
| `/challenges/password-guardian/restart/` | `password_guardian_restart` | Login required, POST only |
| `/challenges/privacy-protector/` | `privacy_protector_home` | Login required |
| `/challenges/privacy-protector/play/` | `privacy_protector_play` | Login required |
| `/challenges/privacy-protector/restart/` | `privacy_protector_restart` | Login required, POST only |
| `/challenges/network-navigator/` | `network_navigator_home` | Login required |
| `/challenges/network-navigator/play/` | `network_navigator_play` | Login required |
| `/challenges/network-navigator/restart/` | `network_navigator_restart` | Login required, POST only |

Anonymous visitors are redirected to login with a `?next=` parameter. Each restart route resets only its own mission session.

### How to launch and test

```powershell
cd C:\Users\Hp\OneDrive\Desktop\CyberQuest

.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\.venv\Scripts\python.exe manage.py test
.\.venv\Scripts\python.exe manage.py runserver
```

Then:

1. Log in at `http://127.0.0.1:8000/accounts/login/` and open **Open Dashboard**.
2. Open `http://127.0.0.1:8000/challenges/` and confirm four mission cards.
3. Open each mission, complete its activities, submit answers and review explanations.
4. Confirm the final screen shows score, accuracy, answer review, restart and navigation links.
5. Confirm typing in the Password Strength Lab creates no network request and is not submitted.
6. Resize the browser or use DevTools device mode to confirm the hub and activity cards stay responsive.

Run only the challenge tests:

```powershell
.\.venv\Scripts\python.exe manage.py test apps.challenges
```

## Migration commands

Use the virtual environment's Python explicitly. Do not use plain `python` unless `.venv` is activated.

```powershell
.\.venv\Scripts\python manage.py check
.\.venv\Scripts\python manage.py makemigrations
.\.venv\Scripts\python manage.py migrate
.\.venv\Scripts\python manage.py test
.\.venv\Scripts\python manage.py runserver
```

If you need to use `python` directly, activate the environment first:

```powershell
.\.venv\Scripts\Activate.ps1
python manage.py check
python manage.py test
python manage.py runserver
```

Then open <http://127.0.0.1:8000/> in a browser.

The admin is available at <http://127.0.0.1:8000/admin/>. Create an admin account with `python manage.py createsuperuser` when you are ready.
