from collections import defaultdict


class ConversationMemory:
    def __init__(self, max_messages: int = 10):
        self.sessions = defaultdict(list)
        self.max_messages = max_messages

    def get_history(self, session_id: str):
        return self.sessions[session_id]

    def add_message(self, session_id: str, role: str, content: str):
        self.sessions[session_id].append(
            {
                "role": role,
                "content": content,
            }
        )
        self._trim(session_id)

    def clear(self, session_id: str):
        self.sessions.pop(session_id, None)

    def _trim(self, session_id: str):
        if len(self.sessions[session_id]) > self.max_messages:
            self.sessions[session_id] = self.sessions[session_id][-self.max_messages:]


memory = ConversationMemory()