# Running Shoe Flask API

A Flask-based REST API for managing running shoes, brands, users, and reviews. It supports JWT authentication, JSON/XML responses, search, and MySQL persistence.

## Features
- JWT auth for protected endpoints
- JSON or XML responses via `?format=xml`
- CRUD for shoes, brands, users (read-only), reviews
- Search across shoes and brands
- MySQL database using `Flask-MySQLdb`

## Requirements
- Python 3.10+
- MySQL Server (with a database named `running_shoe_db` by default)
- Packages in [requirements.txt](requirements.txt)

## Installation
```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

## Configuration
The app reads configuration from environment variables (with sane defaults):
- `MYSQL_HOST` (default: `localhost`)
- `MYSQL_USER` (default: `root`)
- `MYSQL_PASSWORD` (default: `root`)
- `MYSQL_DB` (default: `running_shoe_db`)
- `SECRET_KEY` (default: `dev-secret`)
- `JWT_EXPIRATION_DELTA` minutes (default: `60`)


## Running
Option 1: Flask CLI
```command prompt (cmd)
set FLASK_APP=runningshoeAPI.py
flask run --debug
```

Option 2: Python
```command prompt
python runningshoeAPI.py
```

## API Usage

Base URL: `http://localhost:5000`

Auth:
- `POST /auth/login` — body `{ "email": "user@example.com", "password": "..." }`
- Response: `{ token, expires_at }`
- Use token as header: `Authorization: Bearer <token>`

Shoes:
- `GET /shoes` — optional filters `brand`, `color`, `size`, `min_price`, `max_price`
- `GET /shoes/<id>`
- `POST /shoes` (auth) — `{ name, brand_id, size, color, price }`
- `PUT /shoes/<id>` (auth) — partial updates allowed
- `DELETE /shoes/<id>` (auth)

Brands:
- `GET /brands`
- `GET /brands/<id>`
- `POST /brands` (auth) — `{ name }`
- `PUT /brands/<id>` (auth)
- `DELETE /brands/<id>` (auth)

Users:
- `GET /users` (auth)
- `GET /users/<id>` (auth)

Reviews:
- `GET /reviews`
- `GET /reviews/<id>`
- `POST /reviews` (auth) — `{ user_id, shoe_id, rating, comment }`
- `PUT /reviews/<id>` (auth)
- `DELETE /reviews/<id>` (auth)

Search:
- `GET /search?q=<term>` — returns `{ shoes, brands }`

Response format:
- Add `?format=xml` to any endpoint for XML output, default is JSON.

## Postman Quick Start
1. Start the server.
2. `POST /auth/login` with a valid user to get a token.
3. For protected endpoints, set Postman Authorization to “Bearer Token” and paste the token.
4. Try `GET /shoes` or `GET /shoes?format=xml`.

## Testing
Run unit tests:
```cmd
python -m unittest app.test
```
Tests use Flask’s test client and mock DB access (`fetch_one`, `execute`) and JWT decode where needed.

## Project Structure
- `app/__init__.py` — app factory and MySQL init
- `app/routes.py` — all API endpoints and helpers
- `runningshoeAPI.py` — simple entrypoint to run the app
- `requirements.txt` — dependencies
- `README.md` — this documentation

## Notes
- Ensure you have a `users` table with `email` and `password_hash` (Werkzeug PBKDF2) for login.
- All SQL uses parameterized queries to avoid injection.

