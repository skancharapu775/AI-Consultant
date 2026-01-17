"""Prompt templates for LLM interactions."""

INITIATIVE_GENERATION_PROMPT = """You are a senior financial consultant analyzing a company's financial performance and cost structure.

Based on the following diagnostics summary and company context, propose 8-12 specific, actionable cost and EBITDA improvement initiatives.

COMPANY CONTEXT:
{company_context}

DIAGNOSTICS SUMMARY:
{diagnostics_summary}

P&L SUMMARY:
{pnl_summary}

Generate initiatives that are:
1. Specific and actionable (not generic)
2. Based on evidence from the diagnostics
3. Organized by category: Cost Reduction, Operational Efficiency, or Structural Change
4. Include a clear description of what the initiative entails
5. Include data evidence points that support the initiative

DO NOT invent specific dollar amounts or percentages. Use qualitative descriptions like:
- "Moderate impact expected"
- "High impact potential"
- "Needs further sizing"

For each initiative, provide:
- title: Short, clear title
- category: One of "Cost", "Efficiency", "Structural"
- owner: Suggested owner (e.g., "CFO", "COO", "CTO", "VP Engineering")
- description: 2-3 sentence description
- data_evidence: List of 2-3 specific metrics or observations that support this initiative

Return your response as a JSON array of initiative objects.
"""


