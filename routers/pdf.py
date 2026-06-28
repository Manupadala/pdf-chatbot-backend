from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import PDF
from schemas import PDF as PDFSchema

router = APIRouter(
    prefix="/pdfs",
    tags=["pdfs"],
)

@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # TODO: Implement PDF upload
    pass

@router.get("/")
def get_pdfs(db: Session = Depends(get_db)):
    # TODO: Implement get all PDFs
    pass

@router.get("/{pdf_id}", response_model=PDFSchema)
def get_pdf(pdf_id: int, db: Session = Depends(get_db)):
    # TODO: Implement get PDF
    pass

@router.delete("/{pdf_id}")
def delete_pdf(pdf_id: int, db: Session = Depends(get_db)):
    # TODO: Implement delete PDF
    pass
