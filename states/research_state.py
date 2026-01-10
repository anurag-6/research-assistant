"""State definition for the main research workflow."""
from typing import TypedDict, List, Annotated
import operator
from states.models import Analyst


class ResearchGraphState(TypedDict):
    """State for the main research graph that orchestrates the entire workflow."""
    topic: str
    max_analysts: int
    human_analyst_feedback: str
    analysts: List[Analyst]
    sections: Annotated[List, operator.add]
    introduction: str
    content: str
    conclusion: str
    final_report: str