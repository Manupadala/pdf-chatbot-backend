# Backend Setup Guide

## Prerequisites
- Python 3.8+

## Installation & Setup

### 1. Create Virtual Environment
```bash
python -m venv venv
```

### 2. Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

## Running the Server

```bash
uvicorn main:app --reload
```

The API will be available at: `http://localhost:8000`
API Documentation: `http://localhost:8000/docs`

## Project Structure

```
backend/
├── venv/                 # Virtual environment
├── uploads/              # Uploaded PDF files
├── routers/
│   ├── user.py          # User authentication routes
│   └── pdf.py           # PDF management routes
├── main.py              # FastAPI application entry point
├── database.py          # SQLAlchemy database configuration
├── models.py            # Database models
├── auth.py              # Authentication utilities
├── schemas.py           # Pydantic schemas
└── requirements.txt     # Python dependencies
```

## Environment Variables (Optional)

Create a `.env` file in the backend directory:
```
DATABASE_URL=sqlite:///./test.db
SECRET_KEY=your-secret-key-here
```

## API Endpoints

### User Routes
- `POST /users/register` - Register a new user
- `POST /users/login` - User login
- `GET /users/{user_id}` - Get user profile

### PDF Routes
- `POST /pdfs/upload` - Upload a PDF file
- `GET /pdfs/` - Get all PDFs
- `GET /pdfs/{pdf_id}` - Get specific PDF
- `DELETE /pdfs/{pdf_id}` - Delete a PDF
