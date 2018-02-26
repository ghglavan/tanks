from enum import IntEnum

class PlayerStatus(IntEnum):
    Connected    = 1
    Disconnected = 2


class MessageType(IntEnum):
    UserConnected    = 1
    UserID           = 2
    UserFired        = 3
    UsersUpdate      = 4
    UserDisconnected = 5
    UserKilled       = 6


