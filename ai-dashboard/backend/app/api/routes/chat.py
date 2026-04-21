from fastapi import APIRouter, Depends

from app.api.deps import get_chat_service
from app.schemas.chat import ChatRequest, ChatResponse, ChatSuggestionsResponse
from app.services.chat_service import ChatService

router = APIRouter(tags=["chat"])


@router.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest, service: ChatService = Depends(get_chat_service)) -> ChatResponse:
    return service.answer(request)


@router.get("/api/chat/suggestions", response_model=ChatSuggestionsResponse)
def chat_suggestions(service: ChatService = Depends(get_chat_service)) -> ChatSuggestionsResponse:
    return service.suggestions()


@router.post("/chat", response_model=ChatResponse)
def legacy_chat(request: ChatRequest, service: ChatService = Depends(get_chat_service)) -> ChatResponse:
    return service.answer(request)
