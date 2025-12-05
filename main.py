from game.setup import setup_game, overlay_players_on_board
from board.renderer import visualize_board
from board.grid import print_board
from mechanics.movement import move_player_turn
from mechanics.suggestions import make_suggestion
from board.rooms import SECRET_PASSAGES, SECRET_PASSAGE_POSITIONS, get_room_name


def main():
    #If the person wants to see the debug info
    debug_choice = input(
        "Show debug info (solution and player cards)? (y/n): "
    ).strip().lower()
    debug = debug_choice.startswith("y")

    base_board, players, solution = setup_game(debug=debug)

    current_player_index = 0

    while True:
        if not players:
            print("No players left. Ending game.")
            break

        current_player = players[current_player_index % len(players)]

        #Secret passage option at the START of the turn
        if current_player.in_room in SECRET_PASSAGES:
            dest_room_id = SECRET_PASSAGES[current_player.in_room]
            dest_room_name = get_room_name(dest_room_id)
            current_room_name = get_room_name(current_player.in_room)

            #Checking Ai or human
            is_ai = getattr(current_player, "is_ai", False)
            ai_ctrl = getattr(current_player, "ai", None)

            #Choosing to use secret passage
            #If AI, call AI method
            if is_ai and ai_ctrl is not None and hasattr(ai_ctrl, "decide_use_secret_passage"):
                use_sp = ai_ctrl.decide_use_secret_passage(
                    current_room_name,
                    dest_room_name,
                )
            else:
                #For human players
                ans = input(
                    f"\n{current_player.name} is in the {current_room_name}, "
                    f"which has a secret passage.\n"
                    f"Use secret passage to the {dest_room_name}? (y/n): "
                ).strip().lower()
                use_sp = ans.startswith("y")

            if use_sp:
                target_pos = SECRET_PASSAGE_POSITIONS[dest_room_id]
                current_player.move_to(target_pos)
                current_player.enter_room(dest_room_id)

                print(f"{current_player.name} uses the secret passage to the {dest_room_name}!")

                game_over = make_suggestion(current_player, players, solution)
                if game_over:
                    print("\n=== GAME OVER ===")
                    return

                #End of turn
                current_player_index = (current_player_index + 1) % len(players)
                continue

        #Regular turn menu
        print("\n=== GAME MENU ===")
        print(f"(Current turn: {current_player.name} [{current_player.token}])")
        print("p - print board")
        print("w - open visual map")
        print("m - move current player")
        print("q - quit")

        choice = input("\nEnter choice: ").strip().lower()

        if choice == "p":
            board_with_players = overlay_players_on_board(base_board, players)
            print("\n=== CURRENT BOARD (CLI) ===\n")
            print_board(board_with_players)

        elif choice == "w":
            board_with_players = overlay_players_on_board(base_board, players)
            print("\n=== OPENING VISUAL MAP ===")
            visualize_board(board_with_players)

        elif choice == "m":
            print(f"\n--- {current_player.name}'s turn ---")
            entered_room = move_player_turn(base_board, players, current_player)

            game_over = False
            if entered_room and current_player.in_room is not None:
                game_over = make_suggestion(current_player, players, solution)

            if game_over:
                print("\n=== GAME OVER ===")
                break

            current_player_index = (current_player_index + 1) % len(players)

        elif choice == "q":
            print("Quitting game...")
            break

        else:
            print("Invalid choice, try again.")


if __name__ == "__main__":
    main()
