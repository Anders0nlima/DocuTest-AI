from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class TestSuite(BaseModel):
    filename: str = Field(default="test_generated.py", description="Name of the generated test file")
    framework: str = Field(default="pytest", description="Test framework used")
    code: str = Field(..., description="The actual test code")

class SecurityInsight(BaseModel):
    route: str = Field(default="general", description="The vulnerable or checked route path")
    issue: str = Field(..., description="Description of the security validation issue")

class GenerationResult(BaseModel):
    openapi_spec: Dict[str, Any] = Field(..., description="The OpenAPI 3.0 specification object")
    test_suite: TestSuite = Field(..., description="The generated test suite file")
    security_insights: List[SecurityInsight] = Field(default_factory=list, description="List of DevSecOps insights")
