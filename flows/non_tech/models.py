from pydantic import BaseModel, Field
from typing import Dict

class TaskResponse(BaseModel):
    """Schema for task generation response"""
    name: str = Field(..., description="Task name (focused on AI challenge from scenario)")
    question: str = Field(..., description="A comprehensive description of the business scenario, the AI challenge presented, specific requirements for analysis, and what deliverables are expected")
    code_files: Dict[str, str] = Field(..., description="Object containing file paths as keys and their content as values. Include ONLY files that contain data to analyze - NO templates, NO examples, NO explanatory guides")
    outcomes: str = Field(..., description="Expected deliverables after completion (2-3 lines, simple English)")
    pre_requisites: str = Field(..., description="Bullet-point list of required knowledge and tools")
    answer: str = Field(..., description="High-level solution approach covering diagnosis, AI flaws, redesign, metrics, safety considerations, and CPTO recommendations")
    hints: str = Field(..., description="A single guiding hint that nudges toward good diagnostic or analytical practices without revealing the solution")
    definitions: Dict[str, str] = Field(..., description="Dictionary of terminology definitions (AI/ML focused terms relevant to the scenario)")
    
    class Config:
        extra = "forbid"

