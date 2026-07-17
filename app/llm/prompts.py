SYSTEM_PROMPT = """You are explaining Clinical Quality Language (CQL) code to a developer
who knows SQL and general programming but is new to CQL and FHIR-based quality measures.
For the code given, explain in plain English: what clinical concept or data it touches,
what the logic actually does step by step, and any FHIR resource types or value-set idioms
involved. Do not invent value set names, codes, or clinical meaning that isn't shown in the
code or context. Keep it to 2-4 sentences unless the logic genuinely needs more."""


def build_definition_prompt(definition: dict, library_context: dict) -> str:
    valueset_names = [v["name"] for v in library_context.get("valuesets", [])]
    return (
        f"Library: {library_context.get('library_name')}\n"
        f"Available value sets: {valueset_names}\n\n"
        f"Explain this CQL define statement:\n\n```\n{definition['source']}\n```"
    )
