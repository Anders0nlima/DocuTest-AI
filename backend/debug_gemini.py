"""Diagnostic script to see the raw Gemini response."""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google import genai
from google.genai import types
from dotenv import load_dotenv
import json

load_dotenv()

async def main():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY not set in .env")
        return

    client = genai.Client(api_key=api_key)

    code_content = open("../teste/sample_api.py", "r").read()

    system_instruction = (
        "You are an expert DevSecOps Engineer specializing in API architecture and Quality Assurance (QA). "
        "Your task is to analyze the provided backend source code (e.g., FastAPI, Express, Flask) and extract the exact software contracts. "
        "You must output a strict JSON object containing three elements: "
        "1. 'openapi_spec': A fully valid OpenAPI 3.0 specification representing all found routes, HTTP verbs, parameters, and status codes. "
        "2. 'test_suite': Complete, functional automated test scripts (e.g., using pytest or jest) that cover the extracted routes. "
        "3. 'security_insights': A list of potential security flaws or recommendations found in the static logic. "
        "\n\nCRITICAL DEVSECOPS RULE: "
        "For every identified route with mutable methods (POST, PUT, PATCH, DELETE), you MUST generate an additional test case "
        "that simulates a request without tokens or authorization headers. Ensure that the expected behavior in the test asserts "
        "for security error codes (401 Unauthorized or 403 Forbidden)."
    )

    prompt = f"Analyze the following code and return the requested JSON structure.\n\nCode:\n{code_content}"

    print("Calling Gemini API...")
    response = await client.aio.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
        ),
    )

    print("\n=== RAW RESPONSE TEXT ===")
    print(response.text[:3000])
    print("\n=== PARSED JSON KEYS ===")
    try:
        data = json.loads(response.text)
        print(f"Top-level keys: {list(data.keys())}")
        for key, val in data.items():
            if isinstance(val, dict):
                print(f"  {key} -> dict with keys: {list(val.keys())}")
            elif isinstance(val, list):
                print(f"  {key} -> list with {len(val)} items")
                if val:
                    first = val[0]
                    if isinstance(first, dict):
                        print(f"    first item keys: {list(first.keys())}")
            elif isinstance(val, str):
                print(f"  {key} -> string ({len(val)} chars)")
            else:
                print(f"  {key} -> {type(val).__name__}")
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}")

asyncio.run(main())
