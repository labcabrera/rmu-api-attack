#!/usr/bin/env python3
"""
Script to initialize MongoDB with sample attack data using hexagonal architecture
"""
import asyncio
import sys
from app.config import settings
from app.infrastructure.dependency_container import container
from app.domain.entities import AttackMode

# Sample attack data
SAMPLE_ATTACKS = [
    {
        "id": "atk_001",
        "tactical_game_id": "game_001",
        "source_id": "source_001",
        "target_id": "target_001",
        "action_points": 3,
        "mode": AttackMode.MAIN_HAND
    },
    {
        "id": "atk_002",
        "tactical_game_id": "game_002", 
        "source_id": "source_002",
        "target_id": "target_002",
        "action_points": 4,
        "mode": AttackMode.OFF_HAND
    },
    {
        "id": "atk_003",
        "tactical_game_id": "game_001",
        "source_id": "source_003", 
        "target_id": "target_003",
        "action_points": 2,
        "mode": AttackMode.MAIN_HAND
    }
]

async def init_database():
    """Initialize database with sample data"""
    try:
        print("Initializing hexagonal architecture dependencies...")
        await container.initialize()
        print(f"Connected to database: {settings.MONGODB_DATABASE}")
        
        print("\nInitializing sample data...")
        
        # Get the create attack use case
        create_use_case = container.get_create_attack_use_case()
        get_use_case = container.get_get_attack_use_case()
        list_use_case = container.get_list_attacks_use_case()
        
        for attack_data in SAMPLE_ATTACKS:
            try:
                # Check if attack already exists
                existing_attack = await get_use_case.execute(attack_data["id"])
                
                if existing_attack:
                    print(f"  - Attack {attack_data['id']} already exists, skipping...")
                else:
                    # Create new attack using use case
                    await create_use_case.execute(
                        attack_id=attack_data["id"],
                        tactical_game_id=attack_data["tactical_game_id"],
                        source_id=attack_data["source_id"],
                        target_id=attack_data["target_id"],
                        action_points=attack_data["action_points"],
                        mode=attack_data["mode"]
                    )
                    print(f"  - Created attack {attack_data['id']}")
                    
            except Exception as e:
                print(f"  - Error creating attack {attack_data['id']}: {e}")
        
        print(f"\nDatabase initialization completed!")
        print(f"MongoDB URL: {settings.MONGODB_URL}")
        print(f"Database: {settings.MONGODB_DATABASE}")
        
        # List all attacks
        print("\nExisting attacks:")
        attacks = await list_use_case.execute()
        for attack in attacks:
            print(f"  - {attack.id}: {attack.status} (Game: {attack.tactical_game_id})")
            
    except Exception as e:
        print(f"Error initializing database: {e}")
        sys.exit(1)
    finally:
        await container.cleanup()
        print("\nDisconnected from MongoDB")

if __name__ == "__main__":
    asyncio.run(init_database())
