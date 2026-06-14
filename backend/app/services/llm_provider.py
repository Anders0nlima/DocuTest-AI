import json
import logging
import time
from abc import ABC, abstractmethod

from google import genai
from google.genai import types

from app.core.config import settings
from app.schemas.generation import GenerationResult, TestSuite, SecurityInsight

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIGeneratorProvider(ABC):
    @abstractmethod
    async def generate(self, code_content: str) -> GenerationResult:
        """Analyze the source code and return structured generation result."""
        pass


class MockAIGeneratorProvider(AIGeneratorProvider):
    async def generate(self, code_content: str) -> GenerationResult:
        """Returns a static, hardcoded result for testing without consuming API tokens."""
        return GenerationResult(
            openapi_spec={
                "openapi": "3.0.0",
                "info": {"title": "Mocked API Documentation", "version": "1.0.0"},
                "paths": {"/api/example": {"get": {"summary": "Example Route", "responses": {"200": {"description": "OK"}}}}}
            },
            test_suite=TestSuite(code="def test_example(client):\n    response = client.get('/api/example')\n    assert response.status_code == 200"),
            security_insights=[SecurityInsight(route="/api/example", issue="Consider adding rate limiting.")]
        )


class RealAIGeneratorProvider(AIGeneratorProvider):
    def __init__(self):
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not configured.")
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model_name = "gemini-2.5-flash"

    async def generate(self, code_content: str) -> GenerationResult:
        system_instruction = (
            "You are an expert DevSecOps Engineer. "
            "Analyze backend source code and return a JSON with EXACTLY these 3 keys:\n"
            "1. \"openapi_spec\": A complete, valid OpenAPI 3.0 specification object (NOT a string).\n"
            "2. \"test_suite\": An object with \"filename\" (string) and \"code\" (string with full pytest code).\n"
            "3. \"security_insights\": A list of objects, each with \"route\" (string) and \"issue\" (string).\n\n"
            "CRITICAL RULE: For every route with POST/PUT/PATCH/DELETE, generate a test asserting 401/403 when no auth headers are sent.\n"
            "Return ONLY the JSON object. No markdown, no explanation."
        )

        prompt = f"Analyze the following code:\n\n{code_content}"

        start_time = time.time()
        logger.info(f"Starting LLM generation using model: {self.model_name}")

        try:
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json",
                    temperature=0.0,
                ),
            )
            raw_text = response.text
            if not raw_text:
                raise Exception("Gemini returned empty response.")
        except Exception as e:
            logger.error(f"LLM API call failed: {type(e).__name__}: {e}")
            raise Exception(f"LLM generation failed: {e}") from e

        elapsed_time = time.time() - start_time

        # --- Observability ---
        usage = getattr(response, 'usage_metadata', None)
        if usage:
            logger.info(
                f"LLM completed in {elapsed_time:.2f}s | "
                f"Tokens: {getattr(usage, 'prompt_token_count', 0)} prompt + "
                f"{getattr(usage, 'candidates_token_count', 0)} completion = "
                f"{getattr(usage, 'total_token_count', 0)} total"
            )
        else:
            logger.info(f"LLM completed in {elapsed_time:.2f}s")

        # --- Parse raw JSON response ---
        logger.info(f"Raw LLM output length: {len(raw_text)} chars")
        logger.info(f"Raw LLM output (first 300 chars): {raw_text[:300]}")

        try:
            data = json.loads(raw_text)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}")
            logger.error(f"Raw: {raw_text[:500]}")
            raise Exception(f"AI returned invalid JSON: {e}") from e

        logger.info(f"Parsed top-level keys: {list(data.keys())}")

        # --- Extract openapi_spec ---
        openapi_spec = data.get("openapi_spec", {})
        if isinstance(openapi_spec, str):
            try:
                openapi_spec = json.loads(openapi_spec)
            except json.JSONDecodeError:
                openapi_spec = {}
        if not isinstance(openapi_spec, dict):
            openapi_spec = {}
        # Ensure required fields for SwaggerUI
        if "openapi" not in openapi_spec:
            openapi_spec["openapi"] = "3.0.0"
        if "info" not in openapi_spec:
            openapi_spec["info"] = {"title": "Generated API", "version": "1.0.0"}
        if "paths" not in openapi_spec:
            openapi_spec["paths"] = {}

        # --- Extract test_suite ---
        ts_raw = data.get("test_suite", {})
        if isinstance(ts_raw, str):
            ts = TestSuite(code=ts_raw)
        elif isinstance(ts_raw, dict):
            ts = TestSuite(
                filename=ts_raw.get("filename", "test_generated.py"),
                code=ts_raw.get("code", ts_raw.get("content", ts_raw.get("script", str(ts_raw)))),
            )
        else:
            ts = TestSuite(code=str(ts_raw))

        # --- Extract security_insights ---
        si_raw = data.get("security_insights", [])
        if isinstance(si_raw, dict):
            si_raw = [si_raw]
        insights = []
        for item in si_raw:
            if isinstance(item, dict):
                insights.append(SecurityInsight(
                    route=item.get("route") or item.get("route_or_area") or item.get("finding") or item.get("endpoint") or "general",
                    issue=item.get("issue") or item.get("issue_description") or item.get("impact") or item.get("recommendation") or item.get("description") or str(item),
                ))

        result = GenerationResult(
            openapi_spec=openapi_spec,
            test_suite=ts,
            security_insights=insights,
        )
        logger.info(f"Successfully built GenerationResult with {len(openapi_spec.get('paths', {}))} paths, {len(insights)} insights")
        return result


# Dependency injection factory
def get_llm_provider() -> AIGeneratorProvider:
    return RealAIGeneratorProvider()
