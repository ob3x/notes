from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db import get_db
from models import Note as NoteDB
from schemas import Note, NoteCreate
from auth import get_current_user

router = APIRouter(
    prefix="/notes",
    tags=["notes"]
)

@router.get("")
def get_notes(user : dict = Depends(get_current_user), db : Session = Depends(get_db)):
    notes = db.query(NoteDB).filter(NoteDB.owner_id == user.id).all()

    if not notes:
        raise HTTPException(status_code=404, detail="Error, you dont have any notes")
    
    return notes

@router.post("", response_model=Note)
def add_note(note : NoteCreate, user : dict = Depends(get_current_user), db : Session = Depends(get_db)):
    new_note = NoteDB(title = note.title, content = note.content, owner_id = user.id)

    if not note.title or not note.content:
        raise HTTPException(status_code=400, detail="Title and content cannot be empty")

    db.add(new_note)
    db.commit()
    db.refresh(new_note)

    return new_note

@router.put("/{note_id}")
def edit_note(note : NoteCreate, note_id : int, user : dict = Depends(get_current_user), db : Session = Depends(get_db)):
    note_to_edit = db.query(NoteDB).filter(NoteDB.id == note_id).first()

    if not note_to_edit or note_to_edit.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Error, note not found")
    
    note_to_edit.title = note.title
    note_to_edit.content = note.content

    db.commit()
    db.refresh(note_to_edit)

    return note_to_edit

@router.delete("/{note_id}")
def delete_note(note_id : int, user : dict = Depends(get_current_user), db : Session = Depends(get_db)):
    note_to_delete = db.query(NoteDB).filter(NoteDB.id == note_id).first()

    if not note_to_delete or note_to_delete.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Error, note not found")
    
    db.delete(note_to_delete)
    db.commit()

    return note_to_delete