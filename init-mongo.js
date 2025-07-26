// MongoDB initialization script for RMU Attack API
// This script creates the necessary database and collections

// Switch to the application database
db = db.getSiblingDB('rmu-attacks');

// Create collections with validation
db.createCollection('attacks', {
    validator: {
        $jsonSchema: {
            bsonType: 'object',
            required: ['actionId', 'sourceId', 'targetId', 'status', 'modifiers'],
            properties: {
                actionId: {
                    bsonType: 'string',
                    description: 'Action ID is required and must be a string'
                },
                sourceId: {
                    bsonType: 'string',
                    description: 'Source ID is required and must be a string'
                },
                targetId: {
                    bsonType: 'string',
                    description: 'Target ID is required and must be a string'
                },
                status: {
                    bsonType: 'string',
                    enum: ['draft', 'ready_to_roll', 'ready_to_critical_roll', 'calculated', 'applied', 'failed'],
                    description: 'Status must be one of the valid enum values'
                },
                modifiers: {
                    bsonType: 'object',
                    required: ['attackType', 'rollModifiers'],
                    properties: {
                        attackType: {
                            bsonType: 'string',
                            enum: ['melee', 'ranged'],
                            description: 'Attack type must be melee or ranged'
                        },
                        rollModifiers: {
                            bsonType: 'object',
                            description: 'Roll modifiers object'
                        }
                    }
                },
                roll: {
                    bsonType: ['object', 'null'],
                    description: 'Roll information, can be null'
                },
                results: {
                    bsonType: ['object', 'null'],
                    description: 'Attack results, can be null'
                }
            }
        }
    }
});

db.createCollection('criticals', {
    validator: {
        $jsonSchema: {
            bsonType: 'object',
            required: ['type', 'roll', 'result', 'status'],
            properties: {
                type: {
                    bsonType: 'string',
                    description: 'Critical type is required'
                },
                roll: {
                    bsonType: 'int',
                    minimum: 1,
                    maximum: 100,
                    description: 'Roll must be between 1 and 100'
                },
                result: {
                    bsonType: 'string',
                    description: 'Result description is required'
                },
                status: {
                    bsonType: 'string',
                    enum: ['pending', 'applied', 'cancelled'],
                    description: 'Status must be one of the valid enum values'
                }
            }
        }
    }
});

// Create indexes for better performance
db.attacks.createIndex({ actionId: 1 });
db.attacks.createIndex({ sourceId: 1 });
db.attacks.createIndex({ targetId: 1 });
db.attacks.createIndex({ status: 1 });
db.attacks.createIndex({ actionId: 1, sourceId: 1, targetId: 1 });

db.criticals.createIndex({ type: 1 });
db.criticals.createIndex({ status: 1 });

// Insert sample data for development/testing
db.attacks.insertMany([
    {
        actionId: 'action_001',
        sourceId: 'character_001',
        targetId: 'enemy_001',
        status: 'draft',
        modifiers: {
            attackType: 'melee',
            rollModifiers: {
                bo: 10,
                boInjuryPenalty: 0,
                boActionsPointsPenalty: 0,
                boPacePenalty: 0,
                boFatiguePenalty: 0,
                bd: 5,
                rangePenalty: 0,
                parry: 0,
                customBonus: 0
            }
        },
        roll: null,
        results: null
    },
    {
        actionId: 'action_002',
        sourceId: 'character_002',
        targetId: 'enemy_002',
        status: 'calculated',
        modifiers: {
            attackType: 'ranged',
            rollModifiers: {
                bo: 15,
                boInjuryPenalty: -2,
                boActionsPointsPenalty: 0,
                boPacePenalty: 0,
                boFatiguePenalty: -1,
                bd: 8,
                rangePenalty: -5,
                parry: 0,
                customBonus: 2
            }
        },
        roll: {
            roll: 85
        },
        results: null
    }
]);

db.criticals.insertMany([
    {
        type: 'A',
        roll: 15,
        result: 'Minor wound to arm',
        status: 'pending'
    },
    {
        type: 'B',
        roll: 45,
        result: 'Moderate wound to chest',
        status: 'applied'
    }
]);

print('MongoDB initialization completed successfully!');
print('Collections created: attacks, criticals');
print('Indexes created for optimal performance');
print('Sample data inserted for development');
