# City Public Library Management System

A full-stack Library Management System built using **FastAPI, Python, SQLite, HTML, CSS, and JavaScript**. The application helps manage books, library members, book borrowing and returns, overdue loans, fines, and reports through a web-based interface.

## Features

### Book Management
- View and search the book catalogue.
- Track book inventory and copy availability.
- Retrieve book information through REST APIs.

### Member Management
- Member registration and login.
- Token-based member authentication.
- Access member profiles and personal loan records.

### Loan Management
- Issue books to registered members.
- View active borrowing records.
- Track checkout dates and due dates.
- Return borrowed books.
- Enforce borrowing limits and book availability rules.

### Fine Management
- Calculate fines for overdue returns.
- View outstanding fines.
- Pay fines through the application.

### Librarian Dashboard
- Librarian login with session-based authentication.
- Manage book checkouts and returns.
- View active loans and overdue books.
- Review inventory and library reports.

### Reports
- Overdue loan reports.
- Most-borrowed books report.
- Summary information for library operations.

### Partner API
- Access book catalogue information using API key and API secret authentication.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| FastAPI | REST API development |
| SQLite | Database management |
| HTML5 | Frontend structure |
| CSS3 | Styling and responsive layout |
| JavaScript | Frontend functionality and API integration |
| Uvicorn | Running the FastAPI application |
| Pytest | Automated testing |

## Project Structure

```text
City-Public-Library/
│
├── backend/
│   ├── app/
│   │   ├── routers/
│   │   │   ├── books.py
│   │   │   ├── fines.py
│   │   │   ├── loans.py
│   │   │   ├── members.py
│   │   │   ├── partners.py
│   │   │   └── reports.py
│   │   │
│   │   ├── services/
│   │   │   └── library_service.py
│   │   │
│   │   ├── auth.py
│   │   ├── database.py
│   │   ├── dependencies.py
│   │   ├── main.py
│   │   ├── schema.py
│   │   └── verify_db.py
│   │
│   ├── database/
│   │   ├── library.db
│   │   ├── schema.sql
│   │   └── seed.sql
│   │
│   ├── tests/
│   │   └── test_smoke.py
│   │
│   ├── .env
│   ├── .gitignore
│   ├── requirement.txt
│   └── scripts_set_demo_passwords.py
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   ├── script.js
│   ├── auth.js
│   ├── member_login.html
│   ├── member_dashboard.html
│   ├── librarian_login.html
│   └── librarian_dashboard.html
│
└── README.md
```

## Installation and Setup

### Prerequisites

- Python 3.10 or a compatible version.
- pip package manager.
- Visual Studio Code.
- A modern web browser.
- Live Server extension for running the frontend locally.

### 1. Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd City-Public-Library
```

Replace the placeholder with your actual GitHub repository URL.

### 2. Create a Virtual Environment

Run from the project root:

```powershell
python -m venv venv
```

Activate it using Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

Alternatively, use Command Prompt:

```bat
venv\Scripts\activate.bat
```

### 3. Install Dependencies

```powershell
pip install -r backend/requirement.txt
```

### 4. Start the Backend

From the project root, run:

```powershell
uvicorn backend.app.main:app --reload
```

The backend API will be available at:

http://127.0.0.1:8000

### 5. Explore API Documentation

Open the following URL in your browser:

http://127.0.0.1:8000/docs

FastAPI's Swagger UI allows you to inspect endpoints, submit requests, and review API responses.

### 6. Start the Frontend

1. Open the `frontend` folder in Visual Studio Code.
2. Open `index.html`.
3. Click **Go Live** using the Live Server extension.
4. Keep the backend running while using the frontend.

The frontend and backend must be configured to communicate with each other.

## API Endpoints

The following are the main application endpoints.

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Backend health check |
| GET | `/books/` | Retrieve book catalogue |
| POST | `/members/login` | Member login |
| POST | `/members/staff/login` | Librarian login |
| POST | `/loans/checkout` | Check out a book |
| GET | `/loans/my` | Retrieve the logged-in member's loans |
| GET | `/loans/active` | Retrieve active loans for the librarian |
| POST | `/loans/{loan_id}/return` | Return a borrowed book |
| GET | `/fines/my` | Retrieve the member's fines |
| POST | `/fines/{fine_id}/pay` | Pay a fine |
| GET | `/reports/overdue` | Retrieve overdue loan reports |
| GET | `/reports/most-borrowed` | Retrieve most-borrowed book reports |
| GET | `/partner/books` | Access the partner book catalogue API |

Protected endpoints require the appropriate authentication credentials. Refer to `/docs` for request parameters, response schemas, and other available endpoints.

## Authentication

The application supports different authentication mechanisms:

- **Member authentication:** Token-based authentication using a bearer token.
- **Librarian authentication:** Session-based authentication using cookies.
- **Partner authentication:** API key and API secret.

Authentication credentials must be supplied according to the requirements of each protected endpoint.

## Database

The application uses SQLite to store library data.

| File | Purpose |
|---|---|
| `library.db` | SQLite database |
| `schema.sql` | Database schema definitions |
| `seed.sql` | Initial or sample database records |

The database supports book inventory, member information, loans, returns, and fine-related operations.

## Testing

The project includes automated smoke tests using Pytest.

Run the tests from the project root:

```powershell
python -m pytest backend/tests/test_smoke.py
```

Ensure the virtual environment is activated and all required dependencies are installed before running the tests.

## Security Considerations

- Use parameterized SQL queries to help prevent SQL injection.
- Hash passwords before storing them.
- Protect restricted routes with authentication and authorization checks.
- Keep API secrets and other credentials out of public repositories.
- Exclude sensitive environment files from version control.
- Configure CORS appropriately when running the frontend and backend on separate local origins.

## Future Enhancements

- Add advanced search, filtering, and pagination.
- Improve member and inventory management.
- Add fine payment history and notifications.
- Introduce more granular role-based permissions.
- Add production deployment and logging configuration.

## Learning Outcomes

This project demonstrates practical experience with:

- REST API development using FastAPI.
- Database operations using SQLite.
- Token-based and session-based authentication.
- API key and secret authentication.
- Frontend and backend integration.
- Library borrowing and return workflows.
- Automated testing with Pytest.

## Author

**Gaurav**

*City Public Library Management System — a project focused on backend development, database management, API integration, authentication, and frontend development.*
