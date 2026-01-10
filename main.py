"""Main entry point for the research assistant application."""
from config import settings
from graphs.analyst.analyst_graph import main_builder_graph
from utils.file_utils import save_graph_image, save_report


def main(topic: str = None, max_analysts: int = None):
    """
    Run the research assistant workflow.
    
    Args:
        topic: Research topic to investigate
        max_analysts: Maximum number of analyst personas to create
    """
    # Save graph visualization if enabled
    if settings.save_graph_images:
        save_graph_image(main_builder_graph)

    # Use provided values or defaults from config
    if topic is None:
        topic = "The benefits of adopting LangGraph as an agent framework"
    if max_analysts is None:
        max_analysts = settings.max_analysts
    
    thread = {"configurable": {"thread_id": "1"}}

    # Run the graph until the first interruption
    for event in main_builder_graph.stream({"topic":topic,
                            "max_analysts":max_analysts}, 
                            thread, 
                            stream_mode="values"):
        
        analysts = event.get('analysts', '')
        if analysts:
            for analyst in analysts:
                print(f"Name: {analyst.name}")
                print(f"Affiliation: {analyst.affiliation}")
                print(f"Role: {analyst.role}")
                print(f"Description: {analyst.description}")
                print("-" * 50)


    # We now update the state as if we are the human_feedback node
    main_builder_graph.update_state(thread, {"human_analyst_feedback": 
                                    "Add in the CEO of gen ai native startup"}, as_node="human_feedback")


    # Check
    for event in main_builder_graph.stream(None, thread, stream_mode="values"):
        analysts = event.get('analysts', '')
        if analysts:
            for analyst in analysts:
                print(f"Name: {analyst.name}")
                print(f"Affiliation: {analyst.affiliation}")
                print(f"Role: {analyst.role}")
                print(f"Description: {analyst.description}")
                print("-" * 50)  

    # Confirm we are happy
    main_builder_graph.update_state(thread, {"human_analyst_feedback": 
                                None}, as_node="human_feedback")

    # Continue
    for event in main_builder_graph.stream(None, thread, stream_mode="updates"):
        print("--Node--")
        node_name = next(iter(event.keys()))
        print(node_name)

    final_state = main_builder_graph.get_state(thread)
    report = final_state.values.get('final_report')

    save_report(report)

    print("Graph execution complete...")



if __name__ == "__main__":
    main()
