from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session

async def init_db():
    """앱 시작 시 테이블 자동 생성"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        existing_columns = await conn.run_sync(
            lambda sync_conn: {column["name"] for column in inspect(sync_conn).get_columns("scraps")}
        )
        missing_column_types = {
            "post_id": "INTEGER",
            "external_id": "VARCHAR",
            "title": "VARCHAR",
            "subtitle": "VARCHAR",
            "external_url": "VARCHAR",
        }
        for column, column_type in missing_column_types.items():
            if column not in existing_columns:
                await conn.execute(text(f"ALTER TABLE scraps ADD COLUMN {column} {column_type}"))

        chat_message_columns = await conn.run_sync(
            lambda sync_conn: {column["name"] for column in inspect(sync_conn).get_columns("chat_messages")}
        )
        missing_chat_message_column_types = {
            "message_type": "VARCHAR(20) NOT NULL DEFAULT 'text'",
            "file_url": "VARCHAR(500)",
            "file_name": "VARCHAR(255)",
            "file_size": "INTEGER",
            "file_content_type": "VARCHAR(100)",
        }
        for column, column_type in missing_chat_message_column_types.items():
            if column not in chat_message_columns:
                await conn.execute(text(f"ALTER TABLE chat_messages ADD COLUMN {column} {column_type}"))

        user_columns = await conn.run_sync(
            lambda sync_conn: {column["name"] for column in inspect(sync_conn).get_columns("users")}
        )
        missing_user_column_types = {
            "email_verified": "BOOLEAN NOT NULL DEFAULT TRUE",
            "email_verified_at": "TIMESTAMP",
        }
        for column, column_type in missing_user_column_types.items():
            if column not in user_columns:
                await conn.execute(text(f"ALTER TABLE users ADD COLUMN {column} {column_type}"))
