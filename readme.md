# OmniHR Employee Search API

## Overview

This project is a high-performance Employee Management API built with **Django** and **Django REST Framework**. It allows organizations to manage employee records efficiently with support for:

- Employee listing & creation
- Full-text search
- Filtering by employment status
- Rate limiting (without third-party libraries)
- Dynamic columns based on organization configuration
- Strict data isolation between organizations

---

## Tech Stack

- **Language:** Python 3.12
- **Framework:** Django 5.2, Django REST Framework
- **Database:** SQLite (for development/testing)
- **Testing:** Django's built-in test framework (`unittest`)

---

## API Endpoints

### Create Organization

**POST** `/api/organizations/`

#### Request Payload:
```json
{
    "name": "MyCompany"
}
```

#### Sample Response:
```json
{
    "id": 1,
    "name": "MyCompany",
    "config": {
        "hide_columns": ["contact_email", "contact_phone", "department"]
    }
}
```

### List Organizations

**GET** `/api/organizations/`

#### Sample Response:
```json
[
    {
        "id": 1,
        "name": "MyCompany",
        "config": {
            "hide_columns": ["contact_email", "contact_phone"]
        }
    },
    {
        "id": 2,
        "name": "MyCompany 2",
        "config": {}
    }
]
```


### Create Employee

**POST** `/api/organizations/<organization_id>/employees/`

#### Request Payload:
```json
{
    "first_name": "Alice",
    "last_name": "Smith",
    "department": "HR",
    "location": "Pune",
    "position": "Manager",
    "status": "active"
}
```

#### Sample Response:
```json
{
    "id": 1,
    "first_name": "Alice",
    "last_name": "Smith",
    "department": "HR",
    "location": "Pune",
    "position": "Manager",
    "status": "active"
}
```

### List Employees

**GET** `/api/organizations/<organization_id>/employees/`

#### Query Parameters

| Param     | Type   | Description                                      |
|-----------|--------|--------------------------------------------------|
| `search`  | string | Full-text search on `first_name`, `last_name`, and `position` |
| `status`  | string | Filter employees by status (`active`, `terminated`, `not_started`) |

---

#### Example:
```bash
GET /api/organizations/1/employees/?search=alice&status=active
```

#### Sample Response:

#### Sample Response:
```json
[
    {
        "id": 1,
        "first_name": "Alice",
        "last_name": "Smith",
        "department": "HR",
        "location": "Pune",
        "position": "Manager",
        "status": "active"
    }
]
```


## Features

### Full-Text Search & Filter
- Supports filtering by `status` enum values.
- Full-text search on employee fields using `icontains`.

### Rate Limiting (No External Packages)
- Limits each IP to 5 requests in 10 seconds.
- Returns `429 Too Many Requests` if exceeded.

### Dynamic Column Control
- `Organization.config["hide_columns"]` allows customization of fields shown in responses (scaffolded for future).

### Data Isolation
- Each organization can only view or create its own employees.
- Direct database-level filtering ensures strict data separation.


## Setup Instructions

```bash
# Clone the repository
git clone https://github.com/arbaazpy/omnihr.git
cd omnihr

# Set up virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Start development server
python manage.py runserver

```

## Running Tests
```bash
python manage.py test
```

### Test coverage includes:
- Listing and creating employees
- Searching by name
- Filtering by status
- Validating invalid filters
- Rate limit handling


## Notes & Recommendations
- Use PostgreSQL in production: For efficient full-text search using `SearchVector`, switch from SQLite to PostgreSQL.

- Add pagination: Large datasets should be paginated using DRF's built-in pagination classes.

- Extend dynamic columns logic: Integrate `hide_columns` from `Organization.config` into response serialization for custom field output.

- Rate-limiting storage: Consider using Redis or Memcached instead of in-memory cache for better scalability across multiple app servers.

- API throttling with DRF: For more robust control, DRF’s `Throttle` classes can be enabled when external packages are allowed.


## Design Summary

This application is a high-performance, multi-tenant employee directory system built using Django and Django REST Framework. It follows a clean and modular design to ensure scalability, configurability, and security.

### Approach

- **RESTful API-first Design**  
  All functionalities are exposed via clean, versionable REST endpoints that are scoped per organization (`/organizations/<organization_id>/employees/`), ensuring isolation and security.

- **Modular and Clean Architecture**  
  Code is organized around apps (`employees`) and layered into models, serializers, views, and filters. Business logic is kept out of views when possible to promote maintainability.

- **Configurable Output per Organization**  
  Each organization can define a `config` JSON field (e.g., `hide_columns`) to control which employee fields appear in the response. This ensures flexibility without needing schema changes.

- **Custom Filtering and Search**  
  A lightweight implementation of search and filter functionality is included:
  - Text fields like `first_name`, `last_name`, `department`, etc., are searched using case-insensitive `icontains`.
  - Filters such as `status` are validated and applied manually.
  - `SearchVector` was intentionally **not used**, since we target compatibility with SQLite. PostgreSQL could be introduced later for scalable full-text search.

- **Basic Rate Limiting**  
  Custom middleware restricts API usage to a defined number of requests per user/IP. This is implemented without third-party libraries using a simple in-memory Python dictionary with timestamp tracking.

- **Testing without External Libraries**  
  Tests are implemented using Django’s `TestCase` and `rest_framework.test.APIClient`, with DRY base URLs and data reuse across tests for maintainability.

---

### Key Architectural Decisions

- **Scoped Organization URLs**  
  All employee operations are performed via `/organizations/<organization_id>/employees/`, which ensures tenants (organizations) are clearly separated and unauthorized access is impossible.

- **Custom Rate Limiting Middleware**  
  Avoided using tools like `drf-extensions`, `django-ratelimit`, or Redis for this task to keep the codebase clean and dependency-free. Production systems should use Redis-backed rate limiting (e.g., DRF’s `SimpleRateThrottle` or NGINX).

- **Field Hiding via Configuration**  
  Instead of building dynamic serializers, the system uses the org-level config to dynamically pop unwanted fields from the serialized response in the view layer. This simplifies performance and keeps serializers declarative.

- **SQLite as Dev Database**  
  SQLite is used for simplicity during development. PostgreSQL is recommended for production to:
  - Support `SearchVector`-based full-text search.
  - Enable ACID compliance at scale.
  - Avoid concurrency limitations in SQLite.

---

### Assumptions & Trade-offs

| Area            | Decision                    | Trade-off                                           |
|-----------------|-----------------------------|-----------------------------------------------------|
| **Search**      | Manual `icontains` search   | Simple but slower and not index-optimized           |
| **Rate Limiting** | In-memory dict             | Won’t persist across processes or restarts          |
| **Database**    | SQLite                      | Great for dev, not scalable for prod                |
| **Field Hiding**| Done in view logic          | Could move to dynamic serializer for cleaner abstraction |
| **No Auth/User**| Simplified assumption       | In real-world, API should include authentication    |
