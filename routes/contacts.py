from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from db.connect_db import get_db
from db.models import User
from repository import contacts
from schemas import Contact, ContactCreate
from services.auth import auth_services

router = APIRouter(prefix='/contacts')


@router.post('/', response_model=Contact, status_code=status.HTTP_201_CREATED)
def create_contact(contact: ContactCreate, db: Session = Depends(get_db),
                   current_user: User = Depends(auth_services.get_current_user)):
    db_contact = contacts.create_contact(db=db, contact=contact, user=current_user)
    return db_contact


@router.get("/birthday_next_7_days", response_model=list[Contact])
def get_contacts_birthday_next_7_days(db: Session = Depends(get_db),
                                      current_user: User = Depends(auth_services.get_current_user)):
    return contacts.get_upcoming_birthdays(db, current_user)


@router.get("/search", response_model=list[Contact])
def search_contacts(first_name: str = None, second_name: str = None, email: str = None,
                    db: Session = Depends(get_db), current_user: User = Depends(auth_services.get_current_user)):
    return contacts.search_contacts(db, current_user, first_name=first_name, second_name=second_name, email=email)


@router.get('/{contact_id}', response_model=Contact)
def read_contact(contact_id: int, db: Session = Depends(get_db),
                 current_user: User = Depends(auth_services.get_current_user)):
    db_contact = contacts.get_contact(db, contact_id, current_user)
    if db_contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Contact not found')
    return db_contact


@router.get('/', response_model=list[Contact])
def read_contacts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
                  current_user: User = Depends(auth_services.get_current_user)):
    db_contacts = contacts.get_contacts(db, current_user, skip=skip, limit=limit)
    if db_contacts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No contacts found')
    return db_contacts


@router.put('/{contact_id}', response_model=Contact)
def update_contact(contact_id: int, contact_update: ContactCreate, db: Session = Depends(get_db),
                   current_user: User = Depends(auth_services.get_current_user)):
    db_contact = contacts.upgrade_contact(db, current_user, contact_id, contact_update)
    if db_contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Contact not found')
    return db_contact


@router.delete('/{contact_id}', response_model=Contact)
def delete_contact(contact_id: int, db: Session = Depends(get_db),
                   current_user: User = Depends(auth_services.get_current_user)):
    db_contact = contacts.delete_contact(db, current_user, contact_id)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact
