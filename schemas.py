from pydantic import BaseModel

class QuestionRequest(BaseModel):
    question: str
    email: str
    filename: str
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str
class PDFRequest(BaseModel):
    filename: str
    email: str