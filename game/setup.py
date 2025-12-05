# game/setup.py

#basic game setup functions to create players, set up AI, make solution, deal cards, etc.

import random
from typing import List, Tuple
from board.grid import get_board
from entities.character import CHARACTERS
from entities.player import Player
from game.cards import (
    SUSPECTS,
    WEAPONS,
    ROOMS,
    make_solution,
    deal_cards,
)

#AI
from ai.knowledge import ClueNotebook
from ai.ai_player import AIPlayerController


def create_players() -> List[Player]:
    #Creating player objects from CHARACTERS
    players: List[Player] = []
    for name, meta in CHARACTERS.items():
        token = meta["token"]
        start_pos = meta["start_pos"]
        p = Player(name=name, token=token, start_position=start_pos)
        players.append(p)
    return players


def attach_ai_players(players: List[Player]) -> None:
    #Asking for each player if they are AI or human
    print("\n=== AI PLAYER SETUP ===")
    for p in players:
        is_ai_choice = None
        while is_ai_choice is None:
            ans = input(f"Set '{p.name}' as AI? (y/n): ").strip().lower()

            if ans.startswith("y"):
                p.is_ai = True
                is_ai_choice = True
            elif ans.startswith("n"):
                p.is_ai = False
                is_ai_choice = False
            else:
                print("Invalid input. Please enter 'y' or 'n'.")

        if p.is_ai:
            nb = ClueNotebook(SUSPECTS, WEAPONS, ROOMS)
            controller = AIPlayerController(p, nb)
            p.ai_controller = controller
            p.ai = controller
            print(f"-> {p.name} is set as AI.")
        else:
            p.ai_controller = None
            p.ai = None
            print(f"-> {p.name} is set as Human.")


def setup_game(debug: bool = False) -> Tuple[list, List[Player], dict]:
    base_board = get_board()
    players = create_players()

    #Random player order
    random.shuffle(players)
    
    solution = make_solution()
    deal_cards(players, solution)

    attach_ai_players(players)

    if debug:
        print("\n=== [DEBUG] MURDER SOLUTION (HIDDEN IN REAL GAME) ===")
        print(f"Suspect: {solution['suspect']}")
        print(f"Weapon : {solution['weapon']}")
        print(f"Room   : {solution['room']}")

        print("\n=== [DEBUG] PLAYER CARDS ===")
        for p in players:
            role = "AI" if p.is_ai else "HUMAN"
            print(f"{p.name} ({p.token}, {role}): {sorted(p.hand)}")

    return base_board, players, solution


def overlay_players_on_board(base_board, players: List[Player]):
    #Returning a copy of the board with player tokens drawn on top
    board = [row[:] for row in base_board]
    for p in players:
        r, c = p.position
        if 0 <= r < len(board) and 0 <= c < len(board[0]):
            board[r][c] = p.token
    return board