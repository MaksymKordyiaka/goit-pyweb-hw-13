from typing import Optional

from sqlalchemy import extract, cast, Date, and_
from sqlalchemy.orm import Session
from db.models import Contact, User
from schemas import ContactCreate
from datetime import date, timedelta


def get_contacts(db: Session, user: User, skip: int = 0, limit: int = 100):
    return db.query(Contact).filter(Contact.user_id == user.id).offset(skip).limit(limit).all()


def get_contact(db: Session, contact_id: int, user: User):
    return db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()


def create_contact(db: Session, contact: ContactCreate, user: User):
    db_contact = Contact(**contact.dict(), user_id=user.id)
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact


def upgrade_contact(db: Session, user: User, contact_id: int, contact: ContactCreate):
    db_contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()
    if db_contact:
        for key, value in contact.dict().items():
            setattr(db_contact, key, value)
        db.commit()
        db.refresh(db_contact)
    return db_contact


def delete_contact(db: Session, user: User, contact_id: int):
    db_contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()
    if db_contact:
        db.delete(db_contact)
        db.commit()
        return db_contact
    else:
        return None


def search_contacts(db: Session, user: User, first_name: Optional[str] = None,
                    second_name: Optional[str] = None, email: Optional[str] = None):
    query = db.query(Contact).filter(Contact.user_id == user.id)
    if first_name:
        query = query.filter(Contact.first_name.ilike(f"%{first_name}%"))
    if second_name:
        query = query.filter(Contact.second_name.ilike(f"%{second_name}%"))
    if email:
        query = query.filter(Contact.email.ilike(f"%{email}%"))
    return query.all()


def get_upcoming_birthdays(db: Session, user: User):
    today = date.today()
    seven_days_later = today + timedelta(days=7)
    contacts_with_upcoming_birthdays = db.query(Contact).filter(
        Contact.user_id == user.id,
        extract('month', cast(Contact.birthdate, Date)) == today.month,
        extract('day', cast(Contact.birthdate, Date)) >= today.day,
        extract('day', cast(Contact.birthdate, Date)) <= seven_days_later.day
    ).all()
    if today.month != seven_days_later.month:
        contacts_with_upcoming_birthdays += db.query(Contact).filter(
            extract('month', cast(Contact.birthdate, Date)) == seven_days_later.month,
            extract('day', cast(Contact.birthdate, Date)) <= seven_days_later.day
        ).all()
    return contacts_with_upcoming_birthdays
