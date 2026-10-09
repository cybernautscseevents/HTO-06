from typing import Optional

from pydantic import BaseModel, Field


class CitizenProfile(BaseModel):
    name: str = ""
    age: Optional[int] = None
    income: Optional[float] = None
    occupation: str = ""
    state: str = ""
    district: str = ""
    category: str = ""
    problem: str = ""
    additional_details: dict = Field(default_factory=dict)