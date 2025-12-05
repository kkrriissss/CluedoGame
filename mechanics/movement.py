# mechanics/movement.py

import random
from board.grid import print_board

# tiles
ROOM_TILES = set("123456789")
DOOR_TILE = "X"
WALL_TILE = "#"
SECRET_TILES = {"%", "&"} 

DIRECTIONS = {
    "w": (-1, 0),
    "s": (1, 0),
    "a": (0, -1),
    "d": (0, 1),
    "up": (-1, 0),
    "down": (1, 0),
    "left": (0, -1),
    "right": (0, 1),
}


def roll_dice() -> int:
    #Dice roll between 1 and 6
    return random.randint(1, 6)


def in_bounds(board, r, c) -> bool:
    rows = len(board)
    cols = len(board[0])
    return 0 <= r < rows and 0 <= c < cols


def is_occupied(players, row, col, ignore_player):
    #Checking if a tile is occupied by any player
    for p in players:
        if p is ignore_player:
            continue
        if p.position == (row, col):
            return True
    return False

    
def tile_is_room(tile: str) -> bool:
    return tile in ROOM_TILES or tile in SECRET_TILES


def overlay_players_on_board(base_board, players):
    #Returning a copy of the board with player tokens drawn on top
    board = [row[:] for row in base_board]
    for p in players:
        r, c = p.position
        if 0 <= r < len(board) and 0 <= c < len(board[0]):
            board[r][c] = p.token
    return board


def attempt_step(base_board, players, player, dr, dc):
    #Moving a player one step in the given direction
    r, c = player.position
    new_r = r + dr
    new_c = c + dc

    if not in_bounds(base_board, new_r, new_c):
        print("Cannot move off the board.")
        return False, False

    current_tile = base_board[r][c]
    target_tile = base_board[new_r][new_c]

    #Movement rules
    
    #Wall is always blocked
    if target_tile == WALL_TILE:
        print("You bumped into a wall.")
        return False, False


    if player.in_room is not None and tile_is_room(current_tile):
        #Move inside the same room (to another room/secret tile)
        if tile_is_room(target_tile):
            player.move_to((new_r, new_c))
            return True, False

        #Exit from the X door
        if target_tile == DOOR_TILE:
            player.exit_room()
            player.move_to((new_r, new_c))
            return True, False

        #Room entrance only from door
        print("You must exit the room through a door (X).")
        return False, False

    if target_tile == ".":
        player.move_to((new_r, new_c))
        return True, False

    #I kept logic so that door is a separate tile
    if target_tile == DOOR_TILE:
        player.move_to((new_r, new_c))
        return True, False

    if target_tile in SECRET_TILES:
        print("You can only use a secret passage from inside a room.")
        return False, False

    #Entering a room
    if target_tile in ROOM_TILES:
        if current_tile != DOOR_TILE:
            print("You can only enter a room through a door (X).")
            return False, False

        room_id = int(target_tile)
        player.enter_room(room_id)
        player.move_to((new_r, new_c))
        print(f"{player.name} entered room {room_id}. Movement ends.")
        return True, True

    print("You can't move there.")
    return False, False


def move_player_turn(base_board, players, player):
    #Player Turn
    #Dice rolll + movement + room entry
    dice = roll_dice()
    print(f"\n{player.name} rolled a {dice}.")

    steps_remaining = dice
    entered_room_any = False

    #Ai Player logic
    controller = getattr(player, "ai_controller", None) or getattr(player, "ai", None)
    is_ai = getattr(player, "is_ai", False) and controller is not None

    while steps_remaining > 0:
        board_with_players = overlay_players_on_board(base_board, players)
        print("\n=== CURRENT BOARD (during movement) ===")
        print_board(board_with_players)
        print(
            f"\n{player.name} at {player.position}, "
            f"steps remaining: {steps_remaining}"
        )

        if is_ai:
            cmd = controller.choose_move_command(base_board, players, steps_remaining)
            print(f"AI {player.name} chooses move: {cmd}")
        else:
            print(
                "Enter direction: w(up), s(down), a(left), d(right), "
                "or 'done' to stop movement."
            )
            cmd = input("> ").strip().lower()

        if cmd in ("done", "stop", ""):
            print("Ending movement early.")
            break

        if cmd not in DIRECTIONS:
            print("Invalid direction. Use w/a/s/d or 'done'.")
            continue

        dr, dc = DIRECTIONS[cmd]
        moved, entered_room = attempt_step(base_board, players, player, dr, dc)

        if not moved:
            continue

        steps_remaining -= 1

        if entered_room:
            entered_room_any = True
            break

    print(f"\n{player.name}'s movement turn is over.")
    return entered_room_any