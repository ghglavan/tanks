from enum import IntEnum

class PlayerStatus(IntEnum):
    Connected    = 1
    Disconnected = 2

class Directions(IntEnum):
    UP      = 1
    LEFT    = 2
    DOWN    = 3
    RIGHT   = 0

class MessageType(IntEnum):
    
    #game service messages
    UserID           = 2
    UserFired        = 3
    UserDisconnected = 5
    UserRedirected   = 6
    UserConnectedRed = 8

    #common
    UserConnected    = 1
    UserKilled       = 7
    UsersUpdate      = 4

    #main service messages
    UsersPositions   = 9
    ServerApprove    = 10
    ServerConnect    = 16
    ServerDisconnect = 17
    ConnectTo        = 11
    ServerResetUsers = 12
    RequestPosition  = 13
    RequestUsers     = 14
    ServerKillUser   = 15


class NoHooksRegistered(Exception):
    def __init__(self, message, errors):
        super(NoHooksRegistered, self).__init__(message)

