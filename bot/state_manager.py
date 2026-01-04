# bot/state_manager.py
# Simple in-memory FSM per chat

_user_states = {}

def set_state(chat_id: int, action: str, data=None):
    _user_states[chat_id] = {
        "action": action,
        "data": data
    }

def get_state(chat_id: int):
    return _user_states.get(chat_id, {
        "action": None,
        "data": None
    })

def clear_state(chat_id: int):
    _user_states.pop(chat_id, None)
