from typing import List
from datetime import date, timedelta

from sqlalchemy import String, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import extract

from src.database.models import Contact
from src.schemas import ContactBase, ContactUpdate

class ContactRepository:
    def __init__(self, session: AsyncSession):
        self.db = session

    async def get_contacts(self, skip: int, limit: int, query: str | None) -> List[Contact]:
        if query:
            stmt = (
                select(Contact)
                .filter(
                    Contact.first_name.ilike(f"%{query}%")
                    | Contact.last_name.ilike(f"%{query}%")
                    | Contact.email.ilike(f"%{query}%")
                )
                .offset(skip)
                .limit(limit)
            )
        else:
            stmt = select(Contact).offset(skip).limit(limit)
        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()
    
    async def get_upcoming_birthdays(self) -> List[Contact]:
        today = date.today()
        end_date = today + timedelta(days=7)

        query = select(Contact).where(
            func.to_char(Contact.birthday, "MM-DD").between(
                today.strftime("%m-%d"), end_date.strftime("%m-%d")
            )
        )
        contact = await self.db.execute(query)
        return contact.scalars().all()

    async def get_contact_by_id(self, contact_id: int) -> Contact | None:
        stmt = select(Contact).where(Contact.id == contact_id)
        contact = await self.db.execute(stmt)
        return contact.scalar_one_or_none()

    async def create_contact(self, body: ContactBase) -> Contact:
        contact = Contact(**body.model_dump(exclude_unset=True))
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return await self.get_contact_by_id(contact.id)

    async def remove_contact(self, contact_id: int) -> Contact | None:
        contact = await self.get_contact_by_id(contact_id)
        if contact:
            await self.db.delete(contact)
            await self.db.commit()
        return contact

    async def update_contact(
        self, contact_id: int, body: ContactUpdate) -> Contact | None:
        contact = await self.get_contact_by_id(contact_id)
        if contact:
            for key, value in body.dict(exclude_unset=True).items():
                setattr(contact, key, value)

            await self.db.commit()
            await self.db.refresh(contact)

        return contact
