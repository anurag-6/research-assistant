"""Interview node functions for the research assistant workflow."""
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, get_buffer_string
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_community.document_loaders import WikipediaLoader

from config import settings
from states.interview_state import InterviewState
from states.models import SearchQuery
from prompts.interview_prompt import INTERVIEW_PROMPT
from prompts.web_query_prompt import WEB_QUERY_PROMPT
from prompts.expert_answer_prompt import EXPERT_ANSWER_PROMPT
from prompts.section_report_prompt import SECTION_REPORT_PROMPT
from init_llm import llm


# NODE 1
def generate_question(state: InterviewState) -> dict:
    analyst = state.get("analyst")
    messages = state.get("messages")


    system_msg = INTERVIEW_PROMPT.format(goals=analyst.persona)
    qn = llm.invoke([SystemMessage(content=system_msg)] + messages)

    return {"messages": [qn]}

# NODE 2.1
def serach_web(state: InterviewState) -> dict:
    structured_llm = llm.with_structured_output(SearchQuery)
    search_query = structured_llm.invoke([SystemMessage(content=WEB_QUERY_PROMPT)]+ state['messages'])

    serach_docs = DuckDuckGoSearchResults(output_format=settings.duckduckgo_output_format)
    res = serach_docs.invoke(search_query.search_query)

    formated_search_res = "\n\n ---- \n\n".join(
        [
            f'<Document href="{doc['link']} /> \n {doc['snippet']}  \n </Document>'
            for doc in res
        ]
    )

    return {"context": [formated_search_res]}

# NODE 2.2
def search_wikipedia(state: InterviewState) -> dict:
    structured_llm = llm.with_structured_output(SearchQuery)
    search_query = structured_llm.invoke([SystemMessage(content=WEB_QUERY_PROMPT)] + state['messages'])

    search_docs = WikipediaLoader(
        query=search_query.search_query,
        load_max_docs=settings.wikipedia_max_docs
    ).load()

    formatted_search_docs = "\n\n ---- \n\n".join(
        [
            f'<Document href="{doc.metadata['source']} page={doc.metadata.get("page", '')}/> \n {doc.page_content}  \n </Document>'
            for doc in search_docs
        ]
    )

    return {"context": [formatted_search_docs]}

# NODE 3
def generate_answer(state: InterviewState) -> dict:
    analyst = state.get("analyst")
    messages = state.get("messages")
    context = state.get("context")

    sys_msg = [SystemMessage(content=EXPERT_ANSWER_PROMPT.format(goals=analyst.persona, context=context))]
    llm_result = llm.invoke(sys_msg + messages)

    llm_result.name = 'expert'

    return {"messages": llm_result}

# NODE 4
def save_interview(state: InterviewState) -> dict:

    messages = state.get("messages")
    interview = get_buffer_string(messages)
    
    return {"interview": interview}

# NODE 5
def write_section(state: InterviewState) -> dict:
    interview = state.get("interview")
    context = state.get("context")
    analyst =  state.get("analyst")

    sys_msg = SECTION_REPORT_PROMPT.format(focus=analyst.description)
    section = llm.invoke([SystemMessage(content=sys_msg)]+ [HumanMessage(content=f"Use this source to write your section: {context}")])

    return {"sections": [section.content]}


# EDGE 1
def route_messages(state: InterviewState, name: str = 'expert') -> str:
    """Route to next node based on interview progress."""
    messages = state['messages']
    max_num_turns = state.get("max_num_turns", settings.max_interview_turns)
    current_turns = len([m for m in messages if m.name == name and  isinstance(m, AIMessage)])

    if current_turns >= max_num_turns:
        return "save_interview"

    last_question = messages[-2]

    if "Thank you so much for your help" in last_question.content:
        return "save_interview"

    return "ask_question"

