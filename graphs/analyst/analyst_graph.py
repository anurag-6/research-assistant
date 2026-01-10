"""Main analyst graph definition that orchestrates the research workflow."""
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver

from states.research_state import ResearchGraphState
from graphs.analyst.analyst_nodes import (
    create_analysts,
    human_feedback,
    write_report,
    write_introduction,
    write_conclusion,
    finalize_report,
    initiate_all_interviews
)
from graphs.interview.interview_graph import interview_graph


main_builder = StateGraph(ResearchGraphState)
main_builder.add_node("create_analysts", create_analysts)
main_builder.add_node("human_feedback", human_feedback)
main_builder.add_node("conduct_interviews", interview_graph)
main_builder.add_node("write_report", write_report)
main_builder.add_node("write_introduction", write_introduction)
main_builder.add_node("write_conclusion", write_conclusion)
main_builder.add_node("finalize_report", finalize_report)


main_builder.add_edge(START, "create_analysts")
main_builder.add_edge("create_analysts", "human_feedback")
main_builder.add_conditional_edges("human_feedback", initiate_all_interviews, ["create_analysts", "conduct_interviews"])
main_builder.add_edge("conduct_interviews", "write_report")
main_builder.add_edge("conduct_interviews", "write_introduction")
main_builder.add_edge("conduct_interviews", "write_conclusion")
main_builder.add_edge(["write_report", "write_introduction", "write_conclusion"], "finalize_report")
main_builder.add_edge("finalize_report", END)


memory = MemorySaver()
main_builder_graph = main_builder.compile(interrupt_before=['human_feedback'], checkpointer=memory)
