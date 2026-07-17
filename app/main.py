from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.parser.extract import parse_cql
from app.llm.explainer import explain_all

app = FastAPI(title="CQL Explainer")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class ExplainRequest(BaseModel):
    cql: str


@app.post("/explain")
async def explain(req: ExplainRequest):
    try:
        structure = parse_cql(req.cql)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Could not parse CQL: {e}")

    structure = await explain_all(structure)
    return structure


app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
