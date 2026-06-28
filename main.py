from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    UploadFile,
    File,
    Form
)

from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import os

from database import engine, SessionLocal
from models import Base, User, ChatHistory, PDFFile
from schemas import UserCreate, UserLogin
from auth import (
    hash_password,
    verify_password,
    create_access_token
)
from pdf_utils import (
    extract_text,
    create_chunks
)

from vector_store import (
    create_embeddings
)
from pdf_utils import extract_text
from pdf_utils import (
    extract_text,
    create_chunks
)
from fastapi.responses import StreamingResponse
from ollama_utils import ask_llm_stream

from vector_store import (
    create_embeddings,
    build_faiss_index,
    search_chunks
)
from schemas import (
    UserCreate,
    UserLogin,
    QuestionRequest,
    PDFRequest
)

from ollama_utils import ask_llm

from vector_store import (
    create_embeddings,
    build_faiss_index,
    search_chunks
)

from pdf_utils import (
    extract_text,
    create_chunks
)
selected_pdf = None
Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Database Session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def home():
    return {
        "message": "Backend Running"
    }


@app.post("/register")
def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):

    existing = db.query(User).filter(
        User.email == user.email
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    new_user = User(
        username=user.username,
        email=user.email,
        password=hash_password(user.password)
    )

    db.add(new_user)
    db.commit()

    return {
        "message": "User Registered"
    }


@app.post("/login")
def login(
    user: UserLogin,
    db: Session = Depends(get_db)
):

    db_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if not db_user:
        raise HTTPException(
            status_code=400,
            detail="Invalid Email"
        )

    if not verify_password(
        user.password,
        db_user.password
    ):
        raise HTTPException(
            status_code=400,
            detail="Wrong Password"
        )

    token = create_access_token(
        {
            "email": db_user.email
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }
@app.post("/upload-pdf")
async def upload_pdf(
    file: UploadFile = File(...),
    email: str = Form(...),
    db: Session = Depends(get_db)
):

    global selected_pdf

    user_folder = f"uploads/{email}"

    os.makedirs(
        user_folder,
        exist_ok=True
    )

    file_path = f"{user_folder}/{file.filename}"

    with open(
        file_path,
        "wb"
    ) as buffer:

        buffer.write(
            await file.read()
        )

    selected_pdf = file.filename

    pdf = PDFFile(
        filename=file.filename,
        user_email=email
    )

    db.add(pdf)
    db.commit()

    return {
        "message": "PDF Uploaded Successfully",
        "filename": file.filename
    }

@app.post("/select-pdf")
def select_pdf(data: PDFRequest):

    global selected_pdf

    selected_pdf = data.filename

    return {
        "message": "PDF selected"
    }
@app.get("/test-pdf")
def test_pdf():

    text = extract_text(
        "uploads/sample.pdf"
    )

    return {
        "text": text[:1000]
    }
@app.get("/test-embedding")
def test_embedding():

    text = extract_text(
        "uploads/sample.pdf"
    )

    chunks = create_chunks(
        text
    )

    embeddings = create_embeddings(
        chunks
    )

    return {
        "chunks": len(chunks),
        "embedding_shape":
        embeddings.shape
    }

@app.get("/test-search")
def test_search():

    text = extract_text(
        "uploads/sample.pdf"
    )

    chunks = create_chunks(
        text
    )

    embeddings = create_embeddings(
        chunks
    )

    index = build_faiss_index(
        embeddings
    )

    results = search_chunks(
        "What is Artificial Intelligence?",
        chunks,
        index
    )

    return {
        "results": results
    }


@app.post("/ask")
def ask_question(
    request: QuestionRequest,
    db: Session = Depends(get_db)
):

    global selected_pdf

    if not selected_pdf:
        raise HTTPException(
            status_code=400,
            detail="No PDF selected"
        )
    print("Using PDF:", selected_pdf)
    text = extract_text(
    f"uploads/{request.email}/{request.filename}"
)

    chunks = create_chunks(
        text
    )

    embeddings = create_embeddings(
        chunks
    )

    index = build_faiss_index(
        embeddings
    )

    relevant_chunks = search_chunks(
        request.question,
        chunks,
        index
    )

    context = "\n".join(
        relevant_chunks
    )

    prompt = f"""
Use ONLY the context below.

Context:
{context}

Question:
{request.question}

Answer:
"""

    answer = ask_llm(
    prompt
)

    chat = ChatHistory(
    pdf_name=request.filename,
    question=request.question,
    answer=answer
)

    db.add(chat)
    db.commit()

    return {
    "answer": answer
}

@app.post("/ask-stream")
def ask_stream(
    request: QuestionRequest,
    db: Session = Depends(get_db)
):

    if not request.filename:
     raise HTTPException(
        status_code=400,
        detail="No PDF selected"
    )
    import os

    file_path = f"uploads/{request.email}/{request.filename}"

    if not os.path.exists(file_path):
     raise HTTPException(
        status_code=404,
        detail="PDF not found"
    )

    text = extract_text(file_path)
    text = extract_text(
     f"uploads/{request.email}/{request.filename}"
)

    chunks = create_chunks(text)

    embeddings = create_embeddings(chunks)

    index = build_faiss_index(embeddings)

    relevant_chunks = search_chunks(
        request.question,
        chunks,
        index
    )

    context = "\n".join(relevant_chunks)

    prompt = f"""
Use ONLY the context below.

Context:
{context}

Question:
{request.question}

Answer:
"""

    def generate():

        answer = ""

        for chunk in ask_llm_stream(prompt):

            answer += chunk

            yield chunk

        chat = ChatHistory(
        user_email=request.email,
        pdf_name=request.filename,
        question=request.question,
        answer=answer
     )

        db.add(chat)
        db.commit()

    return StreamingResponse(
        generate(),
        media_type="text/plain"
    )
@app.get("/pdfs")
def get_pdfs(
    email: str,
    db: Session = Depends(get_db)
):

    pdfs = (
        db.query(PDFFile)
        .filter(
            PDFFile.user_email == email
        )
        .all()
    )

    return {
        "pdfs": [
            pdf.filename
            for pdf in pdfs
        ]
    }

@app.get("/history")
def get_history(
    email: str,
    db: Session = Depends(get_db)
):

    chats = (
        db.query(ChatHistory)
        .filter(ChatHistory.user_email == email)
        .order_by(ChatHistory.id.desc())
        .all()
    )

    return chats
@app.delete("/history/{id}")
def delete_history(
    id: int,
    email: str,
    db: Session = Depends(get_db)
):

    chat = (
        db.query(ChatHistory)
        .filter(
            ChatHistory.id == id,
            ChatHistory.user_email == email
        )
        .first()
    )

    if not chat:
        raise HTTPException(
            status_code=404,
            detail="History not found"
        )

    db.delete(chat)
    db.commit()

    return {
        "message": "Deleted"
    }
@app.delete("/delete-pdf/{filename}")
def delete_pdf(
    filename: str,
    email: str,
    db: Session = Depends(get_db)
):

    pdf = (
        db.query(PDFFile)
        .filter(
            PDFFile.filename == filename,
            PDFFile.user_email == email
        )
        .first()
    )

    if not pdf:
        raise HTTPException(
            status_code=404,
            detail="PDF not found"
        )

    file_path = f"uploads/{email}/{filename}"

    if os.path.exists(file_path):
        os.remove(file_path)

    db.delete(pdf)
    db.commit()

    return {
        "message": "PDF deleted"
    }
@app.get("/profile/{email}")
def get_profile(
    email: str,
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(
        User.email == email
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return {
        "username": user.username,
        "email": user.email
    }