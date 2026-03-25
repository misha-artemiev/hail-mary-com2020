# Hail Mary - Food Rescue Marketplace

A full-stack marketplace application connecting businesses with surplus food to consumers, helping reduce food waste.

## Tech Stack

### Frontend
- **React 19** with Vite
- **TailwindCSS** for styling
- **React Router** for navigation
- **ESLint** + **Prettier** for code quality

### Backend
- **FastAPI** (Python 3.14+)
- **PostgreSQL** database
- **SQLAlchemy** ORM
- **psycopg** for PostgreSQL connectivity

## Prerequisites

- **Node.js** 16+ and **npm/yarn**
- **Python** 3.14+
- **PostgreSQL** database server

## Project Structure

```
hail-mary-com2020/
├── frontend/          # React frontend application
├── backend/           # FastAPI backend application
├── README.md          # This file
```

---

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/misha-artemiev/hail-mary-com2020.git
cd hail-mary-com2020
```

### 2. Start Backend

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -e ".[dev]"

# Configure environment variables (see .env section below)
cp .env.template .env
# Edit .env with your database credentials

# Initialize database
make init-db

# Generate synthetic data (optional)
make data

# Run the backend server
make run
```

### 3. Start Frontend

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

The frontend will be available at `http://localhost:5713`

---

## Environment Variables

Create a `.env` file in the `backend/` directory:

```bash
# Backend Server
HOST_HOST="localhost"
HOST_PORT=8080
HOST_NAME="hail mary"
HOST_FORWARD_FROM="*"

# Database (update with your credentials)
DATABASE_HOST="localhost"
DATABASE_PORT=5432
DATABASE_DATABASE="hail-mary"
DATABASE_USERNAME="your_username"
DATABASE_PASSWORD="your_password"
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# Authentication
AUTH_TOKEN_EXPARATION=360
```

---

## Available Commands

### Backend (Makefile)

| Command | Description |
|---------|-------------|
| `make install` | Install Python dependencies |
| `make run` | Start the FastAPI server |
| `make init-db` | Initialize database (interactive) |
| `make init-db-noninteractive` | Initialize database (auto) |
| `make data` | Generate synthetic CSV data |
| `make upload-db` | Upload CSV data to database |
| `make upload-images` | Upload images to block storage |
| `make check` | Run syntax checks (format, typecheck, lint, audit) |
| `make check-apply` | Run checks and apply fixes |
| `make docs` | Generate API documentation |
| `make sql` | Generate SQL queries with sqlc |
| `make test` | Run unit tests |

### Frontend (npm)

| Command | Description |
|---------|-------------|
| `npm install` | Install dependencies |
| `npm run dev` | Start development server |
| `npm run build` | Build for production |
| `npm run preview` | Preview production build |
| `npm run lint` | Run ESLint |
| `npm run format` | Check formatting |
| `npm run format:fix` | Fix formatting |

---

## Database Management

### Initialize Database

Creates all tables from `database/migrations/schema.sql` and seeds static data:

```bash
make init-db
```

### Generate Synthetic Data

Generates test data (25 sellers, 50 consumers, 7 admins, 400 reservations):

```bash
make data
```

### Upload Data to Database

Loads the generated CSV files into PostgreSQL:

```bash
make upload-db
```

### Upload Images

Uploads sample images to block storage:

```bash
make upload-images
```

### Reset Database

To completely reset the database:
1. Drop all tables: `make init-db` → select option 3
2. Recreate tables: `make init-db-noninteractive` or `make init-db` → select option 1
3. Generate and upload data: `make upload-db`

---

## Development

### Backend Code Quality

```bash
cd backend

# Check code without making changes
make check

# Check and apply fixes
make check-apply
```

### Frontend Code Quality

```bash
cd frontend

# Lint code
npm run lint

# Format code
npm run format:fix
```

### Running Tests

```bash
# Backend tests
cd backend
make test

# Frontend tests (if configured)
cd frontend
npm run test
```

---

## API Documentation

Generate and view API documentation:

```bash
cd backend
make docs
```

Documentation will be available in the `docs/` directory.

---

## Additional Notes

- The backend uses **Hatch** for packaging and version management (version synced with frontend package.json)
- Database schema is defined in `backend/database/migrations/schema.sql`
- Synthetic data is generated with real Exeter, UK coordinates for sellers