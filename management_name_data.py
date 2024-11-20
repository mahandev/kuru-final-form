import uuid
import random, string

management_name_data = {
    "Business Fiesta": {
        "Business Fiesta": {
            "price": 6_000,
            "event_type": "team",
            "min_participants": 2,
            "max_participants": 5,
            "min_managers": 1,
            "max_managers": 1,
            "date_of_event": "22/01/2025 to 26/01/2025",
            "age_category": "17+",
            "docs_required": "ID Proof",
            "unique_id": ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(16))
        },
    },
    "Mystery Maze": {
        "Mystery Maze": {
            "price": 0,
            "event_type": "team",
            "min_participants": 2,
            "max_participants": 5,
            "min_managers": 0,
            "max_managers": 0,
            "date_of_event": "22/01/2025 to 26/01/2025",
            "age_category": "17+",
            "docs_required": "ID Proof",
            "unique_id": ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(16))
        },
    },
    "Case Conquest": {
        "Case Conquest": {
            "price": 500,
            "event_type": "team",
            "min_participants": 1,
            "max_participants": 3,
            "min_managers": 0,
            "max_managers": 0,
            "date_of_event": "22/01/2025 to 26/01/2025",
            "age_category": "17+",
            "docs_required": "ID Proof",
            "unique_id": ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(16))
        },
    },
    "MUN": {
        "MUN Solo": {
            "price": 2_500,
            "event_type": "single",
            "min_participants": 1,
            "max_participants": 1,
            "min_managers": 0,
            "max_managers": 0,
            "date_of_event": "24/01/2025 to 25/01/2025",
            "age_category": "15+",
            "docs_required": "ID Proof",
            "unique_id": ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(16)),
            "country_preference":True,
            
        },
        "MUN Team": {
            "price": 40_000,
            "event_type": "team",
            "min_participants": 10,
            "max_participants": 15,
            "min_managers": 1,
            "max_managers": 2,
            "date_of_event": "24/01/2025 to 25/01/2025",
            "age_category": "15+",
            "docs_required": "ID Proof",
            "unique_id": ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(16)),
            "country_preference":True,
            
        },
       
    },
}
