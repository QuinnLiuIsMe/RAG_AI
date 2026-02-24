from fastapi import FastAPI
from pydantic import BaseModel
from app.agents.agent import build_agent
from fastapi.responses import HTMLResponse

app = FastAPI()
agent = build_agent()

class QueryRequest(BaseModel):
    question: str

@app.post("/ask")
async def ask(req: QueryRequest):
    result = agent.invoke({"input": req.question})

    return {
        "answer": result["output"]
    }


@app.get("/", response_class=HTMLResponse)
async def home():
    return "<h1>AI Ops Agent is running!</h1><p>Go to <a href='/docs'>/docs</a> to test API</p>"
