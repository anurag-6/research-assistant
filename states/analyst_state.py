"""State definition for analyst generation phase."""
from typing import TypedDict, List
from states.models import Analyst


class GenerateAnalystsState(TypedDict):
    """State for the analyst generation workflow."""
    topic: str
    max_analysts: int
    human_analyst_feedback: str
    analysts: List[Analyst]

