from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Message as DBMessage
from app.db.models import Session as DBSession


class MemoryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_recent_history(self, session_id: str, limit: int = 10) -> list[dict]:
        stmt = (
            select(DBMessage)
            .where(DBMessage.session_id == session_id)
            .order_by(DBMessage.created_at.desc())
            .limit(limit)
        )
        recent = (await self.db.scalars(stmt)).all()
        return [{"role": msg.role, "content": msg.content} for msg in reversed(recent)]

    async def ensure_session(self, session_id: str, user_id: str | None = None) -> None:
        existing = await self.db.get(DBSession, session_id)
        if existing is None:
            db_session = DBSession(id=session_id, user_id=user_id)
            self.db.add(db_session)
            await self.db.flush()

    async def add_message(self, session_id: str, role: str, content: str) -> None:
        self.db.add(DBMessage(session_id=session_id, role=role, content=content))
        await self.db.flush()
