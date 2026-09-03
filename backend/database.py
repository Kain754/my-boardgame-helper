from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./rules.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class GameRule(Base):
    __tablename__ = "rules"

    id = Column(Integer, primary_key=True, index=True)
    game_name = Column(String(200), index=True)
    page_number = Column(Integer)
    content = Column(Text)
    image = Column(Text, nullable=True)  # Изменено: теперь Text для base64
    image_url = Column(String(500), nullable=True)


Base.metadata.create_all(bind=engine)