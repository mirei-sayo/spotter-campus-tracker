# Spotter: Centralized Campus Lost & Found Tracker

## Project Description

Spotter is a role-based web application that digitalizes and centralizes the campus lost-and-found process. It replaces fragmented social media posts and manual office logs with a secure, searchable catalog.

When students or staff lose personal items on campus, the current reporting process is highly fragmented — leading to accountability gaps and a cluttered physical inventory for the administration. Spotter acts as a **digital bulletin board and inventory management system**. Finders can log item details into a structured database, while users who lost items can search the catalog using keyword and filter queries. A faculty dashboard allows authorized personnel to manage the inventory, process claims through a reservation mechanism, and maintain an auditable record of all transactions.

---

## Tech Stack

| Layer              | Technology                                     |
| ------------------ | ---------------------------------------------- |
| **Language**       | Python 3.9+ (OOP models for Items and Users)   |
| **Server**         | FastAPI (Python)                                |
| **Database**       | PostgreSQL (Hosted via Supabase)                |
| **Client**         | HTML5, CSS3, Vanilla JavaScript                 |
| **Deployment**     | Vercel                                          |

---

## Roles & Access

| Role        | Description                                                                                                |
| ----------- | ---------------------------------------------------------------------------------------------------------- |
| **Student** | Reports lost items, searches the found-item catalog, and reserves items for pickup (48-hour window).        |
| **Finder**  | Logs found items into the system. The system performs a duplicate check and notifies matching lost reports.  |
| **Faculty** | Manages the inventory, verifies physical ownership, resolves claim tickets, and maintains the audit log.    |

> **Note on Admin:** Faculty serves as the administrative role. Each faculty member logs in with their own account (`role: 'faculty'`) to maintain an auditable trail of who approved or resolved each claim. There is no separate "admin" role — faculty handles all moderation.

---

## Core Features

### 📋 Item Management
- **Structured Item Logging** — Capture item type, brand, color, description, unique identifiers, and location found.
- **Image Uploads** — Attach photos of lost or found items for easier identification.
- **Status Tracking** — Track items through stages: `Reported` → `Found` → `Reserved` → `Claimed` → `Closed`.

### 🔍 Search & Matching
- **Keyword Search** — Search items by name, description, brand, color, and category.
- **Filtering** — Filter by location, date range, category, and status.
- **Auto-Match Notifications** — The system cross-references "Found" reports against the "Lost" database and alerts users of potential matches.

### ⏱️ Reservation Mechanism
- When a student claims an item, it is marked as **"Reserved"** for **48 hours**.
- Faculty must verify ownership within this window; otherwise, the reservation expires and the item returns to the catalog.

### 🔐 Authentication & Role Routing
- Secure login via Supabase Auth.
- Users are routed to the correct dashboard based on their role (Student, Finder, or Faculty).

### 📊 Faculty Dashboard
- Inventory overview with item counts by status.
- Claim verification interface — approve or reject claims.
- Read-only **Audit Log** tracking all system actions (who logged, claimed, approved, etc.).

---

## Project Structure

```
spotter-campus-tracker/
│
├── server/                    # Python server (FastAPI)
│   ├── main.py                # Application entry point
│   ├── models.py              # OOP Classes (User, Item, Claim, AuditLog)
│   ├── database.py            # Supabase / PostgreSQL connection logic
│   ├── routes/                # API endpoint modules
│   │   ├── auth.py            # Authentication routes
│   │   ├── items.py           # Item CRUD routes
│   │   ├── claims.py          # Claim & reservation routes
│   │   └── admin.py           # Faculty dashboard routes
│   └── middleware.py          # Auth & role-check middleware
│
├── client/                    # Frontend assets
│   ├── css/                   # Stylesheets
│   ├── js/                    # Vanilla JavaScript modules
│   ├── assets/                # Images, icons, fonts
│   └── pages/                 # HTML pages
│       ├── index.html         # Landing / login page
│       ├── student.html       # Student dashboard
│       ├── finder.html        # Finder item-logging form
│       └── faculty.html       # Faculty management dashboard
│
├── .env                       # Environment variables (ignored by Git)
├── .gitignore                 # Git ignore rules
├── requirements.txt           # Python dependencies
└── README.md                  # Project documentation
```

---

## Getting Started

### Prerequisites
- Python 3.9+
- Git
- A [Supabase](https://supabase.com/) account (free tier works)

### Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/mirei-sayo/spotter-campus-tracker.git
   cd spotter-campus-tracker
   ```

2. **Create and activate a virtual environment**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS / Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_anon_key
   DATABASE_URL=your_postgresql_connection_string
   ```

5. **Run the development server**
   ```bash
   uvicorn server.main:app --reload
   ```

---

## Team & Responsibilities

| Member                       | Role                   |
| ---------------------------- | ---------------------- |
| Leighmarie Abigail Vicente   | Full Stack Developer   |

---

## .gitignore

The repository includes a `.gitignore` configured for Python projects:

```
# Environments
.env
.venv
env/
venv/
ENV/

# Python cache
__pycache__/
*.py[cod]
*$py.class

# IDE settings
.vscode/
.idea/

# OS files
.DS_Store
Thumbs.db

# Vercel
.vercel/
```

---

## License

This project is developed for academic purposes.