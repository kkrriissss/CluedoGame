# ai/knowledge.py
#This is where I have implemented the knowledge representation for the Cluedo AI player.


#So basically I made a notebook class that lets the ai keep track of
# which cards are still possible, which cards it has seen, and how many times it has visited or suggested in each room.


from __future__ import annotations
from typing import Iterable, Optional, Tuple, Dict, Set
from game.cards import SUSPECTS, WEAPONS, ROOMS



class ClueNotebook:
    def __init__(
        self,
        suspects: Iterable[str] = SUSPECTS,
        weapons: Iterable[str] = WEAPONS,
        rooms: Iterable[str] = ROOMS,
    ):
        #All possible cards
        self.all_suspects: Set[str] = set(suspects)
        self.all_weapons: Set[str] = set(weapons)
        self.all_rooms: Set[str] = set(rooms)

        #Current candidates (still possible to be in the solution)
        self.possible_suspects: Set[str] = set(self.all_suspects)
        self.possible_weapons: Set[str] = set(self.all_weapons)
        self.possible_rooms: Set[str] = set(self.all_rooms)

        #Cards seen
        self.seen_cards: Set[str] = set()

        # Room visit / suggestion tracking
        self.room_visit_count: Dict[str, int] = {r: 0 for r in self.all_rooms}
        self.room_suggestion_count: Dict[str, int] = {r: 0 for r in self.all_rooms}
        self.last_room: Optional[str] = None




    # ------------------------------------------------------------------
    # Card knowledge tracking
    # ------------------------------------------------------------------
    def note_own_hand(self, cards: Iterable[str]) -> None:
        #If a card is in our own hand, we note it as seen.
        #Also it cannot be in the solution so we eliminate it from candidates.
        for card in cards:
            self.note_seen_card(card)

    def note_seen_card(self, card_name: str) -> None:
        #This is for when the player sees a card.
        if card_name in self.seen_cards:
            return

        self.seen_cards.add(card_name)
        self._eliminate_card(card_name)

    def _eliminate_card(self, card: str) -> None:
        #Remove 'card' from the candidate sets if present.
        if card in self.possible_suspects:
            self.possible_suspects.discard(card)
        if card in self.possible_weapons:
            self.possible_weapons.discard(card)
        if card in self.possible_rooms:
            self.possible_rooms.discard(card)

    #This is to handle the case where nobody refutes a suggestion
    def process_unrefuted_suggestion(self, triplet: Tuple[str, str, str]) -> None:
        suspect, weapon, room = triplet

        #not seen suspect card = killer
        if suspect not in self.seen_cards:
            self.possible_suspects = {suspect}
        
        #not seen weapon card = murder weapon
        if weapon not in self.seen_cards:
            self.possible_weapons = {weapon}
            
        #not seen room card = crime scene
        if room not in self.seen_cards:
            self.possible_rooms = {room}


    # ------------------------------------------------------------------
    # Room tracking
    # ------------------------------------------------------------------
    def note_room_visit(self, room_name: str) -> None:
        #Record that just entered room
        if room_name in self.room_visit_count:
            self.room_visit_count[room_name] += 1
        else:
            self.room_visit_count[room_name] = 1
        self.last_room = room_name

    def note_room_suggestion(self, room_name: str) -> None:
        #Record that a suggestion was made in that room
        if room_name in self.room_suggestion_count:
            self.room_suggestion_count[room_name] += 1
        else:
            self.room_suggestion_count[room_name] = 1



# ------------------------------------------------------------------
    # Room scoring for movement / secret passages
    # ------------------------------------------------------------------
    def score_room(self, room_name: str) -> float:
        """
        Calculates a score for a room to decide if the AI should move there.
        Higher score = Better target.
        """
        
        # 1. If we know this room is INNOCENT (eliminated), avoid it!
        # We give it a massive negative score so the AI only goes here if blocked elsewhere.
        if room_name not in self.possible_rooms:
            return -100.0

        # 2. STRATEGY UPDATE: "Drilling / Camping"
        # If the room is still in 'possible_rooms', it means it might be the Crime Scene.
        # We give it a HIGH flat score (50.0). 
        # Because we removed the 'last_room' penalty, the AI will now happily
        # turn around and go right back into this room to guess again and again
        # until someone shows a card to prove it innocent.
        return 50.0



    # ------------------------------------------------------------------
    # Candidate choice for suggestions
    # ------------------------------------------------------------------
    def choose_suspect_candidate(self) -> str:
        import random
        if self.possible_suspects:
            return random.choice(list(self.possible_suspects))
        return random.choice(list(self.all_suspects))

    def choose_weapon_candidate(self) -> str:
        import random
        if self.possible_weapons:
            return random.choice(list(self.possible_weapons))
        return random.choice(list(self.all_weapons))



    # ------------------------------------------------------------------
    # Current best guess 
    # ------------------------------------------------------------------
    def current_singleton_hypothesis(self) -> Optional[Tuple[str, str, str]]:
        if (
            len(self.possible_suspects) == 1
            and len(self.possible_weapons) == 1
            and len(self.possible_rooms) == 1
        ):
            sus = next(iter(self.possible_suspects))
            weap = next(iter(self.possible_weapons))
            room = next(iter(self.possible_rooms))
            return sus, weap, room
        return None



    # ------------------------------------------------------------------
    # Debug
    # ------------------------------------------------------------------
    def debug_summary(self) -> str:
        lines = []
        lines.append("=== NOTEBOOK SUMMARY ===")
        lines.append(f"Possible suspects: {sorted(self.possible_suspects)}")
        lines.append(f"Possible weapons : {sorted(self.possible_weapons)}")
        lines.append(f"Possible rooms   : {sorted(self.possible_rooms)}")
        lines.append(f"Seen cards       : {sorted(self.seen_cards)}")
        lines.append("Room visits      :")
        for r in sorted(self.room_visit_count.keys()):
            v = self.room_visit_count[r]
            s = self.room_suggestion_count.get(r, 0)
            lines.append(f"  {r}: visits={v}, suggestions={s}")
        lines.append(f"Last room        : {self.last_room}")
        return "\n".join(lines)