"""Analyst node functions for the research assistant workflow."""
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.types import Send

from prompts.analyst_creation_prompt import ANALYST_CREATION_PROMPT
from prompts.write_report_prompt import WRITE_REPORT_PROMPT
from prompts.intro_conclusion_prompts import INTRO_CONCLUSION_PROMPT
from init_llm import llm
from states.models import Perspectives
from states.research_state import ResearchGraphState


def create_analysts(state: ResearchGraphState) -> dict:
    """Create analyst personas based on the research topic."""
    topic = state.get("topic")
    max_analysts = state.get("max_analysts")
    human_analyst_feedback = state.get("human_analyst_feedback", "")

    structured_llm = llm.with_structured_output(Perspectives)

    system_message = ANALYST_CREATION_PROMPT.format(topic=topic,
                                             human_analyst_feedback=human_analyst_feedback,
                                             max_analysts=max_analysts)

    analysts = structured_llm.invoke([SystemMessage(content=system_message)] + [HumanMessage(content="Generate the set of analysts")])
     
    return {"analysts": analysts.analysts}

def human_feedback(state: ResearchGraphState) -> None:
    """No-op node to interrupt execution for human feedback."""
    pass


def write_report(state: ResearchGraphState) -> dict:
    """Write the main report by consolidating all sections."""
    sections = state.get("sections")
    topic = state.get("topic")

    formatted_sec_str = "\n\n".join([f"{section}" for section in sections])

    sys_msg = WRITE_REPORT_PROMPT.format(topic=topic, context=formatted_sec_str)
    report = llm.invoke([SystemMessage(content=sys_msg)] + [HumanMessage(content="Write a report based upon these memos")])

    return {"content": report.content}


def write_introduction(state: ResearchGraphState) -> dict:
    """Write the introduction section of the report."""
    sections = state["sections"]
    topic = state["topic"]

    # Concat all sections together
    formatted_str_sections = "\n\n".join([f"{section}" for section in sections])
    
    # Summarize the sections into a final report
    
    instructions = INTRO_CONCLUSION_PROMPT.format(topic=topic, formatted_str_sections=formatted_str_sections)    
    intro = llm.invoke([instructions]+[HumanMessage(content=f"Write the report introduction")]) 
    return {"introduction": intro.content}

def write_conclusion(state: ResearchGraphState) -> dict:
    """Write the conclusion section of the report."""
    sections = state["sections"]
    topic = state["topic"]

    # Concat all sections together
    formatted_str_sections = "\n\n".join([f"{section}" for section in sections])
    
    # Summarize the sections into a final report
    
    instructions = INTRO_CONCLUSION_PROMPT.format(topic=topic, formatted_str_sections=formatted_str_sections)    
    conclusion = llm.invoke([instructions]+[HumanMessage(content=f"Write the report conclusion")]) 
    return {"conclusion": conclusion.content}

def finalize_report(state: ResearchGraphState) -> dict:
    """Finalize the report by combining all sections with intro and conclusion."""
    content = state["content"]
    if content.startswith("## Insights"):
        content = content.strip("## Insights")
    if "## Sources" in content:
        try:
            content, sources = content.split("\n## Sources\n")
        except:
            sources = None
    else:
        sources = None

    final_report = state["introduction"] + "\n\n---\n\n" + content + "\n\n---\n\n" + state["conclusion"]
    if sources is not None:
        final_report += "\n\n## Sources\n" + sources
    return {"final_report": final_report}

def initiate_all_interviews(state: ResearchGraphState):
    """
    Initiate interviews for all analysts using the Send API for parallel execution.
    
    This is the map step that dispatches interview sub-graphs.
    """
    if state.get("human_analyst_feedback"):
        return "create_analysts"
    else:
        topic = state.get("topic")
        return [
            Send("conduct_interviews",
            {
                "analyst": analyst,
                "topic": topic,
                "messages": [HumanMessage(content=f"So you said you were writing an article on {topic}")]
            }) for analyst in state.get("analysts")
        ]
