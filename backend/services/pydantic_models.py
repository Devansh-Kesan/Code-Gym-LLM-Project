"""Pydantic Models."""

from pydantic import BaseModel


class LLMRequest(BaseModel):
    """LLM request model."""

    title: str
    description: str
    code: str

class RunCodeRequest(BaseModel):
    """Code run model."""

    code: str
    question_id: str
