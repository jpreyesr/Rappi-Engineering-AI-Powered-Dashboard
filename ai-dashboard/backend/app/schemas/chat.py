from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str = Field(pattern="^(user|assistant)$")
    content: str


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    history: list[ChatMessage] = Field(default_factory=list, max_length=12)


class ToolCallTrace(BaseModel):
    name: str
    arguments: dict


class ChatResponse(BaseModel):
    answer: str
    used_ai: bool
    tool_calls: list[ToolCallTrace] = Field(default_factory=list)
