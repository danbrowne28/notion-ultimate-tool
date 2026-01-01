"""Utility functions for Notion Ultimate Tool."""

import time
import logging
from datetime import datetime, time as dt_time
from typing import Dict, Optional, List
from collections import deque


class RateLimiter:
    """Rate limiter for API requests."""
    
    def __init__(self, max_requests_per_second: float = 3.0):
        """Initialize rate limiter.
        
        Args:
            max_requests_per_second: Maximum requests per second
        """
        self.max_requests_per_second = max_requests_per_second
        self.min_interval = 1.0 / max_requests_per_second
        self.last_request_time = 0.0
    
    def wait(self):
        """Wait if necessary to respect rate limit."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_interval:
            sleep_time = self.min_interval - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()


class Logger:
    """Simple logging wrapper."""
    
    def __init__(self, name: str, level: str = "INFO"):
        """Initialize logger.
        
        Args:
            name: Logger name
            level: Log level (DEBUG, INFO, WARNING, ERROR)
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # Create console handler if not exists
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def debug(self, message: str):
        self.logger.debug(message)
    
    def info(self, message: str):
        self.logger.info(message)
    
    def warning(self, message: str):
        self.logger.warning(message)
    
    def error(self, message: str):
        self.logger.error(message)


def calculate_priority_score(task: Dict) -> float:
    """Calculate priority score for task.
    
    Higher score = higher priority.
    Factors: Priority level, due date, blockers, dependencies, energy level
    
    Args:
        task: Notion page object
        
    Returns:
        Priority score (0-100)
    """
    props = task.get("properties", {})
    score = 0.0
    
    # Base priority (0-40 points)
    priority_map = {
        "Critical": 40,
        "High": 30,
        "Medium": 20,
        "Low": 10,
        "Very Low": 5
    }
    priority = get_select_value(props.get("Priority"))
    score += priority_map.get(priority, 15)
    
    # Due date urgency (0-25 points)
    due_date = get_date_value(props.get("Due Date"))
    if due_date:
        days_until = (due_date - datetime.now()).days
        if days_until < 0:  # Overdue
            score += 25
        elif days_until == 0:  # Due today
            score += 20
        elif days_until <= 2:  # Due within 2 days
            score += 15
        elif days_until <= 7:  # Due this week
            score += 10
        else:
            score += 5
    
    # Blockers (0-15 points)
    blockers = get_multi_select_value(props.get("Blockers"))
    if not blockers or len(blockers) == 0:
        score += 15  # No blockers = good!
    
    # Dependencies (0-10 points)
    # Tasks that unblock others get bonus
    dependencies = get_relation_count(props.get("Blocks"))
    if dependencies > 0:
        score += min(10, dependencies * 3)
    
    # Energy level match (0-10 points)
    # This would be enhanced with time-of-day matching
    energy = get_select_value(props.get("Energy"))
    if energy in ["Medium", "Low"]:
        score += 10  # Easier tasks get slight boost for momentum
    
    return min(100, score)


def get_select_value(prop: Optional[Dict]) -> Optional[str]:
    """Extract value from Notion select property."""
    if not prop or prop.get("type") != "select":
        return None
    select = prop.get("select")
    return select.get("name") if select else None


def get_multi_select_value(prop: Optional[Dict]) -> List[str]:
    """Extract values from Notion multi-select property."""
    if not prop or prop.get("type") != "multi_select":
        return []
    return [item["name"] for item in prop.get("multi_select", [])]


def get_date_value(prop: Optional[Dict]) -> Optional[datetime]:
    """Extract datetime from Notion date property."""
    if not prop or prop.get("type") != "date":
        return None
    date_obj = prop.get("date")
    if not date_obj:
        return None
    
    date_str = date_obj.get("start")
    if not date_str:
        return None
    
    try:
        return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


def get_number_value(prop: Optional[Dict]) -> Optional[float]:
    """Extract number from Notion number property."""
    if not prop or prop.get("type") != "number":
        return None
    return prop.get("number")


def get_relation_count(prop: Optional[Dict]) -> int:
    """Get count of relations."""
    if not prop or prop.get("type") != "relation":
        return 0
    return len(prop.get("relation", []))


def get_title_value(prop: Optional[Dict]) -> Optional[str]:
    """Extract text from Notion title property."""
    if not prop or prop.get("type") != "title":
        return None
    title_array = prop.get("title", [])
    if not title_array:
        return None
    return "".join(item.get("plain_text", "") for item in title_array)


def get_rich_text_value(prop: Optional[Dict]) -> Optional[str]:
    """Extract text from Notion rich_text property."""
    if not prop or prop.get("type") != "rich_text":
        return None
    text_array = prop.get("rich_text", [])
    if not text_array:
        return None
    return "".join(item.get("plain_text", "") for item in text_array)


def parse_notion_date(date_str: Optional[str]) -> Optional[datetime]:
    """Parse Notion date string to datetime."""
    if not date_str:
        return None
    
    try:
        return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


def format_task_display(task: Dict) -> str:
    """Format task for display in CLI.
    
    Args:
        task: Notion page object
        
    Returns:
        Formatted string for display
    """
    props = task.get("properties", {})
    
    task_id = get_rich_text_value(props.get("Task ID", {}))
    title = get_title_value(props.get("Task Name", {}))
    priority = get_select_value(props.get("Priority", {}))
    category = get_select_value(props.get("Category", {}))
    est_hours = get_number_value(props.get("Est. Hours", {}))
    
    # Priority emoji
    priority_emoji = {
        "Critical": "🔴",
        "High": "🟠",
        "Medium": "🟡",
        "Low": "🟢",
        "Very Low": "⚪"
    }.get(priority, "⚪")
    
    parts = []
    if task_id:
        parts.append(f"[{task_id}]")
    if title:
        parts.append(title)
    if priority:
        parts.append(f"{priority_emoji} {priority}")
    if category:
        parts.append(f"({category})")
    if est_hours:
        parts.append(f"{est_hours}h")
    
    return " ".join(parts)


def is_peak_focus_time(medication_config: Dict) -> bool:
    """Check if current time is in peak focus window.
    
    Args:
        medication_config: Dict with peak_start and peak_end times (HH:MM format)
        
    Returns:
        True if currently in peak window
    """
    now = datetime.now().time()
    
    try:
        peak_start = dt_time.fromisoformat(medication_config.get("peak_start", "10:00"))
        peak_end = dt_time.fromisoformat(medication_config.get("peak_end", "14:00"))
        
        return peak_start <= now <= peak_end
    except ValueError:
        return False


def format_duration(seconds: float) -> str:
    """Format duration in seconds to human readable string."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        return f"{seconds/60:.1f}m"
    else:
        return f"{seconds/3600:.1f}h"


def create_notion_select(value: str) -> Dict:
    """Create Notion select property value."""
    return {"select": {"name": value}}


def create_notion_multi_select(values: List[str]) -> Dict:
    """Create Notion multi-select property value."""
    return {"multi_select": [{"name": v} for v in values]}


def create_notion_number(value: float) -> Dict:
    """Create Notion number property value."""
    return {"number": value}


def create_notion_date(date: datetime, include_time: bool = False) -> Dict:
    """Create Notion date property value."""
    if include_time:
        date_str = date.isoformat()
    else:
        date_str = date.date().isoformat()
    
    return {"date": {"start": date_str}}


def create_notion_rich_text(text: str) -> Dict:
    """Create Notion rich_text property value."""
    return {"rich_text": [{"text": {"content": text}}]}
