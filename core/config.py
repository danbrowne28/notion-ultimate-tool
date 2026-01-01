"""Configuration management for Notion Ultimate Tool."""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv


class Config:
    """Configuration manager for Notion Ultimate Tool."""
    
    def __init__(self, env_file: Optional[str] = None):
        """Initialize configuration.
        
        Args:
            env_file: Path to .env file. If None, looks in current directory.
        """
        # Load environment variables
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()  # Looks for .env in current directory
        
        # Notion API Configuration
        self.notion_token = os.getenv("NOTION_TOKEN")
        self.database_id = os.getenv("DATABASE_ID")
        
        if not self.notion_token:
            raise ValueError("NOTION_TOKEN not found in environment variables")
        if not self.database_id:
            raise ValueError("DATABASE_ID not found in environment variables")
        
        # Cache Configuration
        self.cache_enabled = os.getenv("CACHE_ENABLED", "true").lower() == "true"
        self.cache_ttl = int(os.getenv("CACHE_TTL", "300"))  # 5 minutes
        self.cache_db_path = os.getenv("CACHE_DB_PATH", ".notion_cache.db")
        
        # Rate Limiting
        self.rate_limit_requests_per_second = int(os.getenv("RATE_LIMIT_RPS", "3"))
        
        # Medication Schedule (for ADHD-aware scheduling)
        self.medication_enabled = os.getenv("MEDICATION_ENABLED", "false").lower() == "true"
        self.medication_morning_dose = os.getenv("MEDICATION_MORNING_DOSE", "08:00")
        self.medication_peak_start = os.getenv("MEDICATION_PEAK_START", "10:00")
        self.medication_peak_end = os.getenv("MEDICATION_PEAK_END", "14:00")
        self.medication_afternoon_dose = os.getenv("MEDICATION_AFTERNOON_DOSE", "14:00")
        self.medication_evening_decline = os.getenv("MEDICATION_EVENING_DECLINE", "18:00")
        
        # AI Configuration
        self.ai_enabled = os.getenv("AI_ENABLED", "false").lower() == "true"
        self.ai_model = os.getenv("AI_MODEL", "claude-3-sonnet")
        
        # MCP Configuration
        self.mcp_enabled = os.getenv("MCP_ENABLED", "false").lower() == "true"
        self.mcp_port = int(os.getenv("MCP_PORT", "8765"))
        
        # Logging
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.log_file = os.getenv("LOG_FILE", "notion_tool.log")
        
        # Project Settings
        self.project_root = Path(__file__).parent.parent
        self.data_dir = self.project_root / "data"
        self.logs_dir = self.project_root / "logs"
        
        # Create directories if they don't exist
        self.data_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
    
    def __repr__(self) -> str:
        """Return string representation (hiding sensitive data)."""
        return (
            f"Config("
            f"database_id={self.database_id[:8]}..., "
            f"cache_enabled={self.cache_enabled}, "
            f"medication_enabled={self.medication_enabled}, "
            f"ai_enabled={self.ai_enabled}, "
            f"mcp_enabled={self.mcp_enabled}"
            f")"
        )
