from pydantic import BaseModel

from dto.intents import Intent

class BaseResponse(BaseModel):
    intent: Intent