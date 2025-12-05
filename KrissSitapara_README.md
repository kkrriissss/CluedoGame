# Cluedo (Text + Simple Visual Board)

A simple, terminal-based implementation of *Cluedo* with an optional Matplotlib board visualization.

This is **Part 1** and has the following: 
- Full board layout + legend  
- Player movement with dice  
- Rooms, doors, and secret passages  
- Suggestion + refutation + accusation logic  
- Turn system with 2–6 players (the 6 classic characters)


---

## 1. Requirements to run the folder
- Python 3.9+ (3.10/3.11 should also work)
- `pip` (Python package manager)
- For the visual board: a GUI backend so Matplotlib can open a window  
  - On Ubuntu, for example:  
    ```bash
    sudo apt-get install python3-tk
    ```

Python dependencies are listed in `requirements.txt`:

---

## Virtual Python env Setup:
- 1) Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
- 2) Install dependencies
pip install -r requirements.txt

---

# Running the game:
From the project root with the venv activated:
python main.py


You’ll be asked first:
Show debug info (solution and player cards)? (y/n):

y → prints the secret solution (who / what weapon / which room)
and all players’ card hands. Great for testing and understanding the logic.

n → hides all that, like a real game

---

# Controls & Gameplay Flow
Main Menu
For the current player:
p – Print board (CLI)
    Shows the 28×28 grid with all rooms and player tokens as text.

w – Open visual map
Opens a Matplotlib window:
Colored rooms
Doors marked
Secret passages
Player tokens shown as letters (S, M, W, G, P, L)
Legend on the right with room names and tile meanings

m – Move current player
Starts a movement turn (dice roll + step-by-step movement).

q – Quit
Exits the game.

After each action, the menu reappears and turns rotate through the players.

---

# Rooms & Secret Passages & Legend
Rooms are encoded as digits 1–9 in the board:
1 – Kitchen
2 – Ballroom
3 – Conservatory
4 – Dining Room
5 – Billiard Room
6 – Library
7 – Lounge
8 – Hall
9 – Study

Special tiles:
. – Hallway / corridor
'#' – Wall
X – Door (the only way in/out of a room by normal movement)
% – Secret passage tile (Kitchen ↔ Study)
& – Secret passage tile (Lounge ↔ Conservatory)
Q – Central area (just part of the layout)

Players (letters on top of the board tiles):
S – Miss Scarlett
M – Colonel Mustard
W – Mrs. White
G – Reverend Green
P – Mrs. Peacock
L – Professor Plum

---

# Project Structure:

board/
  grid.py        #28x28 board layout (characters, rooms, doors, walls)
  renderer.py    #Matplotlib visualization of the board
  rooms.py       #Room IDs, names, and secret passage mappings

entities/
  character.py   #Metadata for the 6 Clue characters (name, token, start_pos)
  player.py      #Player class (name, token, hand, position, in_room)
  weapon.py      #Weapon definitions (names)
  tokens.py      #(currently unused / optional)

game/
  setup.py       #Creates the base board, players, deals cards, picks solution
  cards.py       #Card lists + dealing logic
  engine.py      #(currently a placeholder: main loop lives in main.py)
  turn_manager.py#(unused in this part, turn logic is in main.py)

mechanics/
  movement.py    #Dice roll + step-by-step w/a/s/d movement + room logic
  suggestions.py #Suggest / refute / accuse logic

utils/
  helper.py      #(placeholder for future helpers)
  
main.py          #Entry point (menus, turn loop)
README.md
requirements.txt

--- 