<<<<<<< HEAD
# Digital Library & E-Book Circulation Portal

A modern, responsive full-stack Django web application designed for public libraries to manage authors, book catalogs, reader registries, and circulation records. Features a custom glassmorphic user interface built with Bootstrap 5, complete with dynamic ES6 JavaScript tools and visual analytics dashboards.

---

## Features

### 📚 Administration & Circulation
- **Book Catalog**: Browse items with real-time stock levels and custom metadata details.
- **Transactional Issues**: Perform real-time copy stock validations and register book loans with automatic 14-day return timelines.
- **Return Processing & Fine engine**: Process returns, register returned statuses, and compute overdue fines at ₹50/day.
- **Member Directory**: Track reader card IDs (`LIB-XXXX`), phone metrics, email identifiers, and active checkout counters.

### ⚡ JavaScript Dynamic Enhancements
- **Live Search & Filter**: AJAX-driven instant filtering by title, author, ISBN, or genre without full-page reloads.
- **Due Date Calculator**: Automatically displays Today's Date and computes the 14-day checkout limit on the issue form.
- **Late Fine Calculator**: Renders outstanding late fees in real-time.
- **Time Remaining Countdown**: Displays days remaining to due dates and applies red alerts for overdue items.
- **Theme Toggle**: Beautiful dark/light mode toggle with preference persistence in `localStorage`.
- **UI Enhancements**: Dynamic back-to-top scrolling, loading spinner, and floating Bootstrap toasts for alert messages.

### 📊 Analytics & Reports
- Interactive charts rendering:
  - Book distribution by genre.
  - Active stock levels (In-stock, Low-stock, Out of stock).
  - Monthly issue rates.

---

## Folder Structure

```text
/ (Project Root)
├── manage.py
├── requirements.txt
├── render.yaml
├── create_superuser.py
├── .gitignore
├── README.md
├── libraryproject/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── library/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   ├── forms.py
│   └── management/
│       └── commands/
│           └── populate_db.py
├── static/
│   ├── css/
│   │   └── custom.css
│   └── js/
│       └── main.js
├── templates/
│   ├── base.html
│   ├── navbar.html
│   ├── footer.html
│   ├── sidebar.html
│   ├── messages.html
│   ├── pagination.html
│   ├── catalog.html
│   ├── catalog_partial.html
│   ├── book_detail.html
│   ├── issue_book.html
│   ├── return_book.html
│   ├── members.html
│   ├── member_form.html
│   ├── history.html
│   ├── dashboard.html
│   ├── login.html
│   ├── about.html
│   ├── contact.html
│   └── 404.html
└── media/
```

---

## Technologies Used

- **Backend**: Python 3.11, Django 5.x
- **Frontend**: Bootstrap 5, Bootstrap Icons, Chart.js, Google Fonts (Outfit, Inter)
- **Database**: SQLite
- **Static Assets Manager**: WhiteNoise with Brotli compression
- **Production Server**: Gunicorn

---

## Installation & Setup

Follow these steps to run the application locally:

### 1. Initialize Virtual Environment
```bash
python -m venv .venv
```

Activate the environment:
- **Windows**:
  ```bash
  .venv\Scripts\activate
  ```
- **macOS / Linux**:
  ```bash
  source .venv/bin/activate
  ```

### 2. Install Requirements
```bash
pip install -r requirements.txt
```

### 3. Run Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Create Administrative Superuser
```bash
python create_superuser.py
```
- **Default username**: `admin`
- **Default password**: `admin123`

### 5. Seed Sample Database
Generate mock authors, books, members, and circulation logs:
```bash
python manage.py populate_db
```

### 6. Run Local Development Server
```bash
python manage.py runserver
```
Visit the local portal at `http://127.0.0.1:8000/`.

---

## Render Deployment

This repository is pre-configured for instant deployment on the **Render Free Tier**.

### Deployment settings (`render.yaml`)
Deploy via the Render Dashboard by linking your repository. The configuration applies:
- Python 3.11 runtimes.
- Automated migrations, static collections (`collectstatic`), and superuser creation.
- Production hosting with `gunicorn`.
- Environment variable configuration for `SECRET_KEY`, `ALLOWED_HOSTS`, and `CSRF_TRUSTED_ORIGINS`.

---

## Future Enhancements
- Integration of third-party E-Book reading engines (EPUB/PDF viewers).
- Support for SMS or Email notifications for overdue alerts.
- Multi-tier member subscriptions (Standard, Premium).

---

## License
Distributed under the MIT License.

---

## Author
Developed by the LibPortal Administration Team.
=======
# libraryproject
>>>>>>> 5df0a08c64f32217bc947f0f3105163ade1cf865
