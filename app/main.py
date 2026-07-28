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
    included_cql: list[str] = []


@app.post("/explain")
async def explain(req: ExplainRequest):
    try:
        structure = parse_cql(req.cql)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Could not parse CQL: {e}")

    included_libraries = []
    for included_source in req.included_cql:
        if not included_source.strip():
            continue
        try:
            included_structure = parse_cql(included_source)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Could not parse additional library: {e}")
        included_libraries.append(included_structure)

    if included_libraries:
        known_valuesets = {v["name"] for v in structure["valuesets"]}
        known_codesystems = set(structure["codesystems"])
        for lib in included_libraries:
            for v in lib["valuesets"]:
                if v["name"] not in known_valuesets:
                    structure["valuesets"].append(v)
                    known_valuesets.add(v["name"])
            for c in lib["codesystems"]:
                if c not in known_codesystems:
                    structure["codesystems"].append(c)
                    known_codesystems.add(c)
        structure["included_libraries"] = [lib["library_name"] for lib in included_libraries]

    structure = await explain_all(structure)
    return structure


app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
