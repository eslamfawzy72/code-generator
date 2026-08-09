from functools import lru_cache

from langchain_classic.memory import ConversationBufferWindowMemory


class MemoryService:

    def __init__(self,preference_language:str="python"):
        self.memory = ConversationBufferWindowMemory(
            k=5,
            return_messages=True
        )
        self.preference_language = preference_language

    def add_user_message(self, message: str):
        self.memory.chat_memory.add_user_message(message)

    def add_ai_message(self, message: str):
        self.memory.chat_memory.add_ai_message(message)

    def get_history(self) -> str:
        history = self.memory.load_memory_variables({})["history"]

        formatted = []

        for message in history:
            role = "User" if message.type == "human" else "Assistant"
            formatted.append(f"{role}: {message.content}")

        return "\n".join(formatted)
    def set_language_preference(self, language: str):
        self.language_preference = language

    def get_language_preference(self):
        return self.language_preference
    @lru_cache
    def get_memory_service():
        return MemoryService()