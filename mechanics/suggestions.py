# mechanics/suggestions.py
# Suggestion / refutation / accusation logic.
# It does for both human and AI players.


from __future__ import annotations
from typing import List, Dict, Tuple, Sequence, Optional
from game.cards import SUSPECTS, WEAPONS, ROOMS
from board.rooms import get_room_name
from entities.player import Player
import random


#User choice
def _choose_from_list(prompt: str, options: Sequence[str]) -> str:
    while True:
        print(prompt)
        for i, opt in enumerate(options, start=1):
            print(f"{i}. {opt}")
        choice = input("Enter number: ").strip()
        if not choice.isdigit():
            print("Please enter a number.")
            continue
        idx = int(choice) - 1
        if 0 <= idx < len(options):
            return options[idx]
        print("Invalid choice, try again.")


def _players_in_turn_order(start_index: int, players: List[Player]):
    n = len(players)
    for offset in range(1, n):
        yield players[(start_index + offset) % n]



#Main suggestion function
def make_suggestion(current_player: Player,
                    players: List[Player],
                    solution: Dict[str, str]) -> bool:
    if current_player.in_room is None:
        print(f"{current_player.name} is not in a room; cannot make a suggestion.")
        return False

    room_id = current_player.in_room
    room_name = get_room_name(room_id)

    print(f"\n{current_player.name} is in the {room_name} and may make a suggestion.")
    if current_player.is_ai:
        suspect, weapon, room = current_player.ai.choose_suggestion(room_name)
        print(f"AI suggestion: {suspect} with the {weapon} in the {room}.")
    else:
        suspect = _choose_from_list("Choose a suspect:", SUSPECTS)
        weapon = _choose_from_list("Choose a weapon:", WEAPONS)
        room = room_name
        print(f"\nSuggestion: {suspect} with the {weapon} in the {room}.")

    #Moving suspect to the room - Summon Rule
    for p in players:
        if p.name == suspect and p != current_player:
            if p.in_room != room_id:
                p.move_to(current_player.position)
                p.enter_room(room_id)
                p.was_summoned = True
                print(f"❗ {p.name} has been summoned to the {room}!")

    #Resolve refutation
    print("\nResolving suggestion...")
    suggester_index = players.index(current_player)
    suggested_cards = (suspect, weapon, room)

    
    
    
    
    
    #Main refutation loop
    for p in _players_in_turn_order(suggester_index, players):
        matches = [card for card in p.hand if card in suggested_cards]
        if not matches:
            print(f"{p.name} cannot refute.")
            continue

        print(f"{p.name} CAN refute the suggestion.")

        # Refuter shows a card
        if p.is_ai:
            shown_card = matches[0]
            print(f"{p.name} (AI) shows a card to {current_player.name}.")
        else:
            #When human player is refuting, I let them choose which card to show
            shown_card = _choose_from_list(
                f"{p.name}, choose a card to show {current_player.name}:",
                matches,
            )
            print(f"{p.name} shows a card to {current_player.name}.")

        #Updating ai notebook for knowledge
        if current_player.is_ai:
            current_player.ai.note_seen_card(shown_card)
        else:
            print(f"The shown card is: {shown_card}")
        return False

    print("\nNo one could refute the suggestion!")

    #Accusation decision logic
    want_accuse = False
    if current_player.is_ai:
        want_accuse = current_player.ai.decide_accusation_from_suggestion(
            (suspect, weapon, room)
        )
        if want_accuse:
            print(f"AI {current_player.name} decides to MAKE an accusation.")
        else:
            print(f"AI {current_player.name} decides NOT to accuse yet.")
    else:
        print("\nNo one could refute your suggestion.")
        ans = input(
            "Do you want to make an ACCUSATION with the same suspect/weapon/room? (y/n): "
        ).strip().lower()
        want_accuse = ans.startswith("y")

    if not want_accuse:
        return False

    #Resolve accusation. 
    return _resolve_accusation(current_player, suspect, weapon, room, solution)



#Final accusation function. This will end the game of the player if they are wrong
def make_accusation_standalone(current_player: Player, solution: Dict[str, str]) -> bool:
    print(f"\n⚠️  {current_player.name} is making a FORMAL ACCUSATION! ⚠️")
    print("This is a game-ending move. If you are wrong, you are eliminated.")

    if current_player.is_ai:
        #Simple AI fallback if called directly
        hypo = current_player.ai.nb.current_singleton_hypothesis()
        if hypo:
            suspect, weapon, room = hypo
        else:
            #Mainly for human accusation testing
            suspect = random.choice(SUSPECTS)
            weapon = random.choice(WEAPONS)
            room = random.choice(ROOMS)
        print(f"AI Accusation: {suspect}, {weapon}, {room}")
    else:
        suspect = _choose_from_list("Accuse Suspect:", SUSPECTS)
        weapon = _choose_from_list("Accuse Weapon:", WEAPONS)
        room = _choose_from_list("Accuse Room:", ROOMS)
        print(f"\nCONFIRM ACCUSATION: {suspect} with the {weapon} in the {room}")
        confirm = input("Are you sure? (y/n): ").strip().lower()
        if not confirm.startswith('y'):
            print("Accusation cancelled.")
            return False

    return _resolve_accusation(current_player, suspect, weapon, room, solution)


def _resolve_accusation(player: Player, 
                        suspect: str, 
                        weapon: str, 
                        room: str, 
                        solution: Dict[str, str]) -> bool:
    
    print(f"\nChecking envelope... {player.name} accuses: {suspect}, {weapon}, {room}")

    correct = (
        suspect == solution["suspect"]
        and weapon == solution["weapon"]
        and room == solution["room"]
    )

    #Game over if accusation right
    if correct:
        print("\n✅ ACCUSATION IS CORRECT! 🎉")
        print(f"{player.name} has solved the mystery and WINS the game!")
        return True
    
    print("\n❌ ACCUSATION IS WRONG.")
    print(f"{player.name} is ELIMINATED from making further accusations/moves.")
    print("They remain in the game to refute suggestions.")
    
    player.is_eliminated = True
    return False