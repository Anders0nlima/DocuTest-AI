"""
Separate Pydantic schema used ONLY as the Gemini response_schema.
All fields must be simple types (str, list[str], float, etc.)
because Dict[str, Any] cannot be serialized to a valid JSON Schema for Gemini.
"""
from pydantic import BaseModel, Field


class LLMSecurityFinding(BaseModel):
    route_or_area: str = Field(description="The route path or area of concern (e.g., '/pets/{pet_id}' or 'Authentication').")
    issue_description: str = Field(description="A clear explanation of the security issue or recommendation.")


class LLMGenerationOutput(BaseModel):
    """Schema that Gemini uses as response_schema. Only simple types."""
    openapi_spec_json: str = Field(description="The FULL OpenAPI 3.0 specification as a valid JSON string.")
    test_code: str = Field(description="Complete, runnable pytest test code covering all extracted routes.")
    test_filename: str = Field(default="test_generated.py", description="The suggested filename for the test file.")
    security_findings: list[LLMSecurityFinding] = Field(
        description="List of security findings or DevSecOps recommendations.",
        default_factory=list,
    )
