# Dorm Align: Roommate Compatibility System

## Project Description
The **Roommate Compatibility System: Dorm Align** is a database-driven hostel room allocation system designed to improve roommate matching through data analysis. Instead of assigning rooms randomly, the system collects students' lifestyle preferences, such as sleep schedule, cleanliness, study habits, and smoking/guest preferences, then calculates a compatibility score to identify suitable roommate pairings.

Built with **Python (Flask)** and **PostgreSQL**, the system applies core DBMS concepts such as relational modeling, normalization, primary and foreign keys, and query processing to manage student, preference, and room data efficiently. By automating compatibility analysis and room allocation while considering room capacity, Dorm Align helps reduce administrative workload, minimize roommate conflicts, and improve hostel living conditions.

## Features
- Student registration and login
- Student profile and lifestyle preference submission
- Compatibility score calculation for roommate matching
- Preference-aware allocation:
  - Double/shared roommate assignment
  - Single-room request handling
- Room assignment management with capacity checks
- Admin dashboard with:
  - Student/room statistics
  - Pending requests
  - Compatibility list
  - Assigned roommate visibility
  - Single-room request status tracking
- PostgreSQL-backed data model with normalized relational tables

## Tech Stack
- Python 3.x
- Flask
- PostgreSQL
- psycopg2
- HTML/CSS templates (Jinja2)

## Setup Guide
### 1. Clone and enter project
```bash
git clone <your-repo-url>
cd dormalign-dbms-project
```

### 2. Create and activate virtual environment
Windows (PowerShell):
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
Create `.env` from `.env.example` and fill values.

```bash
cp .env.example .env
```

Windows PowerShell alternative:
```powershell
Copy-Item .env.example .env
```

### 5. Prepare database
- Create a PostgreSQL database.
- Run schema/migration SQL files (for example `schema.sql` and migration scripts in `db/migrations/`).

### 6. Run the app
```bash
python app.py
```

Open:
`http://127.0.0.1:5001`

## Environment Variables
See `.env.example` for full list.
