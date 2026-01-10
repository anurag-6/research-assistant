"""State definition for interview workflow."""
from langgraph.graph import MessagesState
from typing import List, Annotated
import operator
from states.models import Analyst


class InterviewState(MessagesState):
    """State for the interview workflow between analyst and expert."""
    max_num_turns: int
    context: Annotated[List, operator.add]
    analyst: Analyst
    interview: str
    sections: list