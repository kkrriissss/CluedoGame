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
        self.possible_suspects: Set[str] = set(self.all_suspects)
        self.possible_weapons: Set[str] = set(self.all_weapons)
        self.possible_rooms: Set[str] = set(self.all_rooms)
        self.seen_cards: Set[str] = set()
        self.room_visit_count: Dict[str, int] = {r: 0 for r in self.all_rooms}
        self.room_suggestion_count: Dict[str, int] = {r: 0 for r in self.all_rooms}
        self.last_room: Optional[str] = None




    # Card knowledge tracking
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


    #Room tracking
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



    #Room scoring for movement / secret passages
    def score_room(self, room_name: str) -> float:
        #Checking how good it would be to go to another room.
        
        #When we know it's not the solution,
        #This makes the AI avoid it unless it has absolutely no other choice.
        if room_name not in self.possible_rooms:
            return -100.0

        base = float(len(self.possible_suspects) * len(self.possible_weapons))

        visits = self.room_visit_count.get(room_name, 0)
        suggs = self.room_suggestion_count.get(room_name, 0)

        #This was another main trouble that I faced.
        #I had to tune these penalty values to get good performance.
        visit_penalty = 5.0 * visits
        sugg_penalty = 20.0 * suggs

        score = base - visit_penalty - sugg_penalty

        #This prevents the AI from going back and forth between two rooms.
        if self.last_room == room_name:
            score -= 100.0

        return score



    #Candidate choice for suggestions
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


    #Current best guess 
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



    #Debug
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