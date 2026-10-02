# MediCare Multispeciality Hospital Management System

A college-ready Hospital Management System built with **Python Flask + MySQL + Bootstrap**.

## Hospital name
**MediCare Multispeciality Hospital**

## Modules
- Admin/receptionist/doctor/nurse login
- Dashboard and statistics
- Patient registration
- Doctor and department directory
- Appointment scheduling/status
- Room management
- Patient admission and discharge
- Prescriptions
- Billing and payments
- Staff accounts
- Reports

## Requirements
- Python 3.10+
- MySQL 8+
- VS Code recommended

## Installation
1. Extract the ZIP.
2. Open the `medicare_hospital_management` folder in VS Code.
3. Create a virtual environment: `python -m venv venv`
4. Activate: `venv\\Scripts\\activate` on Windows.
5. Install: `python -m pip install -r requirements.txt`
6. In MySQL Command Line/Workbench run `database/schema.sql`.
7. Copy `.env.example` to `.env` and enter your MySQL password.
8. Create admin: `python -m flask --app app create-admin`
9. Start: `python app.py`
10. Open `http://127.0.0.1:5000`

Default application login: **admin / admin123**.

## MySQL Command Line import
`SOURCE C:/path/to/medicare_hospital_management/database/schema.sql;`

## Academic report topics
Abstract, Introduction, Problem Statement, Objectives, Existing System, Proposed System, Requirements, Feasibility Study, System Architecture, DFD, ER Diagram, UML Use Case, Database Design, Modules, Implementation, Testing, Results, Advantages, Limitations, Future Scope, Conclusion and References.

## Production note
This is an academic project. For real clinical use, add strong role-based authorization, CSRF protection, audit logs, encryption, secure secrets, backups, privacy controls, validation, monitoring and compliance review.
