# entities/player.py
# Players setup
# Each player has a name, token, start position, 
# current position, hand, room status, and AI controller status.

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
        self.was_summoned: bool = False
        self.is_eliminated: bool = False

    
    # ------------- basic helpers -------------
    #Move player to a new position
    def move_to(self, pos: tuple[int, int]) -> None:
        self.position = pos

    #Enter room
    def enter_room(self, room_id: int) -> None:
        self.in_room = room_id

        controller = self.ai_controller or self.ai
        if self.is_ai and controller is not None:
            try:
                controller.note_entered_room(room_id)
            except AttributeError:
                pass

    #Exit room
    def exit_room(self) -> None:
        self.in_room = None

    #Check if player has a specific card
    def has_card(self, card: str) -> bool:
        return card in self.hand

    def reset_to_start(self) -> None:
        self.position = self.start_position
        self.in_room = None