import logging
import os

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.db.base import Base

logger = logging.getLogger(__name__)

settings = get_settings()

# ─── Oracle Wallet (optional) ─────────────────────────────────
connect_args: dict = {}
if settings.ORACLE_WALLET_DIR:
    abs_wallet_dir = os.path.abspath(settings.ORACLE_WALLET_DIR)
    connect_args["config_dir"] = abs_wallet_dir
    connect_args["wallet_location"] = abs_wallet_dir
    os.environ["TNS_ADMIN"] = abs_wallet_dir
    if settings.ORACLE_WALLET_PASSWORD:
        connect_args["wallet_password"] = settings.ORACLE_WALLET_PASSWORD

# ─── Engine & Session ─────────────────────────────────────────
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    connect_args=connect_args,
)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# ─── FastAPI Dependency ───────────────────────────────────────
async def get_db():
    """Yield an async DB session per request."""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


# ─── Startup ──────────────────────────────────────────────────
async def init_db() -> None:
    """Create all tables on startup. Fails gracefully if DB is unavailable."""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables verified/created successfully.")
    except Exception as e:
        logger.error(f"Failed to connect to database on startup: {e}")
        logger.warning("Application will start, but database-dependent features will fail.")
