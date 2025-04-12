from pydantic import BaseModel

class LLMRequest(BaseModel):
    title: str
    description: str
    code: str
