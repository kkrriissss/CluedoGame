#The 6 standard Cluedo characters and their metadata.
#Each character has a name, token, and starting board position.


CHARACTERS = {
    "Miss Scarlett": {
        "token": "S",
        "start_pos": (25, 9)
    },
    "Colonel Mustard": {
        "token": "M",
        "start_pos": (18, 2)
    },
    "Mrs. White": {
        "token": "W",
        "start_pos": (1, 11)
    },
    "Reverend Green": {
        "token": "G",
        "start_pos": (1, 16)
    },
    "Mrs. Peacock": {
        "token": "P",
        "start_pos": (7, 25)
    },
    "Professor Plum": {
        "token": "L",
        "start_pos": (20, 25)
    }
}


#For the card system: each character name is a suspect card
SUSPECT_CARDS = list(CHARACTERS.keys())