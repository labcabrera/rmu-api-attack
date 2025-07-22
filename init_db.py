#!/usr/bin/env python3
"""
Script to initialize MongoDB with sample attack data
"""
import asyncio
import sys
from app.config import settings
from app.services.attack_service import attack_service
from app.models.attack import Attack, AttackInput, AttackRoll, AttackResult, AttackMode

# Sample attack data
SAMPLE_ATTACKS = [
    {
        "id": "atk_001",
        "tacticalGameId": "game_001",
        "status": "executed",
        "input": {
            "sourceId": "source_001",
            "targetId": "target_001",
            "actionPoints": 3,
            "mode": "mainHand"  # Use string value instead of enum
        },
        "roll": {
            "roll": 15
        },
        "results": {
            "labelResult": "8AT",
            "hitPoints": 8,
            "criticals": [
                {
                    "id": "crit_001",
                    "status": "applied"
                }
            ]
        }
    },
    {
        "id": "atk_002",
        "tacticalGameId": "game_002",
        "status": "pending",
        "input": {
            "sourceId": "source_002",
            "targetId": "target_002",
            "actionPoints": 4,
            "mode": "offHand"  # Use string value instead of enum
        },
        "roll": None,
        "results": None
    },
    {
        "id": "atk_003",
        "tacticalGameId": "game_001",
        "status": "executed",
        "input": {
            "sourceId": "source_003",
            "targetId": "target_003",
            "actionPoints": 2,
            "mode": "mainHand"  # Use string value instead of enum
        },
        "roll": {
            "roll": 8
        },
        "results": {
            "labelResult": "3AT",
            "hitPoints": 3,
            "criticals": []
        }
    }
]

async def init_database():
    """Initialize database with sample data"""
    try:
        print("Connecting to MongoDB...")
        await attack_service.connect()
        print(f"Connected to database: {settings.MONGODB_DATABASE}")
        
        print("\nInitializing sample data...")
        
        for attack_data in SAMPLE_ATTACKS:
            try:
                attack = Attack(**attack_data)
                existing_attack = await attack_service.get_attack_by_id(attack.id)
                
                if existing_attack:
                    print(f"  - Attack {attack.id} already exists, skipping...")
                else:
                    await attack_service.create_attack(attack)
                    print(f"  - Created attack {attack.id}")
                    
            except Exception as e:
                print(f"  - Error creating attack {attack_data['id']}: {e}")
        
        print(f"\nDatabase initialization completed!")
        print(f"MongoDB URL: {settings.MONGODB_URL}")
        print(f"Database: {settings.MONGODB_DATABASE}")
        
        # List all attacks
        print("\nExisting attacks:")
        attacks = await attack_service.list_attacks()
        for attack in attacks:
            print(f"  - {attack.id}: {attack.status} (Game: {attack.tacticalGameId})")
            
    except Exception as e:
        print(f"Error initializing database: {e}")
        sys.exit(1)
    finally:
        await attack_service.disconnect()
        print("\nDisconnected from MongoDB")

if __name__ == "__main__":
    asyncio.run(init_database())
