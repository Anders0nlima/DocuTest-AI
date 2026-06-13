from abc import ABC, abstractmethod
from app.schemas.generation import GenerationResult, TestSuite, SecurityInsight
from google import genai
from google.genai import types
from app.core.config import settings

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
                "info": {
                    "title": "Mocked API Documentation",
                    "version": "1.0.0",
                    "description": "This is a mock generation result."
                },
                "paths": {
                    "/api/example": {
                        "get": {
                            "summary": "Example Route",
                            "responses": {
                                "200": {
                                    "description": "Successful operation"
                                }
                            }
                        }
                    }
                }
            },
            test_suite=TestSuite(
                filename="test_example_routes.py",
                code="def test_example_route(client):\n    response = client.get('/api/example')\n    assert response.status_code == 200"
            ),
            security_insights=[
                SecurityInsight(
                    route="/api/example",
                    issue="Consider adding rate limiting to this public endpoint."
                )
            ]
        )

class RealAIGeneratorProvider(AIGeneratorProvider):
    def __init__(self):
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not configured in environment variables.")
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model_name = "gemini-2.5-flash"

    async def generate(self, code_content: str) -> GenerationResult:
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
        
        response = await self.client.aio.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                response_schema=GenerationResult,
            ),
        )
        return GenerationResult.model_validate_json(response.text)

# Dependency injection factory
def get_llm_provider() -> AIGeneratorProvider:
    # Switch to RealAIGeneratorProvider when ready
    # return RealAIGeneratorProvider()
    return MockAIGeneratorProvider()
