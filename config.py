"""Configuration management for the research assistant application."""
import os
from typing import Optional


class Settings:
    """Application settings and configuration."""
    
    def __init__(self):
        """Initialize settings from environment variables."""
        # LLM Configuration
        self.openai_model: str = os.getenv("RESEARCH_OPENAI_MODEL", "gpt-4o")
        self.openai_temperature: float = float(os.getenv("RESEARCH_OPENAI_TEMPERATURE", "0.0"))
        
        # Research Configuration
        self.max_analysts: int = int(os.getenv("RESEARCH_MAX_ANALYSTS", "3"))
        self.max_interview_turns: int = int(os.getenv("RESEARCH_MAX_INTERVIEW_TURNS", "2"))
        
        # Output Configuration
        self.output_directory: str = os.getenv("RESEARCH_OUTPUT_DIR", "outputs")
        self.save_graph_images: bool = os.getenv("RESEARCH_SAVE_GRAPHS", "true").lower() == "true"
        
        # Wikipedia Configuration
        self.wikipedia_max_docs: int = int(os.getenv("RESEARCH_WIKIPEDIA_MAX_DOCS", "2"))
        
        # DuckDuckGo Configuration
        self.duckduckgo_output_format: str = os.getenv("RESEARCH_DUCKDUCKGO_FORMAT", "list")
    
    def __repr__(self) -> str:
        """Return string representation of settings."""
        return (
            f"Settings(model={self.openai_model}, "
            f"temperature={self.openai_temperature}, "
            f"max_analysts={self.max_analysts}, "
            f"max_interview_turns={self.max_interview_turns})"
        )


# Global settings instance
settings = Settings()

