from abc import ABC, abstractmethod
from app.schemas.generation import GenerationResult, TestSuite, SecurityInsight

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

# Dependency injection factory
def get_llm_provider() -> AIGeneratorProvider:
    return MockAIGeneratorProvider()
