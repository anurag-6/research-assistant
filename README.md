# Research Assistant 🔬

A sophisticated AI-powered research assistant built with LangGraph that automatically generates comprehensive research reports on any topic by creating multiple AI analyst personas, conducting simulated expert interviews, and synthesizing findings into cohesive reports.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Architecture](#project-architecture)
- [Detailed Project Logic](#detailed-project-logic)
- [LangGraph Concepts Used](#langgraph-concepts-used)
- [Project Structure](#project-structure)
- [Contributing](#contributing)

---

## Overview

The Research Assistant is an advanced multi-agent system that automates the research process by:

1. **Creating specialized AI analyst personas** based on your research topic
2. **Conducting simulated expert interviews** where analysts ask questions and "experts" answer using web search and Wikipedia
3. **Synthesizing information** from multiple perspectives into a comprehensive report
4. **Generating structured reports** with introduction, findings, conclusion, and sources

This system leverages LangGraph's powerful workflow orchestration capabilities to manage complex, parallel research workflows with human-in-the-loop feedback.

---

## Features

✨ **Multi-Perspective Analysis**: Creates 3+ specialized analyst personas with unique viewpoints  
🔄 **Parallel Execution**: Conducts multiple interviews simultaneously using LangGraph's Send API  
🌐 **Real-time Information Gathering**: Uses DuckDuckGo and Wikipedia for current information  
👤 **Human-in-the-Loop**: Allows human feedback to refine analyst personas before research  
📊 **Comprehensive Reports**: Generates well-structured markdown reports with proper citations  
⚙️ **Configurable**: Environment-based configuration for all parameters  
🎯 **State Management**: Persistent checkpointing for resumable workflows  
📈 **Visual Debugging**: Generates graph visualizations of the workflow

---

## Installation

### Prerequisites

- Python 3.12+
- OpenAI API key

### Setup

1. **Clone or navigate to the project directory**:
```bash
cd /home/anurag-r/work/pycode/research-assistant
```

2. **Install dependencies using uv** (recommended):
```bash
uv sync
```

Or using pip:
```bash
pip install -e .
```

3. **Create a `.env` file** with your configuration:
```bash
cp .env.example .env
```

4. **Add your OpenAI API key** to `.env`:
```bash
OPENAI_API_KEY=your_openai_api_key_here
```

---

## Configuration

The application uses environment variables for configuration. All settings have sensible defaults.

### Environment Variables

Create a `.env` file in the project root:

```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional - LLM Settings
RESEARCH_OPENAI_MODEL=gpt-4o           # Default: gpt-4o
RESEARCH_OPENAI_TEMPERATURE=0.0        # Default: 0.0

# Optional - Research Settings
RESEARCH_MAX_ANALYSTS=3                # Default: 3
RESEARCH_MAX_INTERVIEW_TURNS=2         # Default: 2

# Optional - Output Settings
RESEARCH_OUTPUT_DIR=outputs            # Default: outputs
RESEARCH_SAVE_GRAPHS=true             # Default: true

# Optional - Search Settings
RESEARCH_WIKIPEDIA_MAX_DOCS=2         # Default: 2
RESEARCH_DUCKDUCKGO_FORMAT=list       # Default: list
```

### Configuration in Code

All configuration is managed through `config.py`:

```python
from config import settings

# Access settings anywhere in the code
model = settings.openai_model
max_analysts = settings.max_analysts
```

---

## Usage

### Basic Usage

Run the research assistant with default topic:

```bash
python main.py
```

Or activate the virtual environment first:

```bash
source .venv/bin/activate  # On Linux/Mac
# or
.venv\Scripts\activate     # On Windows

python main.py
```

### Programmatic Usage

```python
from main import main

# Use defaults
main()

# Or customize
main(
    topic="The impact of quantum computing on cryptography",
    max_analysts=5
)
```

### Understanding the Workflow

When you run the application:

1. **Analyst Creation**: The system creates specialized analyst personas
2. **Human Feedback** (interruption point): You can review and request changes
3. **Parallel Interviews**: Analysts conduct research simultaneously
4. **Report Generation**: Findings are synthesized into a comprehensive report
5. **Output**: Final report saved to `outputs/final_report_TIMESTAMP.md`

---

## Project Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Main Research Graph                       │
│                  (ResearchGraphState)                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  1. Create Analysts                                          │
│     - Analyze topic                                          │
│     - Generate 3+ specialized personas                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  2. Human Feedback (Interrupt)                               │
│     - Review analyst personas                                │
│     - Provide optional feedback                              │
│     - Loop back to adjust or proceed                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  3. Conduct Interviews (Parallel - Send API)                 │
│     ┌───────────────┬───────────────┬───────────────┐       │
│     │  Analyst 1    │  Analyst 2    │  Analyst 3    │       │
│     │  Interview    │  Interview    │  Interview    │       │
│     │  Subgraph     │  Subgraph     │  Subgraph     │       │
│     └───────────────┴───────────────┴───────────────┘       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  4. Report Synthesis (Parallel)                              │
│     ┌─────────────┬─────────────┬─────────────────┐         │
│     │Introduction │   Content   │   Conclusion    │         │
│     └─────────────┴─────────────┴─────────────────┘         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  5. Finalize Report                                          │
│     - Combine all sections                                   │
│     - Add citations                                          │
│     - Save to file                                           │
└─────────────────────────────────────────────────────────────┘
```

### Interview Subgraph (Detailed)

Each analyst runs this workflow independently:

```
┌─────────────────────────────────────────────────────────────┐
│                    Interview Subgraph                        │
│                   (InterviewState)                           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Generate Question                                           │
│  - Analyst asks question based on their persona              │
└─────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
┌─────────────────────────┐   ┌─────────────────────────┐
│  Search Web             │   │  Search Wikipedia       │
│  (DuckDuckGo)           │   │  (WikipediaLoader)      │
└─────────────────────────┘   └─────────────────────────┘
                    │                   │
                    └─────────┬─────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Generate Answer                                             │
│  - "Expert" answers using gathered context                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Route Decision                                              │
│  - Max turns reached? → Save Interview                       │
│  - Analyst says "Thank you"? → Save Interview                │
│  - Otherwise → Generate Question (loop)                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Save Interview                                              │
│  - Store conversation transcript                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Write Section                                               │
│  - Convert interview to report section with citations        │
└─────────────────────────────────────────────────────────────┘
```

---

## Detailed Project Logic

### Phase 1: Analyst Creation

**File**: `graphs/analyst/analyst_nodes.py::create_analysts()`

**Purpose**: Generate specialized AI analyst personas based on the research topic.

**Logic**:
1. Takes the research topic from state
2. Uses GPT-4 with structured output (Pydantic `Perspectives` model)
3. Prompts LLM to identify interesting themes in the topic
4. Creates `max_analysts` number of personas, each with:
   - **Name**: Fitting their persona
   - **Role**: Their specific focus area
   - **Affiliation**: Their institutional/professional context
   - **Description**: Their motivations, concerns, and expertise

**Example Output**:
```python
Analyst(
    name="Dr. Sarah Chen",
    role="AI Safety Researcher",
    affiliation="AI Safety Institute",
    description="Focuses on ensuring agent frameworks have proper safety..."
)
```

### Phase 2: Human-in-the-Loop Feedback

**File**: `graphs/analyst/analyst_nodes.py::human_feedback()` & `initiate_all_interviews()`

**Purpose**: Allow human review and refinement of analyst personas.

**Logic**:
1. **Interrupt Point**: Graph pauses execution before interviews
2. **Human Reviews**: User sees generated analysts
3. **Conditional Routing** (`initiate_all_interviews`):
   - If `human_analyst_feedback` exists → Loop back to `create_analysts`
   - If no feedback (None) → Proceed to interviews
4. **State Update**: Uses `graph.update_state()` to inject feedback

**Example Interaction**:
```python
# System generates 3 analysts
# User reviews and says: "Add a CEO of a gen AI startup"
graph.update_state(
    thread,
    {"human_analyst_feedback": "Add a CEO of a gen AI startup"},
    as_node="human_feedback"
)
# System regenerates with 4 analysts including the CEO perspective
```

### Phase 3: Parallel Interview Execution

**File**: `graphs/analyst/analyst_nodes.py::initiate_all_interviews()`

**Purpose**: Run multiple interview subgraphs in parallel using LangGraph's Send API.

**Logic**:
1. **Map Operation**: For each analyst, create a Send object
2. **Send API**: Dispatches interview subgraph with:
   - `analyst`: The analyst persona
   - `messages`: Initial conversation starter
   - `topic`: Research topic
3. **Parallel Execution**: All interviews run simultaneously
4. **State Accumulation**: Results collected in `sections` list

**Code**:
```python
return [
    Send("conduct_interviews", {
        "analyst": analyst,
        "topic": topic,
        "messages": [HumanMessage(content=f"So you said you were writing an article on {topic}")]
    }) 
    for analyst in state.get("analysts")
]
```

### Phase 4: Interview Subgraph (Per Analyst)

**File**: `graphs/interview/interview_nodes.py`

#### Step 4.1: Generate Question
**Function**: `generate_question()`

- Analyst asks a question based on their persona
- Uses analyst's persona context in system prompt
- Maintains conversation history

#### Step 4.2: Information Retrieval (Parallel)
**Functions**: `serach_web()` & `search_wikipedia()`

**Search Web**:
- Converts analyst's question to search query
- Uses DuckDuckGo to find current information
- Formats results as structured documents

**Search Wikipedia**:
- Converts question to Wikipedia query
- Loads up to 2 articles
- Formats with source metadata

**Both run in parallel** to gather diverse information quickly.

#### Step 4.3: Generate Answer
**Function**: `generate_answer()`

- "Expert" role responds using gathered context
- Cites sources using [1], [2] format
- Stays strictly within provided information
- Tagged as 'expert' for conversation tracking

#### Step 4.4: Routing Logic
**Function**: `route_messages()`

**Decision Tree**:
```python
if current_turns >= max_interview_turns:
    return "save_interview"  # Exit condition 1
    
if "Thank you so much for your help" in last_question:
    return "save_interview"  # Exit condition 2
    
return "ask_question"  # Continue interviewing
```

#### Step 4.5: Save & Synthesize
**Functions**: `save_interview()` & `write_section()`

- **Save Interview**: Converts message history to text transcript
- **Write Section**: Transforms interview into formal report section with:
  - Engaging title based on analyst focus
  - Summary with key insights (400 words max)
  - Proper citations
  - Source list

### Phase 5: Report Generation

**File**: `graphs/analyst/analyst_nodes.py`

#### Step 5.1: Parallel Report Writing
Three functions run simultaneously:

**Write Report** (`write_report()`):
- Consolidates all analyst sections
- Creates cohesive narrative
- Merges citations
- Produces "Insights" section

**Write Introduction** (`write_introduction()`):
- Reviews all sections
- Creates compelling title
- Writes preview (100 words)
- Sets context for reader

**Write Conclusion** (`write_conclusion()`):
- Reviews all sections
- Synthesizes key takeaways
- Provides closure (100 words)

#### Step 5.2: Finalize Report
**Function**: `finalize_report()`

**Assembly Logic**:
```
[Title & Introduction]
---
[Main Content/Insights]
---
[Conclusion]
---
## Sources
[Consolidated source list]
```

**Special Handling**:
- Strips "## Insights" header if present
- Extracts and moves sources to end
- Adds markdown separators
- Ensures proper formatting

### Phase 6: Output & Persistence

**File**: `utils/file_utils.py::save_report()`

**Logic**:
1. Creates `outputs/` directory if needed
2. Generates timestamp for unique filename
3. Saves as `final_report_YYYYMMDD_HHMMSS.md`
4. Reports save location to user

---

## LangGraph Concepts Used

This project demonstrates advanced LangGraph patterns and concepts:

### 1. **StateGraph with TypedDict States**

**Concept**: LangGraph uses typed state objects to track data through the workflow.

**Implementation**:
```python
class ResearchGraphState(TypedDict):
    topic: str
    max_analysts: int
    human_analyst_feedback: str
    analysts: List[Analyst]
    sections: Annotated[List, operator.add]  # Accumulator
    introduction: str
    content: str
    conclusion: str
    final_report: str
```

**Key Features**:
- `Annotated[List, operator.add]`: Accumulates sections from parallel interviews
- Type safety with TypedDict
- Clear state schema

### 2. **Interrupt Before (Human-in-the-Loop)**

**Concept**: Pause graph execution for human review/input.

**Implementation**:
```python
main_builder_graph = main_builder.compile(
    interrupt_before=['human_feedback'],
    checkpointer=memory
)
```

**Usage**:
```python
# First run - stops at human_feedback
for event in graph.stream(inputs, thread):
    # Display analysts for review
    
# Update state with feedback
graph.update_state(thread, {"human_analyst_feedback": "..."}, as_node="human_feedback")

# Resume execution
for event in graph.stream(None, thread):
    # Continues from human_feedback
```

**Benefits**:
- User can review and modify analyst personas
- Full control over workflow progression
- State persists between runs

### 3. **Conditional Edges with Dynamic Routing**

**Concept**: Route execution based on state conditions.

**Implementation**:
```python
def initiate_all_interviews(state: ResearchGraphState):
    if state.get("human_analyst_feedback"):
        return "create_analysts"  # Loop back
    else:
        return [Send(...), Send(...), Send(...)]  # Parallel execution

main_builder.add_conditional_edges(
    "human_feedback",
    initiate_all_interviews,
    ["create_analysts", "conduct_interviews"]
)
```

**Pattern**: Decision function returns next node name or Send objects.

### 4. **Send API for Parallel Execution (Map-Reduce)**

**Concept**: Fan-out to multiple parallel executions, then reduce results.

**Implementation (Map)**:
```python
return [
    Send("conduct_interviews", {
        "analyst": analyst1,
        "messages": [...]
    }),
    Send("conduct_interviews", {
        "analyst": analyst2,
        "messages": [...]
    }),
    Send("conduct_interviews", {
        "analyst": analyst3,
        "messages": [...]
    })
]
```

**Result (Reduce)**:
- All interviews run simultaneously
- Results accumulate in `state.sections` (using `operator.add`)
- Significantly faster than sequential execution

**Use Case**: Perfect for independent operations that need aggregation.

### 5. **Nested Subgraphs**

**Concept**: Embed complete graphs as nodes in parent graphs.

**Implementation**:
```python
# Create interview subgraph
interview_builder = StateGraph(InterviewState)
interview_builder.add_node("ask_question", generate_question)
# ... add more nodes
interview_graph = interview_builder.compile()

# Use as node in main graph
main_builder = StateGraph(ResearchGraphState)
main_builder.add_node("conduct_interviews", interview_graph)
```

**Benefits**:
- Modularity and reusability
- Clear separation of concerns
- Independent state management per subgraph
- Easier testing and debugging

### 6. **MessagesState for Conversation Management**

**Concept**: Built-in state for managing chat conversations.

**Implementation**:
```python
from langgraph.graph import MessagesState

class InterviewState(MessagesState):
    max_num_turns: int
    context: Annotated[List, operator.add]
    analyst: Analyst
    interview: str
    sections: list
```

**Features**:
- Automatic message history management
- Built-in `messages` field
- Supports all LangChain message types
- Handles message appending automatically

### 7. **Checkpointing with MemorySaver**

**Concept**: Persist graph state for resumability.

**Implementation**:
```python
from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()
graph = builder.compile(checkpointer=memory)
```

**Usage**:
```python
thread = {"configurable": {"thread_id": "1"}}

# Run 1: Stops at interrupt
graph.stream(inputs, thread)

# Run 2: Resumes from checkpoint
graph.stream(None, thread)

# Access final state
final_state = graph.get_state(thread)
```

**Benefits**:
- Resume interrupted workflows
- Debug by inspecting state at any point
- Multi-session support with thread IDs

### 8. **Structured Output with Pydantic**

**Concept**: Enforce LLM response schemas using Pydantic models.

**Implementation**:
```python
class Analyst(BaseModel):
    affiliation: str
    name: str
    role: str
    description: str

structured_llm = llm.with_structured_output(Perspectives)
analysts = structured_llm.invoke([SystemMessage(...)])
# Returns validated Perspectives object
```

**Benefits**:
- Type-safe LLM outputs
- Automatic validation
- Clear data contracts

### 9. **Parallel Fan-out with Multiple Edges**

**Concept**: Execute multiple nodes simultaneously from one node.

**Implementation**:
```python
# After interviews complete, run 3 nodes in parallel
main_builder.add_edge("conduct_interviews", "write_report")
main_builder.add_edge("conduct_interviews", "write_introduction")
main_builder.add_edge("conduct_interviews", "write_conclusion")

# Merge results
main_builder.add_edge(
    ["write_report", "write_introduction", "write_conclusion"],
    "finalize_report"
)
```

**Pattern**: Multiple edges from one source = parallel execution.

### 10. **State Reducers with operator.add**

**Concept**: Define how state fields combine from parallel branches.

**Implementation**:
```python
from typing import Annotated
import operator

class ResearchGraphState(TypedDict):
    sections: Annotated[List, operator.add]  # Accumulates from parallel nodes
```

**Behavior**:
```python
# Interview 1 returns: {"sections": ["Section A"]}
# Interview 2 returns: {"sections": ["Section B"]}
# Interview 3 returns: {"sections": ["Section C"]}
# Final state: {"sections": ["Section A", "Section B", "Section C"]}
```

### 11. **Conditional Routing within Subgraphs**

**Concept**: Dynamic routing based on conversation state.

**Implementation**:
```python
def route_messages(state: InterviewState) -> str:
    messages = state['messages']
    max_turns = state.get("max_num_turns", 2)
    current_turns = len([m for m in messages if m.name == 'expert'])
    
    if current_turns >= max_turns:
        return "save_interview"
    if "Thank you so much for your help" in messages[-2].content:
        return "save_interview"
    return "ask_question"

interview_builder.add_conditional_edges(
    "answer_question",
    route_messages,
    ["ask_question", "save_interview"]
)
```

**Use Case**: Loop until max turns or conversation naturally ends.

### 12. **Graph Visualization**

**Concept**: Visual debugging and documentation of workflows.

**Implementation**:
```python
png_data = graph.get_graph(xray=1).draw_mermaid_png()
with open("graph.png", "wb") as f:
    f.write(png_data)
```

**Benefits**:
- Understand complex workflows visually
- Documentation
- Debug routing issues
- Share architecture with team

---

## Project Structure

```
research-assistant/
├── README.md                        # This file
├── config.py                        # Configuration management
├── init_llm.py                      # LLM initialization
├── main.py                          # Entry point
│
├── states/                          # State definitions
│   ├── __init__.py                  # Package exports
│   ├── models.py                    # Pydantic models (Analyst, etc.)
│   ├── analyst_state.py             # Analyst generation state
│   ├── interview_state.py           # Interview workflow state
│   └── research_state.py            # Main research state
│
├── prompts/                         # LLM prompt templates
│   ├── __init__.py
│   ├── analyst_creation_prompt.py   # Create analyst personas
│   ├── expert_answer_prompt.py      # Expert response template
│   ├── interview_prompt.py          # Analyst question template
│   ├── intro_conclusion_prompts.py  # Report intro/conclusion
│   ├── section_report_prompt.py     # Section writing template
│   ├── web_query_prompt.py          # Search query generation
│   └── write_report_prompt.py       # Main report template
│
├── graphs/                          # LangGraph definitions
│   ├── __init__.py
│   ├── analyst/                     # Main research graph
│   │   ├── __init__.py
│   │   ├── analyst_graph.py         # Graph structure
│   │   └── analyst_nodes.py         # Node functions
│   └── interview/                   # Interview subgraph
│       ├── __init__.py
│       ├── interview_graph.py       # Subgraph structure
│       └── interview_nodes.py       # Interview node functions
│
├── utils/                           # Utility functions
│   ├── __init__.py
│   └── file_utils.py                # File I/O helpers
│
├── outputs/                         # Generated reports
│   └── final_report_*.md
│
├── pyproject.toml                   # Project metadata & dependencies
├── uv.lock                          # Locked dependencies
└── .env                             # Environment configuration (not in git)
```

---

## Dependencies

**Core**:
- `langgraph` - Graph-based workflow orchestration
- `langchain` - LLM framework
- `langchain-openai` - OpenAI integration
- `langchain-community` - Community tools (DuckDuckGo, Wikipedia)

**Search & Retrieval**:
- `duckduckgo-search` - Web search
- `wikipedia` - Wikipedia API access

**Configuration**:
- `python-dotenv` - Environment variable management

**Models**:
- `pydantic` - Data validation and settings

---

## Contributing

Contributions are welcome! Areas for improvement:

- **Error Handling**: Add try-catch blocks for API calls
- **Logging**: Replace print statements with proper logging
- **Testing**: Add unit and integration tests
- **CLI**: Add argparse for command-line interface
- **Multiple LLM Support**: Add support for Anthropic, Google, etc.
- **Streaming**: Add streaming support for real-time output
- **Cost Tracking**: Track and report API costs
- **Resume Capability**: Better checkpoint management

---

## License

This project is licensed under the MIT License.

---

## Acknowledgments

Built with:
- [LangGraph](https://github.com/langchain-ai/langgraph) - State machine orchestration
- [LangChain](https://github.com/langchain-ai/langchain) - LLM framework
- [OpenAI](https://openai.com/) - GPT-4 language model

---

## Support

For issues, questions, or contributions, please open an issue in the repository.

**Happy Researching! 🚀**

