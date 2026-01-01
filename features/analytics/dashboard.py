"""Dashboard analytics for project health and velocity."""

from typing import Dict, List, Tuple
from datetime import datetime, timedelta
from collections import defaultdict

from core import NotionAPI, Logger
from core.utils import (
    get_select_value,
    get_number_value,
    get_date_value,
    get_title_value
)


class DashboardAnalytics:
    """Comprehensive dashboard analytics for Notion tasks."""
    
    def __init__(self, api: NotionAPI):
        """Initialize dashboard analytics.
        
        Args:
            api: NotionAPI instance
        """
        self.api = api
        self.logger = Logger("DashboardAnalytics")
    
    def get_project_health(self) -> Dict:
        """Calculate overall project health score.
        
        Returns:
            Dict with health score and breakdown
        """
        self.logger.info("Calculating project health...")
        
        tasks = self.api.query_database()
        
        if not tasks:
            return {
                "score": 0,
                "status": "No Data",
                "breakdown": {}
            }
        
        total = len(tasks)
        
        # Count by status
        status_counts = defaultdict(int)
        priority_counts = defaultdict(int)
        blocked_count = 0
        overdue_count = 0
        
        for task in tasks:
            props = task.get("properties", {})
            
            # Status
            status = get_select_value(props.get("Status"))
            if status:
                status_counts[status] += 1
            
            # Priority
            priority = get_select_value(props.get("Priority"))
            if priority:
                priority_counts[priority] += 1
            
            # Blockers
            blockers = props.get("Blockers", {}).get("multi_select", [])
            if blockers:
                blocked_count += 1
            
            # Overdue
            due_date = get_date_value(props.get("Due Date"))
            if due_date and due_date < datetime.now() and status != "Complete":
                overdue_count += 1
        
        # Calculate health score (0-100)
        score = 100
        
        # Penalty for blockers (up to -20)
        blocked_ratio = blocked_count / total if total > 0 else 0
        score -= blocked_ratio * 20
        
        # Penalty for overdue tasks (up to -30)
        overdue_ratio = overdue_count / total if total > 0 else 0
        score -= overdue_ratio * 30
        
        # Bonus for completion (up to +10)
        completed_ratio = status_counts.get("Complete", 0) / total if total > 0 else 0
        score += completed_ratio * 10
        
        # Penalty for critical tasks not started (up to -15)
        critical_not_started = sum(
            1 for t in tasks
            if get_select_value(t.get("properties", {}).get("Priority")) == "Critical"
            and get_select_value(t.get("properties", {}).get("Status")) == "Not Started"
        )
        score -= min(critical_not_started * 5, 15)
        
        score = max(0, min(100, score))
        
        # Determine status
        if score >= 90:
            status = "Excellent"
        elif score >= 75:
            status = "Good"
        elif score >= 60:
            status = "Fair"
        else:
            status = "Needs Attention"
        
        return {
            "score": round(score, 1),
            "status": status,
            "breakdown": {
                "total_tasks": total,
                "completed": status_counts.get("Complete", 0),
                "in_progress": status_counts.get("In Progress", 0),
                "not_started": status_counts.get("Not Started", 0),
                "blocked": blocked_count,
                "overdue": overdue_count,
                "critical_pending": critical_not_started
            }
        }
    
    def calculate_velocity(self, weeks: int = 4) -> Dict:
        """Calculate task completion velocity.
        
        Args:
            weeks: Number of weeks to analyze
            
        Returns:
            Dict with velocity metrics
        """
        self.logger.info(f"Calculating velocity for last {weeks} weeks...")
        
        # Get completed tasks from last N weeks
        cutoff_date = datetime.now() - timedelta(weeks=weeks)
        
        tasks = self.api.query_database(
            filter_dict={
                "property": "Status",
                "select": {"equals": "Complete"}
            }
        )
        
        # Filter by completion date
        recent_tasks = []
        total_hours = 0
        
        for task in tasks:
            props = task.get("properties", {})
            
            # Check if completed recently (using last_edited_time as proxy)
            last_edited = task.get("last_edited_time")
            if last_edited:
                edited_date = datetime.fromisoformat(last_edited.replace("Z", "+00:00"))
                if edited_date >= cutoff_date:
                    recent_tasks.append(task)
                    
                    # Add up actual hours
                    actual_hours = get_number_value(props.get("Actual Hours"))
                    if actual_hours:
                        total_hours += actual_hours
        
        # Calculate metrics
        tasks_per_week = len(recent_tasks) / weeks if weeks > 0 else 0
        hours_per_week = total_hours / weeks if weeks > 0 else 0
        
        return {
            "weeks_analyzed": weeks,
            "completed_tasks": len(recent_tasks),
            "total_hours": round(total_hours, 1),
            "tasks_per_week": round(tasks_per_week, 1),
            "hours_per_week": round(hours_per_week, 1),
            "avg_hours_per_task": round(total_hours / len(recent_tasks), 1) if recent_tasks else 0
        }
    
    def get_sprint_progress(self, sprint_name: str) -> Dict:
        """Get progress for specific sprint.
        
        Args:
            sprint_name: Name of sprint
            
        Returns:
            Dict with sprint progress
        """
        self.logger.info(f"Getting progress for sprint: {sprint_name}")
        
        # Query tasks for this sprint
        tasks = self.api.query_database(
            filter_dict={
                "property": "Sprint",
                "select": {"equals": sprint_name}
            }
        )
        
        if not tasks:
            return {
                "sprint": sprint_name,
                "total_tasks": 0,
                "message": "No tasks found for this sprint"
            }
        
        total = len(tasks)
        completed = 0
        in_progress = 0
        total_estimated = 0
        total_actual = 0
        
        for task in tasks:
            props = task.get("properties", {})
            
            status = get_select_value(props.get("Status"))
            if status == "Complete":
                completed += 1
            elif status == "In Progress":
                in_progress += 1
            
            est_hours = get_number_value(props.get("Est. Hours"))
            if est_hours:
                total_estimated += est_hours
            
            actual_hours = get_number_value(props.get("Actual Hours"))
            if actual_hours:
                total_actual += actual_hours
        
        completion_rate = (completed / total * 100) if total > 0 else 0
        
        return {
            "sprint": sprint_name,
            "total_tasks": total,
            "completed": completed,
            "in_progress": in_progress,
            "not_started": total - completed - in_progress,
            "completion_rate": round(completion_rate, 1),
            "estimated_hours": round(total_estimated, 1),
            "actual_hours": round(total_actual, 1),
            "hours_remaining": round(total_estimated - total_actual, 1)
        }
    
    def get_capacity_analysis(self, sprint_name: str, capacity_hours: float = 40) -> Dict:
        """Analyze sprint capacity vs workload.
        
        Args:
            sprint_name: Name of sprint
            capacity_hours: Available capacity in hours
            
        Returns:
            Dict with capacity analysis
        """
        progress = self.get_sprint_progress(sprint_name)
        
        estimated = progress.get("estimated_hours", 0)
        utilization = (estimated / capacity_hours * 100) if capacity_hours > 0 else 0
        
        if utilization > 120:
            status = "Severely Overloaded"
        elif utilization > 100:
            status = "Overloaded"
        elif utilization > 85:
            status = "At Capacity"
        elif utilization > 60:
            status = "Well Balanced"
        else:
            status = "Under Capacity"
        
        return {
            "sprint": sprint_name,
            "capacity_hours": capacity_hours,
            "estimated_hours": estimated,
            "utilization_percent": round(utilization, 1),
            "status": status,
            "hours_over_under": round(estimated - capacity_hours, 1)
        }
