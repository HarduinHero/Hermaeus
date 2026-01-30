from enum import Enum

class GatewayOpcodes(Enum) :
    # From https://discord.com/developers/docs/topics/opcodes-and-status-codes#gateway-gateway-opcodes
    DISPATCH = 0
    HEARTBEAT = 1
    IDENTIFY = 2
    PRESENCE_UPDATE = 3
    VOICE_STATE_UPDATE = 4
    RESUME = 6
    RECONNECT = 7
    REQUEST_GUILD_MEMBERS = 8
    INVALID_SESSION = 9
    HELLO = 10
    HEARTBEAT_ACK = 11
    REQUEST_SOUNDBOARD_SOUNDS = 31
    
class GatewayEventCodes(Enum) :
    # From https://discord.com/developers/docs/topics/opcodes-and-status-codes#gateway-gateway-opcodes
    UNKNOWN_ERROR           = (4000, "We're not sure what went wrong. Try reconnecting?", True)
    UNKNOWN_OPCODE          = (4001, "You sent an invalid Gateway opcode or an invalid payload for an opcode. Don't do that!", True)
    DECODE_ERROR            = (4002, "You sent an invalid payload to Discord. Don't do that!", True)
    NOT_AUTHENTICATED       = (4003, "You sent us a payload prior to identifying, or this session has been invalidated.", True)
    AUTHENTICATION_FAILED   = (4004, "The account token sent with your identify payload is incorrect.", False)
    ALREADY_AUTHENTICATED   = (4005, "You sent more than one identify payload. Don't do that!", True)
    INVALID_SEQ             = (4007, "The sequence sent when resuming the session was invalid. Reconnect and start a new session.", True)
    RATE_LIMITED            = (4008, "Woah nelly! You're sending payloads to us too quickly. Slow it down! You will be disconnected on receiving this.", True)
    SESSION_TIMED_OUT       = (4009, "Your session timed out. Reconnect and start a new one.", True)
    INVALID_SHARD           = (4010, "You sent us an invalid shard when identifying.", False)
    SHARDING_REQUIRED       = (4011, "The session would have handled too many guilds - you are required to shard your connection in order to connect.", False)
    INVALID_API_VERSION     = (4012, "You sent an invalid version for the gateway.", False)
    INVALID_INTENT          = (4013, "You sent an invalid intent for a Gateway Intent. You may have incorrectly calculated the bitwise value.", False)
    DISALLOWED_INTENT       = (4014, "You sent a disallowed intent for a Gateway Intent. You may have tried to specify an intent that you have not enabled or are not approved for.", False)

    def __init__(self, code:int, desc:str, reconnect:bool) :
        self.code = code
        self.desc = desc
        self.reconnect = reconnect
    

    

    


