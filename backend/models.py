from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text, Enum, Table
from sqlalchemy.orm import relationship
from database import Base
import uuid
from datetime import datetime, timezone
import enum

class RequestTypeEnum(str, enum.Enum):
    CORRECTIVE = "Corrective"
    PREVENTIVE = "Preventive"

class RequestStatusEnum(str, enum.Enum):
    NEW = "New"
    IN_PROGRESS = "In Progress"
    REPAIRED = "Repaired"
    SCRAP = "Scrap"

team_members = Table(
    'team_members',
    Base.metadata,
    Column('team_id', String, ForeignKey('maintenance_teams.id')),
    Column('user_id', String, ForeignKey('users.id'))
)

class User(Base):
    __tablename__ = 'users'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    role = Column(String, default="Technician")
    avatar = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    teams = relationship('MaintenanceTeam', secondary=team_members, back_populates='members')
    assigned_requests = relationship('MaintenanceRequest', back_populates='assigned_user')

class Equipment(Base):
    __tablename__ = 'equipment'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    serial_number = Column(String, unique=True, nullable=False)
    category = Column(String, nullable=False)
    department = Column(String, nullable=True)
    assigned_to = Column(String, nullable=True)
    location = Column(String, nullable=False)
    purchase_date = Column(DateTime, nullable=True)
    warranty_expiry = Column(DateTime, nullable=True)
    maintenance_team_id = Column(String, ForeignKey('maintenance_teams.id'), nullable=True)
    image_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    maintenance_team = relationship('MaintenanceTeam', back_populates='equipment')
    requests = relationship('MaintenanceRequest', back_populates='equipment')

class MaintenanceTeam(Base):
    __tablename__ = 'maintenance_teams'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False, unique=True)
    specialization = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    members = relationship('User', secondary=team_members, back_populates='teams')
    equipment = relationship('Equipment', back_populates='maintenance_team')
    requests = relationship('MaintenanceRequest', back_populates='maintenance_team')

class MaintenanceRequest(Base):
    __tablename__ = 'maintenance_requests'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    subject = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    request_type = Column(Enum(RequestTypeEnum), nullable=False)
    status = Column(Enum(RequestStatusEnum), default=RequestStatusEnum.NEW)
    equipment_id = Column(String, ForeignKey('equipment.id'), nullable=False)
    maintenance_team_id = Column(String, ForeignKey('maintenance_teams.id'), nullable=True)
    assigned_user_id = Column(String, ForeignKey('users.id'), nullable=True)
    scheduled_date = Column(DateTime, nullable=True)
    duration_hours = Column(Float, nullable=True)
    priority = Column(String, default="Medium")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    equipment = relationship('Equipment', back_populates='requests')
    maintenance_team = relationship('MaintenanceTeam', back_populates='requests')
    assigned_user = relationship('User', back_populates='assigned_requests')

class ChatHistory(Base):
    __tablename__ = 'chat_history'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, nullable=False)
    user_message = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
