from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import get_db, init_db
from models import User, Equipment, MaintenanceTeam, MaintenanceRequest, ChatHistory, RequestTypeEnum, RequestStatusEnum
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timezone
import logging
import os
from dotenv import load_dotenv
from pathlib import Path
from emergentintegrations.llm.chat import LlmChat, UserMessage

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

app = FastAPI()
api_router = APIRouter(prefix="/api")

# Initialize database
init_db()

# Pydantic models for requests/responses
class UserCreate(BaseModel):
    name: str
    email: str
    role: str = "Technician"
    avatar: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str
    avatar: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class TeamCreate(BaseModel):
    name: str
    specialization: Optional[str] = None
    member_ids: List[str] = []

class TeamResponse(BaseModel):
    id: str
    name: str
    specialization: Optional[str]
    members: List[UserResponse]
    created_at: datetime

    class Config:
        from_attributes = True

class EquipmentCreate(BaseModel):
    name: str
    serial_number: str
    category: str
    department: Optional[str] = None
    assigned_to: Optional[str] = None
    location: str
    purchase_date: Optional[datetime] = None
    warranty_expiry: Optional[datetime] = None
    maintenance_team_id: Optional[str] = None
    image_url: Optional[str] = None

class EquipmentResponse(BaseModel):
    id: str
    name: str
    serial_number: str
    category: str
    department: Optional[str]
    assigned_to: Optional[str]
    location: str
    purchase_date: Optional[datetime]
    warranty_expiry: Optional[datetime]
    maintenance_team_id: Optional[str]
    image_url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class RequestCreate(BaseModel):
    subject: str
    description: Optional[str] = None
    request_type: RequestTypeEnum
    equipment_id: str
    scheduled_date: Optional[datetime] = None
    priority: str = "Medium"

class RequestUpdate(BaseModel):
    subject: Optional[str] = None
    description: Optional[str] = None
    status: Optional[RequestStatusEnum] = None
    assigned_user_id: Optional[str] = None
    duration_hours: Optional[float] = None
    scheduled_date: Optional[datetime] = None
    priority: Optional[str] = None

class RequestResponse(BaseModel):
    id: str
    subject: str
    description: Optional[str]
    request_type: str
    status: str
    equipment_id: str
    maintenance_team_id: Optional[str]
    assigned_user_id: Optional[str]
    scheduled_date: Optional[datetime]
    duration_hours: Optional[float]
    priority: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"

class ChatResponse(BaseModel):
    response: str
    session_id: str

class DashboardStats(BaseModel):
    total_equipment: int
    total_requests: int
    active_requests: int
    teams_count: int
    requests_by_status: dict
    requests_by_type: dict

# Routes
@api_router.get("/")
async def root():
    return {"message": "GearGuard API"}

# User endpoints
@api_router.post("/users", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@api_router.get("/users", response_model=List[UserResponse])
async def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

@api_router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Team endpoints
@api_router.post("/teams", response_model=TeamResponse)
async def create_team(team: TeamCreate, db: Session = Depends(get_db)):
    db_team = MaintenanceTeam(name=team.name, specialization=team.specialization)
    
    if team.member_ids:
        members = db.query(User).filter(User.id.in_(team.member_ids)).all()
        db_team.members = members
    
    db.add(db_team)
    db.commit()
    db.refresh(db_team)
    return db_team

@api_router.get("/teams", response_model=List[TeamResponse])
async def get_teams(db: Session = Depends(get_db)):
    teams = db.query(MaintenanceTeam).all()
    return teams

@api_router.get("/teams/{team_id}", response_model=TeamResponse)
async def get_team(team_id: str, db: Session = Depends(get_db)):
    team = db.query(MaintenanceTeam).filter(MaintenanceTeam.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team

@api_router.put("/teams/{team_id}", response_model=TeamResponse)
async def update_team(team_id: str, team: TeamCreate, db: Session = Depends(get_db)):
    db_team = db.query(MaintenanceTeam).filter(MaintenanceTeam.id == team_id).first()
    if not db_team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    db_team.name = team.name
    db_team.specialization = team.specialization
    
    if team.member_ids:
        members = db.query(User).filter(User.id.in_(team.member_ids)).all()
        db_team.members = members
    
    db.commit()
    db.refresh(db_team)
    return db_team

# Equipment endpoints
@api_router.post("/equipment", response_model=EquipmentResponse)
async def create_equipment(equipment: EquipmentCreate, db: Session = Depends(get_db)):
    db_equipment = Equipment(**equipment.model_dump())
    db.add(db_equipment)
    db.commit()
    db.refresh(db_equipment)
    return db_equipment

@api_router.get("/equipment", response_model=List[EquipmentResponse])
async def get_equipment(db: Session = Depends(get_db)):
    equipment = db.query(Equipment).all()
    return equipment

@api_router.get("/equipment/{equipment_id}", response_model=EquipmentResponse)
async def get_equipment_by_id(equipment_id: str, db: Session = Depends(get_db)):
    equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    return equipment

@api_router.put("/equipment/{equipment_id}", response_model=EquipmentResponse)
async def update_equipment(equipment_id: str, equipment: EquipmentCreate, db: Session = Depends(get_db)):
    db_equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if not db_equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    
    for key, value in equipment.model_dump().items():
        setattr(db_equipment, key, value)
    
    db.commit()
    db.refresh(db_equipment)
    return db_equipment

@api_router.delete("/equipment/{equipment_id}")
async def delete_equipment(equipment_id: str, db: Session = Depends(get_db)):
    db_equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if not db_equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    
    db.delete(db_equipment)
    db.commit()
    return {"message": "Equipment deleted successfully"}

# Maintenance Request endpoints
@api_router.post("/requests", response_model=RequestResponse)
async def create_request(request: RequestCreate, db: Session = Depends(get_db)):
    # Get equipment to auto-fill team
    equipment = db.query(Equipment).filter(Equipment.id == request.equipment_id).first()
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    
    db_request = MaintenanceRequest(
        **request.model_dump(),
        maintenance_team_id=equipment.maintenance_team_id
    )
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    return db_request

@api_router.get("/requests", response_model=List[RequestResponse])
async def get_requests(db: Session = Depends(get_db)):
    requests = db.query(MaintenanceRequest).all()
    return requests

@api_router.get("/requests/{request_id}", response_model=RequestResponse)
async def get_request(request_id: str, db: Session = Depends(get_db)):
    request = db.query(MaintenanceRequest).filter(MaintenanceRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    return request

@api_router.put("/requests/{request_id}", response_model=RequestResponse)
async def update_request(request_id: str, request: RequestUpdate, db: Session = Depends(get_db)):
    db_request = db.query(MaintenanceRequest).filter(MaintenanceRequest.id == request_id).first()
    if not db_request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    for key, value in request.model_dump(exclude_unset=True).items():
        setattr(db_request, key, value)
    
    db_request.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(db_request)
    return db_request

@api_router.delete("/requests/{request_id}")
async def delete_request(request_id: str, db: Session = Depends(get_db)):
    db_request = db.query(MaintenanceRequest).filter(MaintenanceRequest.id == request_id).first()
    if not db_request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    db.delete(db_request)
    db.commit()
    return {"message": "Request deleted successfully"}

@api_router.get("/equipment/{equipment_id}/requests", response_model=List[RequestResponse])
async def get_equipment_requests(equipment_id: str, db: Session = Depends(get_db)):
    requests = db.query(MaintenanceRequest).filter(MaintenanceRequest.equipment_id == equipment_id).all()
    return requests

# Dashboard stats
@api_router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(db: Session = Depends(get_db)):
    total_equipment = db.query(Equipment).count()
    total_requests = db.query(MaintenanceRequest).count()
    active_requests = db.query(MaintenanceRequest).filter(
        MaintenanceRequest.status.in_([RequestStatusEnum.NEW, RequestStatusEnum.IN_PROGRESS])
    ).count()
    teams_count = db.query(MaintenanceTeam).count()
    
    requests_by_status = {}
    for status in RequestStatusEnum:
        count = db.query(MaintenanceRequest).filter(MaintenanceRequest.status == status).count()
        requests_by_status[status.value] = count
    
    requests_by_type = {}
    for req_type in RequestTypeEnum:
        count = db.query(MaintenanceRequest).filter(MaintenanceRequest.request_type == req_type).count()
        requests_by_type[req_type.value] = count
    
    return DashboardStats(
        total_equipment=total_equipment,
        total_requests=total_requests,
        active_requests=active_requests,
        teams_count=teams_count,
        requests_by_status=requests_by_status,
        requests_by_type=requests_by_type
    )

# AI Chatbot endpoint
@api_router.post("/chat", response_model=ChatResponse)
async def chat(chat_request: ChatRequest, db: Session = Depends(get_db)):
    try:
        api_key = os.environ.get('EMERGENT_LLM_KEY')
        
        system_message = """You are a helpful AI assistant for GearGuard, a maintenance tracking system.
        You can help users with:
        1. Answering FAQs about maintenance management
        2. Providing smart suggestions for preventive maintenance schedules
        3. Understanding maintenance requests in natural language
        4. General guidance on using the application
        
        Be helpful, concise, and professional."""
        
        chat = LlmChat(
            api_key=api_key,
            session_id=chat_request.session_id,
            system_message=system_message
        ).with_model("openai", "gpt-4o")
        
        user_message = UserMessage(text=chat_request.message)
        response = await chat.send_message(user_message)
        
        chat_history = ChatHistory(
            session_id=chat_request.session_id,
            user_message=chat_request.message,
            ai_response=response
        )
        db.add(chat_history)
        db.commit()
        
        return ChatResponse(
            response=response,
            session_id=chat_request.session_id
        )
    except Exception as e:
        logging.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
