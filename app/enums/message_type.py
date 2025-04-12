from enum import Enum


class MessageType(str, Enum):
    FOUND = 'found'
    QUEUE = 'queue'
    STOP = 'stop'
    STOP_QUEUE = 'stop_queue'
