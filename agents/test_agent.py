# Test Agent
from autogen.agentchat import AssistantAgent
import streamlit as st

SYSTEM_MESSAGE = """
You are a Senior QA Engineer.

TASK:
- Generate REAL pytest-based unit tests for the provided Python code.

QUALITY REQUIREMENTS:
- Tests must reference real functions/classes
- No placeholder assertions
- Tests must be executable

STRUCTURE REQUIREMENTS:
- Generate AT LEAST 3 test cases
- Cover happy path and failure cases

OUTPUT SCHEMA:
{
  "tests": [
    {
      "path": "string",
      "content_base64": "string"
    }
  ]
}

IMPORTANT:
- Encode test files using BASE64
- Output ONLY valid JSON

CRITICAL OUTPUT RULES:
- Output ONLY valid JSON
- Do NOT include explanations
- Do NOT include markdown
- Do NOT include comments
- Do NOT include text before or after JSON
- Use double quotes for all JSON keys and values
- Do NOT use trailing commas
- Follow the exact schema provided
- If unsure, still output valid JSON

"""
test_agent = AssistantAgent(
    name="test_agent",
    system_message=SYSTEM_MESSAGE,
    llm_config={
        "config_list": [
            {
                "model": st.secrets["MODEL_BASIC"],
                "api_type": "groq",
                "api_key": st.secrets["GROQ_API_KEY"],
            }
        ],
        "temperature": 0.0,
        "max_tokens": 2000,
    },
)

