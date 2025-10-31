from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import os

from app.guard import GuardService
from app.llm import GroqChat


load_dotenv()

app = FastAPI(title="Guarded Chat Service")


class ChatRequest(BaseModel):
    prompt: str


class ChatResponse(BaseModel):
    content: str
    blocked: bool
    reason: str | None = None


_llm = GroqChat()
_guard = GuardService(rail_path=os.path.join("rails", "safety.rail"))


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    input_check = await _guard.check_input(req.prompt)
    if input_check.blocked:
        return ChatResponse(content="", blocked=True, reason=input_check.reason)

    raw = await _llm.complete(req.prompt)
    filtered = await _guard.check_output(prompt=req.prompt, output=raw)

    if filtered.blocked:
        return ChatResponse(content="", blocked=True, reason=filtered.reason)

    return ChatResponse(content=filtered.content, blocked=False)


