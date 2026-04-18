import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "mysql+pymysql://user:password@db:3306/scraper"

# 🔥 retry connect
for i in range(10):
    try:
        engine = create_engine(DATABASE_URL)
        conn = engine.connect()
        conn.close()
        print("DB connected!")
        break
    except Exception as e:
        print("Waiting for DB...", e)
        time.sleep(3)

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()
