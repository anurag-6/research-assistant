"""Shared Pydantic models used across the application."""
from pydantic import BaseModel, Field
from typing import List


class Analyst(BaseModel):
    """Represents an AI analyst persona with specific focus and expertise."""
    affiliation: str = Field(description="Primary affiliation of the analyst")
    name: str = Field(description="Name of the analyst")
    role: str = Field(description="Role of the analyst in the context of the topic")
    description: str = Field(description="Description of the analyst focus, motive, concerns")

    @property
    def persona(self) -> str:
        """Return a formatted persona string for the analyst."""
        return f" Name: {self.name}, Role: {self.role}, Affiliation: {self.affiliation}, Description: {self.description}"


class Perspectives(BaseModel):
    """Collection of analyst personas."""
    analysts: List[Analyst] = Field(description="Comprehensive list of analysts with their role and affiliations")


class SearchQuery(BaseModel):
    """Represents a search query for information retrieval."""
    search_query: str = Field(None, description="Search query for retrieval")

