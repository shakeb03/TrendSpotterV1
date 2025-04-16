from sqlalchemy import (
    Column, Integer, String, DateTime, 
    Float, ForeignKey, Table, Text,
    JSON, Boolean, create_engine
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(String, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    location = Column(JSON, nullable=True)
    interests = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False)
    last_active = Column(DateTime, nullable=False)
    
    interactions = relationship("Interaction", back_populates="user")

class Content(Base):
    __tablename__ = 'content'
    
    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    image_url = Column(String, nullable=False)
    source_url = Column(String, nullable=True)
    categories = Column(JSON, nullable=True)
    tags = Column(JSON, nullable=True)
    location = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False)
    metadata = Column(JSON, nullable=True)
    
    interactions = relationship("Interaction", back_populates="content")
    toronto_event = relationship("TorontoEvent", back_populates="content", uselist=False)

class Interaction(Base):
    __tablename__ = 'interactions'
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    content_id = Column(String, ForeignKey('content.id'), nullable=False)
    interaction_type = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    session_id = Column(String, nullable=False)
    metadata = Column(JSON, nullable=True)
    
    user = relationship("User", back_populates="interactions")
    content = relationship("Content", back_populates="interactions")

class TorontoEvent(Base):
    __tablename__ = 'toronto_events'
    
    id = Column(String, primary_key=True)
    content_id = Column(String, ForeignKey('content.id'), nullable=False)
    event_name = Column(String, nullable=False)
    venue = Column(String, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    address = Column(JSON, nullable=False)
    price_range = Column(JSON, nullable=True)
    seasonal_relevance = Column(JSON, nullable=True)
    
    content = relationship("Content", back_populates="toronto_event")