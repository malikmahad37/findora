# CampusFind — Smart Lost & Found Management System

> **Tagline:** *"Lost Something? Find It. Found Something? Return It."*  
> **Type:** Full-Stack Web Application (University FYP Project)  
> **Status:** Fully Functional Production-Ready Prototype

---

## 🌟 Overview

**CampusFind** is a modern, responsive, general-purpose Lost & Found management platform designed for universities, colleges, corporate campuses, community centers, and municipal localities. It provides a structured, secure, and privacy-respecting environment where users can report lost or found belongings, evaluate automated match candidates, verify ownership before handover, and coordinate safe returns through internal messaging.

---

## 🚀 Key Features

### 1. 🔍 Rule-Based Smart Matching Algorithm
- Automatically compares newly posted Lost items against active Found listings (and vice versa).
- Transparent, non-black-box algorithmic scoring (0–100% match confidence score):
  - **Category Similarity:** 25 points (exact category classification)
  - **Item Name Similarity:** 20 points (text sequence similarity)
  - **Geographical Proximity:** 20 points (City + Region + Country match)
  - **Brand Similarity:** 10 points (brand name matching)
  - **Color Similarity:** 10 points (color attribute comparison)
  - **Date Temporal Proximity:** 10 points (decay scoring based on date difference)
  - **Description Keyword Overlap:** 5 points
- Matches exceeding the configurable 40% threshold automatically alert posters with notification badges and factor explanations (e.g., *"Same Category • Similar Name • Same City"*).

### 2. 🗺️ Dynamic Hierarchical Location System
- **Not restricted to any single university campus.**
- Scalable hierarchical structure: `Country` ➔ `Province / State / Region` ➔ `City / District` ➔ `Area / Locality / Campus`.
- Includes a starter dataset for Pakistan (e.g., *Pakistan ➔ Punjab ➔ Gujranwala ➔ Shaheenabad*).
- Interactive cascading dropdowns and instant search capability.
- Full Admin CRUD to add, modify, or remove locations at any tier.

### 3. 🛡️ Two-Way Ownership Claim & Verification
- When a user spots their lost item among the Found listings, they submit a verification claim.
- Claimant provides private identifying details (serial numbers, hidden stickers, wallpaper, contents).
- The finder reviews submitted private proof and accepts or rejects the claim.
- Accepting a claim automatically marks the item as **Returned / Resolved**.

### 4. 💬 Internal Direct Messaging System
- Database-backed internal conversation inbox and thread view.
- Contact item posters securely without publicly exposing personal mobile numbers or emails.
- Automatic unread counters and notification triggers.

### 5. 👥 User Roles & Access Control
- **Regular Users:** Report lost/found items, upload photos, manage posts, search, filter, claim items, exchange messages, toggle dark/light theme.
- **Administrators:** Site-wide statistics dashboard, user account enabling/disabling, posts moderation, status overrides, claims inspection, report resolution, category management, dynamic location hierarchy management.

### 6. 🎨 Responsive UI with Light & Dark Theme
- Modern SaaS aesthetics with clean cards, rounded corners, subtle shadows, and status tags.
- Fully responsive across Desktop, Laptop, Tablet, and Mobile screens.
- Dark mode toggle with persistent `localStorage` preference retention.

---

## 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.10+ / Flask |
| **ORM** | SQLAlchemy (Flask-SQLAlchemy) |
| **Database** | SQLite (default development), MySQL compatible |
| **Authentication** | Flask-Login with secure Werkzeug password hashing |
| **Forms & CSRF** | Flask-WTF / WTForms with CSRF tokens |
| **Frontend** | HTML5, CSS3 Custom Properties, Vanilla JavaScript |
| **Image Handling** | Secure local storage with type and file size validation (Pillow) |

---

## 📂 Project Structure

```
CampusFind/
├── app/
│   ├── __init__.py           # Flask app factory, extension registration
│   ├── models.py             # SQLAlchemy ORM models
│   ├── utils.py              # File upload, notification, audit helpers
│   ├── routes/
│   │   ├── admin.py          # Admin dashboard & management routes
│   │   ├── api.py            # Cascading location & stats JSON APIs
│   │   ├── auth.py           # Registration, login, session logout
│   │   ├── claims.py         # Ownership claim submission & verification
│   │   ├── dashboard.py      # User metrics and posts dashboard
│   │   ├── items.py          # Lost & found reporting, item CRUD
│   │   ├── main.py           # Home, Browse, Search, About, Errors
│   │   ├── messages.py       # Internal messaging inbox & chat
│   │   ├── notifications.py  # User notifications feed
│   │   ├── profile.py        # User profile & password management
│   │   └── reports.py        # Item flag and report submission
│   ├── services/
│   │   └── matching.py       # Rule-based Smart Matching algorithm
│   ├── static/
│   │   ├── css/style.css     # Responsive design with CSS theme variables
│   │   └── js/main.js        # Cascading dropdowns, modals, dark mode
│   └── templates/
│       ├── base.html         # Main layout, nav, flash alerts, footer
│       ├── index.html        # Landing page with stats & how-it-works
│       ├── about.html        # About page
│       ├── auth/             # Login & register templates
│       ├── dashboard/        # User dashboard
│       ├── items/            # Post, edit, detail, browse, search, my-posts
│       ├── messages/         # Inbox, sent, conversation
│       ├── claims/           # Submit claim, my claims, received claims
│       ├── notifications/    # Notifications feed
│       ├── reports/          # Report submission
│       ├── profile/          # Profile view, edit, password change
│       ├── admin/            # Admin console templates
│       └── errors/           # 404, 403, 500 error pages
├── config.py                 # Development and production configurations
├── requirements.txt          # Python package dependencies
├── run.py                    # Application launch script
├── seed.py                   # Database schema creation & realistic demo data
└── README.md                 # Complete documentation
```

---

## ⚙️ Installation & Setup Guide

### 1. Prerequisites
- Python 3.10 or higher installed on your system
- Git (optional)

### 2. Clone / Open Project Directory
```bash
cd d:\web\CampusFind
```

### 3. Create & Activate Virtual Environment
On Windows (PowerShell / Command Prompt):
```bash
python -m venv venv
venv\Scripts\activate
```

On Linux / macOS:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Initialize & Seed Database
This script creates all tables and inserts starter data including admin accounts, Pakistan location hierarchy, categories, and test listings:
```bash
python seed.py
```

### 6. Run the Application
```bash
python run.py
```
Open your web browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🔑 Default Development Credentials

| Role | Email | Password | Access Level |
|---|---|---|---|
| **Administrator** | `admin@campusfind.com` | `Admin@1234` | Full Admin Console & Moderation |
| **Demo User 1** | `demo@campusfind.com` | `Demo@1234` | Normal User (Owns Lost Wallet Post) |
| **Demo User 2** | `fatima@campusfind.com` | `User@1234` | Normal User (Owns Found Wallet Post) |
| **Demo User 3** | `bilal@campusfind.com` | `User@1234` | Normal User |

---

## 🎓 FYP Presentation & Viva Talking Points

When presenting this project for your University Final Year Project (FYP) defense, emphasize:

1. **Software Engineering Architecture:**
   - Modular Flask application factory pattern (`create_app`).
   - Clean separation of concerns: Models (`models.py`), Business Logic / Algorithm (`services/matching.py`), Controllers (`routes/`), and Views (`templates/`).
   - SQLAlchemy ORM database abstraction (zero SQL injection vulnerabilities, effortless migration from SQLite to MySQL/PostgreSQL).

2. **Honest, Defensible Smart Matching:**
   - Clearly state that this is a **Rule-Based Multi-Factor Similarity Algorithm** using Python text sequence matching, geospatial hierarchy, and time delta weights.
   - Avoid overselling it as a "Deep Learning Black Box" — examiners respect transparent, explainable heuristic algorithms.

3. **General Purpose Design:**
   - Explain how the dynamic location system (`Country ➔ Region ➔ City ➔ Area`) prevents the project from being a toy restricted to a single university cafeteria.

4. **Security & Data Integrity:**
   - Passwords hashed using industry-standard bcrypt/PBKDF2.
   - Session-based authentication with role authorization decorators (`@admin_required`).
   - CSRF token protection on all forms.
   - Private verification data hidden from public item cards to prevent fraudulent claims.
