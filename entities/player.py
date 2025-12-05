# entities/player.py


#This is for the player class in Cluedo game.
#Each character has a name, token, starting position, current position, hand of cards, room status, and AI attributes.
class Player:
    def __init__(self, name: str, token: str, start_position: tuple[int, int]):
        self.name = name
        self.token = token
        self.start_position = start_position
        self.position = start_position
        self.hand: list[str] = []
        self.in_room: int | None = None
        self.is_ai: bool = False
        self.ai_controller = None
        self.ai = None

    
    
    
    
    
    #Basic helper methods for player actions.
    def move_to(self, pos: tuple[int, int]) -> None:
        #Move the token to a new (row, col) on the board.
        self.position = pos

    def enter_room(self, room_id: int) -> None:
        #Mark this player as being in the given room.
        self.in_room = room_id

        controller = self.ai_controller or self.ai
        if self.is_ai and controller is not None:
            try:
                controller.note_entered_room(room_id)
            except AttributeError:
                pass

    def exit_room(self) -> None:
        self.in_room = None

    def has_card(self, card: str) -> bool:
        return card in self.hand

    def reset_to_start(self) -> None:
        self.position = self.start_position
        self.in_room = None
