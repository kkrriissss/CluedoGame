ROOM_NAMES = {
    1: "Kitchen",
    2: "Ballroom",
    3: "Conservatory",
    4: "Dining Room",
    5: "Billiard Room",
    6: "Library",
    7: "Lounge",
    8: "Hall",
    9: "Study",
}


def get_room_name(room_id: int) -> str:
    """Return the room's display name for a given numeric ID."""
    return ROOM_NAMES.get(room_id, f"Unknown Room {room_id}")


#For the card system it needs to be stable list of room names
ROOM_CARDS = list(ROOM_NAMES.values())


#Rooms that are connected by secret passages
#Kitchen (1) ↔ Study (9)
#Conservatory (3) ↔ Lounge (7)
SECRET_PASSAGES = {
    1: 9,
    9: 1,
    3: 7,
    7: 3,
}


#Where the player token should appear when arriving
#via a secret passage. These coordinates are inside here and these would swap when using the passage.
SECRET_PASSAGE_POSITIONS = {
    1: (2, 7),    # Kitchen '%' 
    9: (22, 25),  # Study '%'
    3: (6, 24),   # Conservatory '&'
    7: (20, 2),   # Lounge '&'
}

