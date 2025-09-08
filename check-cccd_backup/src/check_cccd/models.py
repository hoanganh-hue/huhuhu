from sqlalchemy import Column, String, DateTime, Text, Integer, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

Base = declarative_base()


class CheckRequest(Base):
    __tablename__ = "check_requests"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cccd = Column(String(20), nullable=False, index=True)
    status = Column(String(20), nullable=False, default="queued")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    error_message = Column(Text, nullable=True)
    
    # Relationships
    matches = relationship("CheckMatch", back_populates="request", cascade="all, delete-orphan")


class CheckMatch(Base):
    __tablename__ = "check_matches"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    request_id = Column(UUID(as_uuid=True), ForeignKey("check_requests.id"), nullable=False)
    
    type = Column(String(20), nullable=False)  # person, company, person_or_company
    name = Column(String(255), nullable=True)
    tax_code = Column(String(20), nullable=True, index=True)
    url = Column(String(500), nullable=True)
    address = Column(Text, nullable=True)
    role = Column(String(100), nullable=True)
    raw_snippet = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    request = relationship("CheckRequest", back_populates="matches")


class ApiKey(Base):
    __tablename__ = "api_keys"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key_hash = Column(String(255), nullable=False, unique=True, index=True)
    name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    rate_limit_per_minute = Column(Integer, default=60)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used_at = Column(DateTime, nullable=True)