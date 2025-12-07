# ai/ai_player.py
#This is where I implement the AI logic for a Cluedo player. So basically:
#Choosing movement directions, making suggestions, deciding on accusations,

from __future__ import annotations
import random
from collections import deque
from typing import List, Tuple, Sequence, Optional, Dict
from ai.knowledge import ClueNotebook
from game.cards import SUSPECTS, WEAPONS, ROOMS
from board.rooms import get_room_name

#Same interpretation of directions as in mechanics/movement.py, but I define them here for clarity.
DIRECTION_COMMANDS = ["w", "a", "s", "d"]
DIR_VECTORS = {
    "w": (-1, 0),
    "s": (1, 0),
    "a": (0, -1),
    "d": (0, 1),
}


class AIPlayerController:
    def __init__(self, player, notebook: Optional[ClueNotebook] = None):
        self.player = player
        self.nb = notebook if notebook is not None else ClueNotebook()

        if self.player.hand:
            self.nb.note_own_hand(self.player.hand)
    


    #Check if we can win immediately
    def check_for_winning_accusation(self) -> Optional[Tuple[str, str, str]]:
        """
        Checks the notebook to see if we have a 100% confident solution.
        Returns (suspect, weapon, room) if yes, None otherwise.
        """
        return self.nb.current_singleton_hypothesis()
    




    # Movement choice - With BFS pathfinding
    def _build_door_to_room_map(self, base_board) -> Dict[Tuple[int, int], int]:
        
        #Scan the board for door tiles 'X'.
        rows = len(base_board)
        cols = len(base_board[0])
        door_map: Dict[Tuple[int, int], int] = {}

        for r in range(rows):
            for c in range(cols):
                if base_board[r][c] != "X":
                    continue
                #Check 4-neighborhood for room interior
                room_id: Optional[int] = None
                for dr, dc in DIR_VECTORS.values():
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < rows and 0 <= nc < cols:
                        tile = base_board[nr][nc]
                        if tile in "123456789":
                            room_id = int(tile)
                            break
                if room_id is not None:
                    door_map[(r, c)] = room_id
        return door_map

    def _bfs_distances(self, base_board, start: Tuple[int, int]):
        # BFS over hallway/door tiles ('.' and 'X') starting from 'start'.
        from mechanics.movement import in_bounds

        rows = len(base_board)
        cols = len(base_board[0])

        dist = [[None for _ in range(cols)] for _ in range(rows)]
        prev = [[None for _ in range(cols)] for _ in range(rows)]

        sr, sc = start
        if not in_bounds(base_board, sr, sc):
            return dist, prev

        #At first I didnt allow players to be on same tile, but now I do.
        q = deque()
        q.append((sr, sc))
        dist[sr][sc] = 0

        def can_walk(r: int, c: int) -> bool:
            if not in_bounds(base_board, r, c):
                return False
            tile = base_board[r][c]
            return tile in (".", "X")

        while q:
            r, c = q.popleft()
            for dr, dc in DIR_VECTORS.values():
                nr, nc = r + dr, c + dc
                if not can_walk(nr, nc):
                    continue
                if dist[nr][nc] is not None:
                    continue
                dist[nr][nc] = dist[r][c] + 1
                prev[nr][nc] = (r, c)
                q.append((nr, nc))

        return dist, prev

    def _reconstruct_first_step(
        self,
        start: Tuple[int, int],
        target: Tuple[int, int],
        prev,
    ) -> Optional[str]:
        sr, sc = start
        tr, tc = target

        if prev[tr][tc] is None and (sr, sc) != (tr, tc):
            return None

        #Reconstruct backwards
        path = []
        cur = (tr, tc)
        while cur is not None:
            path.append(cur)
            if cur == (sr, sc):
                break
            cur = prev[cur[0]][cur[1]]

        if not path or path[-1] != (sr, sc):
            return None

        path.reverse()
        if len(path) < 2:
            return None

        next_r, next_c = path[1]
        dr = next_r - sr
        dc = next_c - sc

        for cmd, (vr, vc) in DIR_VECTORS.items():
            if (dr, dc) == (vr, vc):
                return cmd
        return None

    #This is basically the function that decides movement each turn.
    #I divided it into multiple steps for clarity, since it would get super confusing otherwise.
    def choose_move_command(self, base_board, players, steps_remaining: int) -> str:
        #Decide one movement command.
        #I imported is_occupied here to avoid crash ***
        from mechanics.movement import in_bounds, is_occupied
        from mechanics.movement import WALL_TILE

        row, col = self.player.position
        current_tile = base_board[row][col]
        # -------------------------------------------------------------
        # STEP 0: INSIDE A ROOM
        # -------------------------------------------------------------

        if self.player.in_room is not None and current_tile in "123456789%&":
            
            # 0a: If adjacent to a door ('X'), TAKE IT (unless blocked).
            for cmd in DIRECTION_COMMANDS:
                dr, dc = DIR_VECTORS[cmd]
                nr, nc = row + dr, col + dc
                if not in_bounds(base_board, nr, nc): continue
                if base_board[nr][nc] == "X":
                    if not is_occupied(players, nr, nc, self.player):
                        return cmd

            #This part was the wanderin inside room logic before I added BFS.
            door_map = self._build_door_to_room_map(base_board)
            my_room_id = self.player.in_room
            
            
            #Move towards the nearest door of this room
            my_doors = [pos for pos, rid in door_map.items() if rid == my_room_id]
            
            if my_doors:
                best_door = None
                min_dist = float('inf')
                
                for d_r, d_c in my_doors:
                    dist = abs(d_r - row) + abs(d_c - col)
                    if dist < min_dist:
                        min_dist = dist
                        best_door = (d_r, d_c)
                
                #Move towards that door (simple heuristic)
                if best_door:
                    tr, tc = best_door
                    # Determine direction
                    if tr < row: return "w"
                    if tr > row: return "s"
                    if tc < col: return "a"
                    if tc > col: return "d"

            #Inside moves
            tried = set()
            for _ in range(10):
                cmd = random.choice(DIRECTION_COMMANDS)
                if cmd in tried: continue
                tried.add(cmd)
                dr, dc = DIR_VECTORS[cmd]
                nr, nc = row + dr, col + dc
                
                if not in_bounds(base_board, nr, nc): continue
                if base_board[nr][nc] == WALL_TILE: continue
                if is_occupied(players, nr, nc, self.player): continue
                return cmd
            return "done"



        # -------------------------------------------------------------
        # STEP 1: STANDING ON A DOOR ('X')
        # -------------------------------------------------------------
        if current_tile == "X":
            # Priority: Enter the room if we didn't just leave it.
            for cmd in DIRECTION_COMMANDS:
                dr, dc = DIR_VECTORS[cmd]
                nr, nc = row + dr, col + dc
                if not in_bounds(base_board, nr, nc): continue
                
                tile = base_board[nr][nc]
                if tile in "123456789":
                    room_id = int(tile)
                    room_name = get_room_name(room_id)
                    
                    if room_name == self.nb.last_room:
                        continue 
                    
                    #Do not enter if we know it's not the solution
                    if room_name not in self.nb.possible_rooms:
                        continue

                    if not is_occupied(players, nr, nc, self.player):
                        return cmd



        # -------------------------------------------------------------
        # STEP 2-5: BFS PATHFINDING - Main Movement Logic
        # -------------------------------------------------------------
        door_map = self._build_door_to_room_map(base_board)
        dist, prev = self._bfs_distances(base_board, (row, col))

        best_utility = -float('inf')
        best_door = None

        for (dr_row, dr_col), room_id in door_map.items():
            d = dist[dr_row][dr_col]
            if d is None: continue
            if d == 0: continue

            room_name = get_room_name(room_id)
            
            # Heavy penalty if this is the last room we visited. This is basically to mimic human-like
            # behavior of not immediately re-entering a room we just left.
            if room_name == self.nb.last_room:
                pass

            room_score = self.nb.score_room(room_name)
            utility = room_score - (0.5 * d)

            if utility > best_utility:
                best_utility = utility
                best_door = (dr_row, dr_col)

        if best_door is not None:
            cmd = self._reconstruct_first_step((row, col), best_door, prev)
            if cmd is not None:
                dr, dc = DIR_VECTORS[cmd]
                nr, nc = row + dr, col + dc
                if not is_occupied(players, nr, nc, self.player):
                    return cmd


        # -------------------------------------------------------------
        # STEP 6: FALLBACK (Adjacent to Door?)
        # -------------------------------------------------------------
        for cmd in DIRECTION_COMMANDS:
            dr, dc = DIR_VECTORS[cmd]
            nr, nc = row + dr, col + dc
            if not in_bounds(base_board, nr, nc): continue
            if base_board[nr][nc] == "X":
                if not is_occupied(players, nr, nc, self.player):
                    return cmd



        # -------------------------------------------------------------
        # STEP 7: FINAL FALLBACK (Random Valid Move)
        # -------------------------------------------------------------
        tried = set()
        for _ in range(15): # Increased tries
            cmd = random.choice(DIRECTION_COMMANDS)
            if cmd in tried: continue
            tried.add(cmd)

            dr, dc = DIR_VECTORS[cmd]
            nr, nc = row + dr, col + dc
            
            if not in_bounds(base_board, nr, nc): continue
            
            tile = base_board[nr][nc]
            
            if tile == WALL_TILE: continue
            if is_occupied(players, nr, nc, self.player): continue
            
            #This is to avoid room enterance
            if tile in "123456789": continue

            return cmd

        return "done"



    # -------------------------------------------------
    # Room entry notification
    # -------------------------------------------------
    def note_entered_room(self, room_id: int) -> None:
        room_name = get_room_name(room_id)
        self.nb.note_room_visit(room_name)






    # -------------------------------------------------
    # Suggestion choice
    # -------------------------------------------------
    def choose_suggestion(
        self,
        room_name: str,
        all_suspects: Sequence[str] = SUSPECTS,
        all_weapons: Sequence[str] = WEAPONS,
    ) -> Tuple[str, str, str]:
        suspect = self.nb.choose_suspect_candidate()
        if suspect not in all_suspects:
            suspect = random.choice(list(all_suspects))

        weapon = self.nb.choose_weapon_candidate()
        if weapon not in all_weapons:
            weapon = random.choice(list(all_weapons))

        room = room_name
        self.nb.note_room_suggestion(room_name)
        return suspect, weapon, room






    # -------------------------------------------------
    # Secret passage decision
    # -------------------------------------------------
    def decide_use_secret_passage(
        self,
        current_room_name: str,
        dest_room_name: str,
    ) -> bool:
        #At first I just made the AI always use secret passages,
        #but now I added some logic to it.
        
        #Never take a passage to a room we know is innocent.
        if dest_room_name not in self.nb.possible_rooms:
            return False

        if dest_room_name == self.nb.last_room:
            return False

        score_current = self.nb.score_room(current_room_name)
        score_dest = self.nb.score_room(dest_room_name)

        # 1. Is destination better than staying?
        if score_dest <= score_current:
             return False
        max_score = -float('inf')
        for r in ROOMS:
            s = self.nb.score_room(r)
            if s > max_score:
                max_score = s
        if score_dest < (max_score - 15.0):
            return False

        return True



    # -------------------------------------------------
    # Accusation decision
    # -------------------------------------------------
    def decide_accusation_from_suggestion(
        self,
        suggested_triplet: Tuple[str, str, str],
    ) -> bool:
        
        #NO ONE REFUTED the suggestion.
        #The AI will update its knowledge.
        self.nb.process_unrefuted_suggestion(suggested_triplet)

        hypo = self.nb.current_singleton_hypothesis()
        if hypo is None:
            return False

        sus_h, weap_h, room_h = hypo
        sus_s, weap_s, room_s = suggested_triplet

        return sus_h == sus_s and weap_h == weap_s and room_h == room_s




    # -------------------------------------------------
    # Knowledge updates - seen cards
    # -------------------------------------------------
    def note_seen_card(self, card_name: str):
        self.nb.note_seen_card(card_name)

    def debug_print_notebook(self):
        print(self.nb.debug_summary())