# database/models.py
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    domain = Column(String(50), default="general")
    created_at = Column(DateTime, default=datetime.utcnow)

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    session_id = Column(String(100), index=True)
    question = Column(Text)
    answer = Column(Text)
    domain = Column(String(50))
    response_time = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

class DomainKnowledge(Base):
    __tablename__ = "domain_knowledge"
    
    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String(50), index=True)
    question = Column(Text)
    answer = Column(Text)
    keywords = Column(Text)
    confidence = Column(Float, default=1.0)
    usage_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class DatabaseManager:
    def __init__(self, database_url):
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self):
        return self.SessionLocal()
    
    def add_conversation(self, user_id, session_id, question, answer, domain, response_time):
        session = self.get_session()
        try:
            conversation = Conversation(
                user_id=user_id,
                session_id=session_id,
                question=question,
                answer=answer,
                domain=domain,
                response_time=response_time
            )
            session.add(conversation)
            session.commit()
            return conversation.id
        finally:
            session.close()