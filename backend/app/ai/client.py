"""LLM client for OpenAI/Anthropic integration."""

import json
from typing import List, Dict, Any
from app.core.config import settings
import openai
from pydantic import BaseModel, Field


class InitiativeProposal(BaseModel):
    """Structured output for initiative proposals from LLM."""

    title: str
    category: str = Field(..., pattern="^(Cost|Efficiency|Structural)$")
    owner: str
    description: str
    data_evidence: List[str]


def generate_initiatives(diagnostics_summary: str, pnl_summary: str, company_context: str = "") -> List[Dict[str, Any]]:
    """Generate initiative proposals using LLM."""
    from app.ai.prompts import INITIATIVE_GENERATION_PROMPT

    prompt = INITIATIVE_GENERATION_PROMPT.format(
        company_context=company_context,
        diagnostics_summary=diagnostics_summary,
        pnl_summary=pnl_summary,
    )

    if settings.llm_provider == "openai":
        return _generate_openai(prompt)
    else:
        raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")


def _generate_openai(prompt: str) -> List[Dict[str, Any]]:
    """Generate using OpenAI API."""
    if not settings.openai_api_key:
        raise ValueError("OpenAI API key not configured")

    client = openai.OpenAI(api_key=settings.openai_api_key)

    # Use structured output with function calling
    # Request JSON array format
    enhanced_prompt = prompt + "\n\nReturn ONLY a valid JSON object with this structure: {\"initiatives\": [array of initiative objects]}"

    response = client.chat.completions.create(
        model=settings.llm_model,
        messages=[
            {
                "role": "system",
                "content": "You are a financial consultant. You must respond with valid JSON only, containing an 'initiatives' array.",
            },
            {"role": "user", "content": enhanced_prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0.7,
    )

    content = response.choices[0].message.content
    try:
        data = json.loads(content)
        # Handle {"initiatives": [...]} format
        if "initiatives" in data:
            initiatives = data["initiatives"]
        elif isinstance(data, list):
            initiatives = data
        else:
            initiatives = [data]

        # Validate and convert to dicts
        result = []
        for init in initiatives:
            try:
                proposal = InitiativeProposal(**init)
                result.append(proposal.dict())
            except Exception as e:
                # Skip invalid initiatives
                continue

        return result
    except json.JSONDecodeError:
        # Fallback: try to extract JSON from markdown code blocks
        import re
        json_match = re.search(r"```json\s*(.*?)\s*```", content, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group(1))
            if "initiatives" in data:
                return data["initiatives"]
            return data if isinstance(data, list) else [data]
        return []

