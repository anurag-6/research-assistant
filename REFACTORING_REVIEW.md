# Code Review: Refactoring from Monolithic Script to Structured Project

**Reviewer:** Python Project Structuring Expert  
**Date:** January 10, 2026  
**Original:** `groq-test/research-agent.py` (631 lines)  
**Refactored:** `research-assistant/` (modular structure)

---

## Executive Summary

✅ **Overall Assessment: GOOD REFACTORING with Critical Issues to Fix**

The refactoring demonstrates solid understanding of separation of concerns and modular design. However, there are **2 critical bugs** that will prevent the code from running, along with several structural improvements needed.

**Severity Breakdown:**
- 🔴 **Critical Issues:** 2 (will break execution)
- 🟡 **Major Issues:** 5 (structural/maintainability)
- 🟢 **Minor Issues:** 4 (best practices)

---

## Part 1: Project Structure Review

### Current Structure
```
research-assistant/
├── main.py                      # Entry point
├── init_llm.py                  # LLM initialization
├── pyproject.toml               # Dependencies
├── graphs/
│   ├── analyst/
│   │   ├── analyst_graph.py     # Main graph definition
│   │   └── analyst_nodes.py     # Node functions
│   └── interview/
│       ├── interview_graph.py   # Interview graph
│       └── interview_nodes.py   # Interview node functions
├── states/
│   ├── analyst_state.py         # Analyst models & state
│   ├── interview_state.py       # Interview state
│   └── research_state.py        # Research graph state
├── prompts/
│   ├── analyst_creation_prompt.py
│   ├── expert_answer_prompt.py
│   ├── interview_prompt.py
│   ├── intro_conclusion_prompts.py
│   ├── section_report_prompt.py
│   ├── web_query_prompt.py
│   └── write_report_prompt.py
└── utils/
    ├── __init__.py
    └── file_utils.py
```

### ✅ What You Did Well

1. **Clear Separation of Concerns**
   - States, prompts, graphs, and utilities are properly separated
   - Each module has a single, well-defined responsibility

2. **Logical Grouping**
   - Graph-related code grouped by domain (analyst/interview)
   - All prompts in dedicated directory
   - State definitions centralized

3. **Reusability**
   - Prompts extracted as constants (easy to modify)
   - Utility functions for common operations
   - LLM initialization centralized

4. **Clean Entry Point**
   - `main.py` is concise and readable
   - Clear execution flow

---

## Part 2: Critical Issues (Must Fix)

### 🔴 CRITICAL #1: Broken Import in `interview_graph.py`

**Location:** `graphs/interview/interview_graph.py:3`

```python
from interview_nodes import (generate_question, serach_web, ...)
```

**Problem:** Missing package prefix. This is a **relative import without proper syntax**.

**Impact:** ❌ Application will crash immediately with `ModuleNotFoundError`

**Fix Required:**
```python
# Option 1: Relative import (recommended for same package)
from .interview_nodes import (generate_question, serach_web, ...)

# Option 2: Absolute import
from graphs.interview.interview_nodes import (generate_question, serach_web, ...)
```

---

### 🔴 CRITICAL #2: Incorrect LLM Invocation in `interview_nodes.py`

**Location:** `graphs/interview/interview_nodes.py:47`

```python
def search_wikipedia(state: InterviewState):
    structured_llm = llm.with_structured_output(SearchQuery)
    search_query = structured_llm.invoke(SystemMessage(content=WEB_QUERY_PROMPT)+ state['messages'])
    # ❌ This will fail - can't add SystemMessage + list
```

**Problem:** Attempting to add `SystemMessage` object directly to a list using `+` operator.

**Impact:** ❌ Runtime error: `TypeError: unsupported operand type(s) for +`

**Fix Required:**
```python
def search_wikipedia(state: InterviewState):
    structured_llm = llm.with_structured_output(SearchQuery)
    search_query = structured_llm.invoke([SystemMessage(content=WEB_QUERY_PROMPT)] + state['messages'])
    # ✅ Wrap SystemMessage in list first
```

**Note:** Line 30 in the same file does this correctly - this is an inconsistency.

---

## Part 3: Major Structural Issues

### 🟡 MAJOR #1: Model Duplication Across State Files

**Problem:** The `Analyst` class is defined in **TWO** places:
- `states/analyst_state.py` (lines 4-16)
- `states/interview_state.py` (lines 7-15)

**Impact:**
- Violates DRY principle
- Maintenance nightmare (update in two places)
- Potential for inconsistencies
- Confusing for other developers

**Recommendation:**
```python
# states/models.py (NEW FILE)
from pydantic import BaseModel, Field

class Analyst(BaseModel):
    affiliation: str = Field(description="Primary affiliation of the analyst")
    name: str = Field(description="Name of the analyst")
    role: str = Field(description="Role of the analyst in the context of the topic")
    description: str = Field(description="Description of the analyst focus, motive, concerns")

    @property
    def persona(self):
        return f" Name: {self.name}, Role: {self.role}, Affiliation: {self.affiliation}, Description: {self.description}"

class Perspectives(BaseModel):
    analysts: List[Analyst] = Field(description="Comprehensive list of analysts with their role and affiliations")

class SearchQuery(BaseModel):
    search_query: str = Field(None, description="Search query for retrieval")
```

Then import from this single source:
```python
# states/analyst_state.py
from .models import Analyst, Perspectives

# states/interview_state.py
from .models import Analyst, SearchQuery
```

---

### 🟡 MAJOR #2: Missing `__init__.py` Files

**Problem:** Most packages lack `__init__.py` files:
- ❌ `graphs/__init__.py`
- ❌ `graphs/analyst/__init__.py`
- ❌ `graphs/interview/__init__.py`
- ❌ `states/__init__.py`
- ❌ `prompts/__init__.py`
- ✅ `utils/__init__.py` (exists)

**Impact:**
- Imports may fail in some Python environments
- Cannot use package-level imports
- Not following Python package conventions
- May cause issues with tools like pytest, mypy, etc.

**Recommendation:** Create `__init__.py` in all package directories (can be empty or with explicit exports)

```python
# graphs/__init__.py
from .analyst.analyst_graph import main_builder_graph
from .interview.interview_graph import interview_graph

__all__ = ['main_builder_graph', 'interview_graph']
```

---

### 🟡 MAJOR #3: Inconsistent Import Styles

**Problem:** Mix of absolute and relative imports throughout the codebase:

```python
# analyst_nodes.py - uses absolute imports
from states.research_state import ResearchGraphState
from init_llm import llm

# interview_nodes.py - uses absolute imports
from states.interview_state import InterviewState

# interview_graph.py - uses incorrect relative import
from interview_nodes import (...)  # ❌ Missing dot
```

**Impact:**
- Harder to refactor
- Confusing for maintainers
- May break when running from different directories

**Recommendation:** Choose one style consistently:

**Option A: Relative imports within packages (recommended)**
```python
# graphs/analyst/analyst_nodes.py
from ...states.research_state import ResearchGraphState
from ...init_llm import llm

# graphs/interview/interview_nodes.py
from ...states.interview_state import InterviewState
from .interview_graph import interview_graph
```

**Option B: Absolute imports everywhere**
```python
# All files use:
from research_assistant.states.research_state import ResearchGraphState
from research_assistant.init_llm import llm
```

For Option B, you'd need to add to `pyproject.toml`:
```toml
[project]
name = "research-assistant"
# Add this to make it installable:

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"
```

---

### 🟡 MAJOR #4: Configuration Hardcoded in `init_llm.py`

**Problem:**
```python
llm = ChatOpenAI(
    model="gpt-4o",  # Hardcoded
    temperature=0    # Hardcoded
)
```

**Impact:**
- Cannot change model without editing code
- Cannot configure for different environments (dev/prod)
- Not following 12-factor app principles

**Recommendation:**
```python
# config.py (NEW FILE)
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openai_model: str = "gpt-4o"
    openai_temperature: float = 0.0
    max_analysts: int = 3
    max_interview_turns: int = 2
    output_directory: str = "outputs"
    
    class Config:
        env_file = ".env"
        env_prefix = "RESEARCH_"

settings = Settings()

# init_llm.py
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from .config import settings

load_dotenv()

llm = ChatOpenAI(
    model=settings.openai_model,
    temperature=settings.openai_temperature
)
```

---

### 🟡 MAJOR #5: No Error Handling

**Problem:** Zero error handling throughout the codebase:
- API calls to OpenAI (can fail)
- Web searches (can timeout)
- Wikipedia queries (can fail)
- File I/O operations

**Example vulnerable code:**
```python
# interview_nodes.py:32
res = serach_docs.invoke(search_query.search_query)  # Can fail
```

**Recommendation:**
```python
def serach_web(state: InterviewState):
    try:
        structured_llm = llm.with_structured_output(SearchQuery)
        search_query = structured_llm.invoke([SystemMessage(content=WEB_QUERY_PROMPT)] + state['messages'])
        
        serach_docs = DuckDuckGoSearchResults(output_format="list")
        res = serach_docs.invoke(search_query.search_query)
        
        if not res:
            return {"context": ["No search results found."]}
        
        formated_search_res = "\n\n ---- \n\n".join([
            f'<Document href="{doc.get("link", "N/A")} /> \n {doc.get("snippet", "")}  \n </Document>'
            for doc in res
        ])
        
        return {"context": [formated_search_res]}
    except Exception as e:
        print(f"Web search failed: {e}")
        return {"context": [f"Search failed: {str(e)}"]}
```

---

## Part 4: Minor Issues & Best Practices

### 🟢 MINOR #1: Typo in Function Name

**Location:** Multiple files

```python
def serach_web(state: InterviewState):  # ❌ "serach" should be "search"
```

**Files affected:**
- `graphs/interview/interview_nodes.py:28`
- `graphs/interview/interview_graph.py:3, 13`

**Impact:** Unprofessional, confusing for other developers

---

### 🟢 MINOR #2: Typos in Model Field Descriptions

**Location:** `states/analyst_state.py:8` and `states/interview_state.py:11`

```python
description: str = Field(description="Description of the analyst focust, motive, concerns")
# ❌ "focust" should be "focus"
```

**Location:** `states/analyst_state.py:16` and `states/interview_state.py:15`

```python
analysts: List[Analyst] = Field(description="Comprehensive list of analysts with thier role and affilations")
# ❌ "thier" should be "their"
# ❌ "affilations" should be "affiliations"
```

---

### 🟢 MINOR #3: Inconsistent Prompt Formatting

**Problem:** Some prompt files have extra blank lines at the top:
- `interview_prompt.py` - 3 blank lines
- `web_query_prompt.py` - 4 blank lines

**Recommendation:** Remove leading blank lines for consistency

---

### 🟢 MINOR #4: Missing Type Hints

**Location:** `graphs/interview/interview_nodes.py:95`

```python
def route_messages(state: InterviewState, name:str = 'expert'):
    # Missing return type hint
```

**Recommendation:**
```python
def route_messages(state: InterviewState, name: str = 'expert') -> str:
```

---

## Part 5: Logic Verification

### ✅ Graph Structure Preserved

Comparing original vs refactored:

**Original Graph Flow:**
```
create_analysts → human_feedback → conduct_interviews → 
[write_report, write_introduction, write_conclusion] → finalize_report
```

**Refactored Graph Flow:**
```python
# analyst_graph.py maintains same structure
main_builder.add_edge(START, "create_analysts")
main_builder.add_edge("create_analysts", "human_feedback")
main_builder.add_conditional_edges("human_feedback", initiate_all_interviews, ...)
# ✅ Identical logic
```

### ✅ Interview Subgraph Preserved

**Original:**
```
ask_question → [search_web, search_wikipedia] → answer_question → 
(conditional) → save_interview → write_section
```

**Refactored:**
```python
# interview_graph.py maintains same structure
interview_builder.add_edge(START, "ask_question")
interview_builder.add_edge("ask_question", "search_web")
interview_builder.add_edge("ask_question", "search_wikipedia")
# ✅ Identical logic
```

### ✅ State Management Preserved

All state fields from original `TypedDict` classes are present in refactored versions.

### ⚠️ Potential Logic Issue: Missing Return Statement

**Location:** `graphs/interview/interview_nodes.py:106-107`

```python
if "Thank you so much for your help" in last_question.content:
    "save_interview"  # ❌ Missing return statement!

return "ask_question"
```

**Impact:** This condition will never trigger - the string is evaluated but not returned.

**Fix:**
```python
if "Thank you so much for your help" in last_question.content:
    return "save_interview"  # ✅ Add return
```

**Note:** This bug exists in the original code too (line 261), so it's not introduced by refactoring.

---

## Part 6: Suggested Improvements

### 1. Add Project Root to Python Path

**Create:** `research-assistant/__init__.py`

```python
"""Research Assistant - LangGraph-based research automation."""
__version__ = "0.1.0"
```

### 2. Add Logging Instead of Print Statements

```python
# utils/logger.py (NEW FILE)
import logging
from pathlib import Path

def setup_logger(name: str, log_file: str = "research_assistant.log") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger
```

### 3. Add CLI Interface

```python
# cli.py (NEW FILE)
import argparse
from main import main

def parse_args():
    parser = argparse.ArgumentParser(description="Research Assistant")
    parser.add_argument("--topic", type=str, required=True, help="Research topic")
    parser.add_argument("--max-analysts", type=int, default=3, help="Maximum number of analysts")
    parser.add_argument("--output-dir", type=str, default="outputs", help="Output directory")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    main(topic=args.topic, max_analysts=args.max_analysts, output_dir=args.output_dir)
```

### 4. Add Tests Structure

```
research-assistant/
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_analyst_nodes.py
│   ├── test_interview_nodes.py
│   └── test_states.py
```

### 5. Add Documentation

```python
# Each node function should have docstrings:
def create_analysts(state: ResearchGraphState) -> dict:
    """
    Create analyst personas based on the research topic.
    
    Args:
        state: Current research graph state containing topic and max_analysts
        
    Returns:
        Dictionary with 'analysts' key containing list of Analyst objects
        
    Raises:
        ValueError: If topic is empty or max_analysts is invalid
    """
```

### 6. Add Requirements for Development

```toml
# pyproject.toml - add dev dependencies
[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "black>=23.7.0",
    "ruff>=0.0.285",
    "mypy>=1.5.0",
]
```

---

## Part 7: Recommended Folder Structure (Ideal)

```
research-assistant/
├── README.md                    # Project documentation
├── pyproject.toml               # Dependencies & config
├── .env.example                 # Example environment variables
├── .gitignore                   # Git ignore rules
│
├── research_assistant/          # Main package (note underscore)
│   ├── __init__.py
│   ├── main.py                  # Entry point
│   ├── config.py                # Configuration management
│   ├── llm.py                   # LLM initialization
│   │
│   ├── models/                  # Pydantic models
│   │   ├── __init__.py
│   │   ├── analyst.py
│   │   └── search.py
│   │
│   ├── states/                  # Graph states
│   │   ├── __init__.py
│   │   ├── analyst_state.py
│   │   ├── interview_state.py
│   │   └── research_state.py
│   │
│   ├── graphs/                  # LangGraph definitions
│   │   ├── __init__.py
│   │   ├── analyst/
│   │   │   ├── __init__.py
│   │   │   ├── graph.py
│   │   │   └── nodes.py
│   │   └── interview/
│   │       ├── __init__.py
│   │       ├── graph.py
│   │       └── nodes.py
│   │
│   ├── prompts/                 # Prompt templates
│   │   ├── __init__.py
│   │   └── [prompt files]
│   │
│   └── utils/                   # Utilities
│       ├── __init__.py
│       ├── file_utils.py
│       └── logger.py
│
├── tests/                       # Test suite
│   ├── __init__.py
│   ├── conftest.py
│   └── [test files]
│
├── outputs/                     # Generated reports
└── logs/                        # Application logs
```

**Key Changes:**
1. Package name uses underscore (`research_assistant`) not hyphen
2. Models separated from states
3. Clear distinction between package code and outputs
4. Follows Python packaging conventions

---

## Summary & Action Items

### 🔴 Critical Fixes (Do First)
1. [ ] Fix import in `graphs/interview/interview_graph.py:3` - add dot for relative import
2. [ ] Fix `search_wikipedia()` in `interview_nodes.py:47` - wrap SystemMessage in list

### 🟡 Major Improvements (Do Next)
3. [ ] Create `states/models.py` and remove duplicate `Analyst` class
4. [ ] Add `__init__.py` to all package directories
5. [ ] Standardize import style (choose relative or absolute)
6. [ ] Create `config.py` for configuration management
7. [ ] Add basic error handling to API calls

### 🟢 Polish (Do When Time Permits)
8. [ ] Fix typo: `serach_web` → `search_web`
9. [ ] Fix typos in model field descriptions
10. [ ] Add return statement in `route_messages()` line 106
11. [ ] Add type hints to all functions
12. [ ] Add logging instead of print statements
13. [ ] Create CLI interface
14. [ ] Add docstrings to all functions
15. [ ] Set up test structure

---

## Final Verdict

**Score: 7.5/10**

**Strengths:**
- ✅ Excellent separation of concerns
- ✅ Logical module organization
- ✅ Preserved all original functionality
- ✅ Improved maintainability
- ✅ Better code reusability

**Weaknesses:**
- ❌ 2 critical bugs that prevent execution
- ❌ Model duplication
- ❌ Missing package initialization files
- ❌ Inconsistent import patterns
- ❌ No error handling

**Recommendation:** Fix the 2 critical bugs immediately, then address the major structural issues. The foundation is solid, but the details need attention. Once fixed, this will be a well-structured, maintainable codebase.

---

**Great job on the refactoring! The structure is sound - just needs these fixes to be production-ready.** 🚀

