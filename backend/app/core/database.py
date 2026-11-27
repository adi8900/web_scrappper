import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    user = os.getenv("MYSQL_USER", "user")
    password = os.getenv("MYSQL_PASSWORD", "password")
    database = os.getenv("MYSQL_DATABASE", "scraper")
    host = os.getenv("DB_HOST", "db")
    from urllib.parse import quote_plus
    DATABASE_URL = f"mysql+pymysql://{quote_plus(user)}:{quote_plus(password)}@{host}:3306/{database}"

engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=1800)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
