# game/cards.py

#Card definitions and dealing logic for Cluedo.
#Three main lists: SUSPECTS, WEAPONS, ROOMS.

from __future__ import annotations
import random
from typing import Dict, List
from board.rooms import get_room_name
from entities.player import Player


#Card lists
SUSPECTS: List[str] = [
    "Miss Scarlett",
    "Colonel Mustard",
    "Mrs. White",
    "Reverend Green",
    "Mrs. Peacock",
    "Professor Plum",
]

WEAPONS: List[str] = [
    "Candlestick",
    "Dagger",
    "Lead Pipe",
    "Revolver",
    "Rope",
    "Wrench",
]

ROOMS: List[str] = [
    "Kitchen",
    "Ballroom",
    "Conservatory",
    "Dining Room",
    "Billiard Room",
    "Library",
    "Lounge",
    "Hall",
    "Study",
]



#Solution and dealing logic
def make_solution() -> Dict[str, str]:
    #Randomly pick one suspect, one weapon, and one room
    suspect = random.choice(SUSPECTS)
    weapon = random.choice(WEAPONS)
    room = random.choice(ROOMS)
    return {"suspect": suspect, "weapon": weapon, "room": room}


def _build_deck_without_solution(solution: Dict[str, str]) -> List[str]:
    #Deck without the solution cards
    deck: List[str] = []
    deck.extend(SUSPECTS)
    deck.extend(WEAPONS)
    deck.extend(ROOMS)
    
    for key in ("suspect", "weapon", "room"):
        card = solution[key]
        if card in deck:
            deck.remove(card)

    return deck


def deal_cards(players: List[Player], solution: Dict[str, str]) -> None:
    #Deal the remaining cards in round-robin fashion.
    deck = _build_deck_without_solution(solution)
    random.shuffle(deck)

    for p in players:
        p.hand.clear()
    i = 0
    n = len(players)
    for card in deck:
        players[i].hand.append(card)
        i = (i + 1) % n
