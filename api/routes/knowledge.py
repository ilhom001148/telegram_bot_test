from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

from api.dependencies import get_db, get_current_admin
from bot.models import KnowledgeBase

router = APIRouter(prefix="/knowledge", tags=["Knowledge Base"])

class KnowledgeCreate(BaseModel):
    question: str
    answer: str

class KnowledgeResponse(BaseModel):
    id: int
    question: str
    answer: str
    
    class Config:
        orm_mode = True

@router.get("/", response_model=List[KnowledgeResponse])
def get_knowledge_list(db: Session = Depends(get_db)):
    # optionally auth check here if needed: _ = Depends(get_current_user)
    return db.query(KnowledgeBase).order_by(KnowledgeBase.id.desc()).all()

@router.post("/", response_model=KnowledgeResponse)
def create_knowledge(item: KnowledgeCreate, db: Session = Depends(get_db)):
    kb = KnowledgeBase(question=item.question, answer=item.answer)
    db.add(kb)
    db.commit()
    db.refresh(kb)
    return kb

@router.delete("/{kb_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_knowledge(kb_id: int, db: Session = Depends(get_db)):
    kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id).first()
    if not kb:
        raise HTTPException(status_code=404, detail="Knowledge not found")
    
    db.delete(kb)
    db.commit()
    return None
