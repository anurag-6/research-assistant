"""Prompt templates for the research assistant application."""
from prompts.analyst_creation_prompt import ANALYST_CREATION_PROMPT
from prompts.expert_answer_prompt import EXPERT_ANSWER_PROMPT
from prompts.interview_prompt import INTERVIEW_PROMPT
from prompts.intro_conclusion_prompts import INTRO_CONCLUSION_PROMPT
from prompts.section_report_prompt import SECTION_REPORT_PROMPT
from prompts.web_query_prompt import WEB_QUERY_PROMPT
from prompts.write_report_prompt import WRITE_REPORT_PROMPT

__all__ = [
    'ANALYST_CREATION_PROMPT',
    'EXPERT_ANSWER_PROMPT',
    'INTERVIEW_PROMPT',
    'INTRO_CONCLUSION_PROMPT',
    'SECTION_REPORT_PROMPT',
    'WEB_QUERY_PROMPT',
    'WRITE_REPORT_PROMPT',
]

