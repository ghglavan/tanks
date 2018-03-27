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
    UsersPositions   = 7
    ServerApprove    = 8
    ConnectTo        = 9
    ServerResetUsers = 10
    RequestPosition  = 11
    RequestUsers     = 12
