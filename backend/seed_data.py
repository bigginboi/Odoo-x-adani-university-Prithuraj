import asyncio
from database import SessionLocal, init_db
from models import User, Equipment, MaintenanceTeam, MaintenanceRequest, RequestTypeEnum, RequestStatusEnum
from datetime import datetime, timedelta, timezone

def seed_database():
    init_db()
    db = SessionLocal()
    
    try:
        # Create users
        users = [
            User(name="John Smith", email="john@gearguard.com", role="Technician", avatar="https://i.pravatar.cc/150?img=1"),
            User(name="Sarah Johnson", email="sarah@gearguard.com", role="Manager", avatar="https://i.pravatar.cc/150?img=2"),
            User(name="Mike Wilson", email="mike@gearguard.com", role="Technician", avatar="https://i.pravatar.cc/150?img=3"),
            User(name="Emily Davis", email="emily@gearguard.com", role="Technician", avatar="https://i.pravatar.cc/150?img=4"),
        ]
        db.add_all(users)
        db.commit()
        print("✅ Users created")
        
        # Create maintenance teams
        teams = [
            MaintenanceTeam(name="Mechanical Team", specialization="Mechanical Equipment"),
            MaintenanceTeam(name="Electrical Team", specialization="Electrical Systems"),
            MaintenanceTeam(name="IT Support", specialization="Computer Equipment"),
        ]
        db.add_all(teams)
        db.commit()
        
        # Assign users to teams
        teams[0].members = [users[0], users[1]]
        teams[1].members = [users[2]]
        teams[2].members = [users[3]]
        db.commit()
        print("✅ Teams created")
        
        # Create equipment
        equipment_list = [
            Equipment(
                name="CNC Machine #1",
                serial_number="CNC-2024-001",
                category="Production",
                department="Manufacturing",
                location="Factory Floor A",
                maintenance_team_id=teams[0].id,
                image_url="https://images.pexels.com/photos/35383624/pexels-photo-35383624.jpeg"
            ),
            Equipment(
                name="Hydraulic Press",
                serial_number="HP-2024-002",
                category="Production",
                department="Manufacturing",
                location="Factory Floor B",
                maintenance_team_id=teams[0].id,
                image_url="https://images.pexels.com/photos/35383624/pexels-photo-35383624.jpeg"
            ),
            Equipment(
                name="Generator #3",
                serial_number="GEN-2024-003",
                category="Power",
                department="Facilities",
                location="Power Room",
                maintenance_team_id=teams[1].id,
                image_url="https://images.pexels.com/photos/35383624/pexels-photo-35383624.jpeg"
            ),
            Equipment(
                name="Server Rack #1",
                serial_number="SRV-2024-004",
                category="IT",
                department="IT Department",
                location="Data Center",
                assigned_to="Emily Davis",
                maintenance_team_id=teams[2].id,
                image_url="https://images.pexels.com/photos/35383624/pexels-photo-35383624.jpeg"
            ),
            Equipment(
                name="Conveyor Belt System",
                serial_number="CBS-2024-005",
                category="Production",
                department="Manufacturing",
                location="Assembly Line",
                maintenance_team_id=teams[0].id,
                image_url="https://images.pexels.com/photos/35383624/pexels-photo-35383624.jpeg"
            ),
        ]
        db.add_all(equipment_list)
        db.commit()
        print("✅ Equipment created")
        
        # Create maintenance requests
        requests = [
            MaintenanceRequest(
                subject="Oil Leak in CNC Machine",
                description="Machine is leaking hydraulic oil near the base. Needs immediate attention.",
                request_type=RequestTypeEnum.CORRECTIVE,
                status=RequestStatusEnum.NEW,
                equipment_id=equipment_list[0].id,
                maintenance_team_id=teams[0].id,
                priority="High"
            ),
            MaintenanceRequest(
                subject="Routine Maintenance - Hydraulic Press",
                description="Scheduled quarterly maintenance check.",
                request_type=RequestTypeEnum.PREVENTIVE,
                status=RequestStatusEnum.IN_PROGRESS,
                equipment_id=equipment_list[1].id,
                maintenance_team_id=teams[0].id,
                assigned_user_id=users[0].id,
                scheduled_date=datetime.now(timezone.utc) + timedelta(days=7),
                priority="Medium"
            ),
            MaintenanceRequest(
                subject="Generator Battery Replacement",
                description="Backup batteries showing low voltage, need replacement.",
                request_type=RequestTypeEnum.PREVENTIVE,
                status=RequestStatusEnum.NEW,
                equipment_id=equipment_list[2].id,
                maintenance_team_id=teams[1].id,
                scheduled_date=datetime.now(timezone.utc) + timedelta(days=3),
                priority="High"
            ),
            MaintenanceRequest(
                subject="Server Cooling Fan Failure",
                description="Server rack cooling fan #2 has stopped working.",
                request_type=RequestTypeEnum.CORRECTIVE,
                status=RequestStatusEnum.IN_PROGRESS,
                equipment_id=equipment_list[3].id,
                maintenance_team_id=teams[2].id,
                assigned_user_id=users[3].id,
                priority="High"
            ),
            MaintenanceRequest(
                subject="Conveyor Belt Alignment Check",
                description="Monthly preventive check for belt alignment and tension.",
                request_type=RequestTypeEnum.PREVENTIVE,
                status=RequestStatusEnum.REPAIRED,
                equipment_id=equipment_list[4].id,
                maintenance_team_id=teams[0].id,
                assigned_user_id=users[1].id,
                duration_hours=2.5,
                scheduled_date=datetime.now(timezone.utc) - timedelta(days=2),
                priority="Low"
            ),
            MaintenanceRequest(
                subject="Lubrication Service - CNC Machine",
                description="Weekly lubrication and cleaning service.",
                request_type=RequestTypeEnum.PREVENTIVE,
                status=RequestStatusEnum.NEW,
                equipment_id=equipment_list[0].id,
                maintenance_team_id=teams[0].id,
                scheduled_date=datetime.now(timezone.utc) + timedelta(days=14),
                priority="Medium"
            ),
        ]
        db.add_all(requests)
        db.commit()
        print("✅ Maintenance requests created")
        
        print("\n🎉 Sample data seeded successfully!")
        print(f"   - {len(users)} users")
        print(f"   - {len(teams)} teams")
        print(f"   - {len(equipment_list)} equipment items")
        print(f"   - {len(requests)} maintenance requests")
        
    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
