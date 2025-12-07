from game.setup import setup_game, overlay_players_on_board
from board.renderer import visualize_board
from board.grid import print_board
from mechanics.movement import move_player_turn
from mechanics.suggestions import make_suggestion, make_accusation_standalone
from board.rooms import SECRET_PASSAGES, SECRET_PASSAGE_POSITIONS, get_room_name
import time


#final printing for win
def print_victory_screen(winner_name: str, turn_count: int):
    print("\n" + "★" * 50)
    print("★" + " " * 48 + "★")
    print(f"★   🏆 CONGRATULATIONS! {winner_name.upper()} WINS! 🏆    ★")
    print("★" + " " * 48 + "★")
    print(f"★            Total Turns: {turn_count:<23} ★")
    print("★" + " " * 48 + "★")
    print("★" * 50 + "\n")


#Main game loop
def main():

    #This if for testing but if the player wants to see the solution and cards
    debug_choice = input(
        "Show debug info (solution and player cards)? (y/n): "
    ).strip().lower()
    debug = debug_choice.startswith("y")

    base_board, players, solution = setup_game(debug=debug)

    current_player_index = 0
    turn_count = 1
    autoplay = False

    #Checking if the players are eliminated
    while True:
        active_players = [p for p in players if not p.is_eliminated]
        if not active_players:
            print("\n" + "="*40)
            print("       GAME OVER - ALL PLAYERS ELIMINATED")
            print(f"       Total Turns: {turn_count}")
            print("="*40)
            break

        current_player = players[current_player_index % len(players)]

        #skip the eliminated players
        if current_player.is_eliminated:
            current_player_index = (current_player_index + 1) % len(players)
            continue

        is_ai = getattr(current_player, "is_ai", False)
        ai_ctrl = getattr(current_player, "ai", None)


        #1. Summon rule - connected with suggestion.py
        if getattr(current_player, "was_summoned", False):
            print(f"\n❗ {current_player.name} was summoned to the {get_room_name(current_player.in_room)}!")
            
            stay_choice = False
            current_player.was_summoned = False

            if autoplay and is_ai:
                print(f"[AUTOPLAY] AI {current_player.name} chooses to STAY and suggest.")
                time.sleep(0.05)
                stay_choice = True
            elif is_ai:
                print(f"AI {current_player.name} chooses to STAY and suggest.")
                stay_choice = True
            else:
                ans = input("Do you want to stay and make a suggestion? (y/n): ").strip().lower()
                stay_choice = ans.startswith("y")

            if stay_choice:
                game_over = make_suggestion(current_player, players, solution)
                if game_over:
                    print_victory_screen(current_player.name, turn_count)
                    break
            
                if current_player.is_eliminated:
                    print(f"({current_player.name} lost the turn due to wrong accusation.)")

                current_player_index = (current_player_index + 1) % len(players)
                turn_count += 1
                continue

        #2. If they are not summoned, the next best thing is to check for secret passages
        if current_player.in_room in SECRET_PASSAGES and not current_player.is_eliminated:
            dest_room_id = SECRET_PASSAGES[current_player.in_room]
            dest_room_name = get_room_name(dest_room_id)
            current_room_name = get_room_name(current_player.in_room)

            if is_ai and ai_ctrl is not None and hasattr(ai_ctrl, "decide_use_secret_passage"):
                use_sp = ai_ctrl.decide_use_secret_passage(current_room_name, dest_room_name)
            else:
                ans = input(
                    f"\n{current_player.name} is in the {current_room_name}, which has a secret passage.\n"
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
                    print_victory_screen(current_player.name, turn_count)
                    break
                
                if current_player.is_eliminated:
                     print(f"({current_player.name} lost the turn.)")

                current_player_index = (current_player_index + 1) % len(players)
                turn_count += 1
                continue

        #3. Regular turn, you can move or accuse
        choice = None

        #for the Ai 
        if is_ai:
            winning_hypo = ai_ctrl.check_for_winning_accusation()
            if winning_hypo:
                print(f"\n💡 AI {current_player.name} has deduced the solution! Making accusation...")
                time.sleep(1)
                choice = "x"
            elif autoplay:
                print(f"\n[AUTOPLAY] Turn {turn_count}: AI {current_player.name} is moving...")
                time.sleep(0.05)
                choice = "m"

        if choice is None:
            print("\n=== GAME MENU ===")
            print(f"(Turn {turn_count} | Current turn: {current_player.name} [{current_player.token}])")
            print("p - print board")
            print("w - open visual map")
            print("m - move current player")
            print("x - make accusation (any room)")
            print(f"a - toggle autoplay (currently {'ON' if autoplay else 'OFF'})")
            print("q - quit")
            choice = input("\nEnter choice: ").strip().lower()

        if choice == "a":
            autoplay = not autoplay
            print(f"Autoplay is now {'ON' if autoplay else 'OFF'}.")
            continue

        elif choice == "p":
            board_with_players = overlay_players_on_board(base_board, players)
            print("\n=== CURRENT BOARD (CLI) ===\n")
            print_board(board_with_players)

        elif choice == "w":
            board_with_players = overlay_players_on_board(base_board, players)
            print("\n=== OPENING VISUAL MAP ===")
            visualize_board(board_with_players)

        elif choice == "x":
            game_over = make_accusation_standalone(current_player, solution)
            if game_over:
                print_victory_screen(current_player.name, turn_count)
                break
            
            if current_player.is_eliminated:
                current_player_index = (current_player_index + 1) % len(players)
                turn_count += 1
            continue

        elif choice == "m":
            print(f"\n--- {current_player.name}'s turn ---")
            entered_room = move_player_turn(base_board, players, current_player)

            game_over = False
            if entered_room and current_player.in_room is not None:
                game_over = make_suggestion(current_player, players, solution)

            if game_over:
                print_victory_screen(current_player.name, turn_count)
                break

            current_player_index = (current_player_index + 1) % len(players)
            turn_count += 1

        elif choice == "q":
            print("Quitting game...")
            break

        else:
            print("Invalid choice, try again.")


if __name__ == "__main__":
    main()