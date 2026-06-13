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
        # Note: The advanced DevSecOps prompt will be built in Step 10
        prompt = f"Analyze the following code and return the requested JSON structure.\n\nCode:\n{code_content}"
        
        response = await self.client.aio.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
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
