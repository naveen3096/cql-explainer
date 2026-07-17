import re


# Patterns ordered from most specific to most general
_RULES = [
    # Population criteria
    (r'\bInitialPopulation\b', "Defines the **Initial Population** — the base set of patients who meet the broadest entry criteria for this measure."),
    (r'\bDenominator\b(?!Exclu|Excep)', "Defines the **Denominator** — patients from the Initial Population who are eligible to be measured."),
    (r'\bDenominatorExclusion\b', "Defines the **Denominator Exclusion** — patients removed from the Denominator before scoring (e.g., hospice, death)."),
    (r'\bDenominatorException\b', "Defines the **Denominator Exception** — patients who may be removed from the Denominator based on clinical reason or patient preference."),
    (r'\bNumerator\b(?!Exclu)', "Defines the **Numerator** — patients in the Denominator who received the desired care or met the quality target."),
    (r'\bNumeratorExclusion\b', "Defines the **Numerator Exclusion** — patients removed from the Numerator under specific conditions."),

    # Temporal operators
    (r'\bduring\b.*\bMeasurementPeriod\b', "Checks whether a clinical event (like an encounter or observation) occurred **during the measurement period**."),
    (r'\bstarts\s+before\b', "Uses a temporal operator to check if one event **starts before** another."),
    (r'\bends\s+after\b', "Uses a temporal operator to check if one event **ends after** another."),
    (r'\boverlaps\b', "Checks whether two time intervals **overlap** — a common pattern for concurrent conditions or encounters."),
    (r'\bduring\b', "Checks whether an event falls **within** a specified time interval."),
    (r'\bMeasurementPeriod\b', "References the **Measurement Period** parameter — the date range over which the measure is evaluated (usually one calendar year)."),

    # Age / demographics
    (r'\bAgeInYearsAt\b', "Calculates the patient's **age in years** at a specific date — used for age-based eligibility criteria."),
    (r'\bAgeInYears\b', "Calculates the patient's **current age in years** — used for age-based eligibility criteria."),
    (r'\bAgeInMonths\b', "Calculates the patient's **age in months** — typically used for pediatric measures."),
    (r'\bGender\b|\bgender\b', "Filters or checks the patient's **gender** — used when a measure applies to a specific sex."),

    # Existence checks
    (r'\bexists\s*\(', "Uses **exists()** to check whether at least one matching clinical record is found — returns true/false."),
    (r'\bnot\s+exists\b', "Uses **not exists** to confirm the **absence** of a clinical event or condition."),
    (r'\bCount\s*\(', "Counts the number of matching records — used when a measure requires a minimum frequency (e.g., 2 visits)."),
    (r'\bLast\s*\(', "Retrieves the **most recent** record from a list — common for latest lab result or most recent encounter."),
    (r'\bFirst\s*\(', "Retrieves the **earliest** record from a list."),

    # Value set / code lookups
    (r'\bValueSet\b|valueset\b', "References a **Value Set** — a named collection of clinical codes (ICD-10, SNOMED, LOINC, etc.) that define a clinical concept."),
    (r'\[Condition:', "Queries **FHIR Condition** resources — represents diagnoses or problems on the patient's problem list."),
    (r'\[Encounter:', "Queries **FHIR Encounter** resources — represents visits, admissions, or clinical interactions."),
    (r'\[Observation:', "Queries **FHIR Observation** resources — represents lab results, vital signs, or clinical findings."),
    (r'\[Procedure:', "Queries **FHIR Procedure** resources — represents procedures or interventions performed."),
    (r'\[MedicationRequest:', "Queries **FHIR MedicationRequest** resources — represents prescribed or ordered medications."),
    (r'\[Patient\b', "Queries the **FHIR Patient** resource — used to access demographics like birthdate or gender."),

    # Status filters
    (r'clinicalStatus.*active|status.*active', "Filters for **active** records only — excludes resolved, inactive, or historical entries."),
    (r'verificationStatus.*confirmed', "Filters for **confirmed** diagnoses — excludes unconfirmed or entered-in-error records."),
    (r'status.*finished|status.*completed', "Filters for **completed** encounters or procedures."),

    # Logic operators
    (r'\band\b.*\band\b', "Combines **multiple conditions** with AND — all conditions must be true for a patient to qualify."),
    (r'\bor\b', "Uses OR logic — the patient qualifies if **any one** of the conditions is true."),
    (r'\bnot\b', "Uses **not** to negate a condition — the patient must NOT meet this criterion."),

    # Includes / libraries
    (r'\bFHIRHelpers\b', "Includes the **FHIRHelpers** library — a standard utility that converts FHIR data types into CQL-compatible types."),
    (r'\binclude\b', "Imports an **external CQL library** — reuses shared logic (e.g., helper functions or common definitions)."),

    # Functions
    (r'\bfunction\b', "Defines a **reusable function** — encapsulates logic that can be called with different inputs."),
    (r'\bparameter\b', "Declares a **parameter** — an input value passed in at runtime, like the Measurement Period dates."),

    # Intervals
    (r'\bInterval\[', "Constructs a **date/time interval** — used to define a time range for temporal comparisons."),
    (r'\bstart of\b', "Extracts the **start date** of a time interval."),
    (r'\bend of\b', "Extracts the **end date** of a time interval."),
]


def _rule_based_explain(source: str) -> str:
    matched = []
    seen = set()
    for pattern, explanation in _RULES:
        if re.search(pattern, source, re.IGNORECASE):
            if explanation not in seen:
                matched.append(explanation)
                seen.add(explanation)

    if not matched:
        return (
            "This define statement contains CQL logic. "
            "It likely retrieves or filters clinical data — review the expression "
            "for FHIR resource types, value set references, and temporal conditions."
        )

    # Limit to the 3 most relevant matches to keep explanations concise
    return " ".join(matched[:3])


def explain_definition(definition: dict, library_context: dict) -> str:
    name = definition.get("name", "")
    source = definition.get("source", "")
    explanation = _rule_based_explain(source)

    # Prepend a name-based hint for population criteria names
    pop_hints = {
        "initialPopulation": "Initial Population",
        "denominator": "Denominator",
        "denominatorexclusion": "Denominator Exclusion",
        "denominatorexception": "Denominator Exception",
        "numerator": "Numerator",
        "numeratorexclusion": "Numerator Exclusion",
    }
    hint = pop_hints.get(name.lower().replace(" ", ""))
    if hint and hint.lower() not in explanation.lower():
        explanation = f"**[{hint}]** {explanation}"

    return explanation


async def explain_all(structure: dict) -> dict:
    for d in structure["definitions"]:
        d["explanation"] = explain_definition(d, structure)
    return structure
