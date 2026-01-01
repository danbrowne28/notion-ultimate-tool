"""Interactive CLI menu for Notion Ultimate Tool."""

import sys
from typing import Optional

from core import Config, NotionAPI, Logger
from .ui import UI, print_banner, print_table, colors


class MainMenu:
    """Main interactive menu for Notion Ultimate Tool."""
    
    def __init__(self, api: NotionAPI, config: Config):
        """Initialize main menu.
        
        Args:
            api: NotionAPI instance
            config: Config instance
        """
        self.api = api
        self.config = config
        self.ui = UI()
        self.logger = Logger("MainMenu")
    
    def run(self):
        """Run main menu loop."""
        while True:
            self.display_main_menu()
            choice = self.ui.get_input("Enter command [1-9, 0 for more]: ")
            
            if not self.handle_main_menu_choice(choice):
                break
    
    def display_main_menu(self):
        """Display main menu."""
        self.ui.clear_screen()
        print_banner()
        
        # TODO: Get real health score from analytics
        health_score = 87
        health_bar = self._create_progress_bar(health_score, 100, width=20)
        health_status = self._get_health_status(health_score)
        
        print(f"\n{colors.BOLD}📊 PROJECT HEALTH:{colors.END} {health_score}/100 {health_bar} [{health_status}]")
        
        print(f"\n{colors.BOLD}{colors.CYAN}⚡ QUICK ACTIONS{colors.END}")
        print(f"{colors.GREEN}[1]{colors.END} Start Next Task        {colors.GREEN}[6]{colors.END} Daily Standup")
        print(f"{colors.GREEN}[2]{colors.END} Complete Current Task  {colors.GREEN}[7]{colors.END} Sprint Dashboard")
        print(f"{colors.GREEN}[3]{colors.END} View Dashboard         {colors.GREEN}[8]{colors.END} AI Workflow (Auto)")
        print(f"{colors.GREEN}[4]{colors.END} Generate AI Prompt     {colors.GREEN}[9]{colors.END} Bulk Operations")
        print(f"{colors.GREEN}[5]{colors.END} Planning & Scheduling  {colors.GREEN}[0]{colors.END} More Features...")
        
        # TODO: Get real task data
        print(f"\n{colors.BOLD}📈 AT A GLANCE{colors.END}")
        print(f"• Next Task: {colors.YELLOW}Loading...{colors.END}")
        print(f"• Sprint Progress: {colors.YELLOW}Loading...{colors.END}")
        print(f"• Velocity: {colors.YELLOW}Loading...{colors.END}")
        
        print(f"\n{colors.BOLD}💡 SMART RECOMMENDATIONS{colors.END}")
        print(f"{colors.CYAN}✨ Loading recommendations...{colors.END}")
        print()
    
    def handle_main_menu_choice(self, choice: str) -> bool:
        """Handle main menu choice.
        
        Args:
            choice: User's menu choice
            
        Returns:
            True to continue, False to exit
        """
        choice = choice.strip()
        
        if choice == "1":
            self.start_next_task()
        elif choice == "2":
            self.complete_current_task()
        elif choice == "3":
            self.view_dashboard()
        elif choice == "4":
            self.generate_ai_prompt()
        elif choice == "5":
            self.planning_menu()
        elif choice == "6":
            self.daily_standup()
        elif choice == "7":
            self.sprint_dashboard()
        elif choice == "8":
            self.ai_workflow()
        elif choice == "9":
            self.bulk_operations_menu()
        elif choice == "0":
            self.more_features_menu()
        elif choice.lower() in ["q", "quit", "exit"]:
            return False
        else:
            self.ui.print_error("Invalid choice. Please try again.")
            self.ui.pause()
        
        return True
    
    def start_next_task(self):
        """Start next priority task."""
        self.ui.clear_screen()
        print(f"{colors.BOLD}{colors.CYAN}🚀 Starting Next Task{colors.END}\n")
        
        try:
            # Query tasks with status "Not Started"
            tasks = self.api.query_database(
                filter_dict={
                    "property": "Status",
                    "select": {"equals": "Not Started"}
                }
            )
            
            if not tasks:
                self.ui.print_warning("No tasks found with status 'Not Started'")
                self.ui.pause()
                return
            
            # TODO: Calculate priority scores and get highest
            task = tasks[0]  # For now, just take first
            
            from core.utils import format_task_display
            print(f"Next task: {format_task_display(task)}")
            
            if self.ui.confirm("\nStart this task?"):
                # Update status to "In Progress"
                self.api.update_page(
                    task["id"],
                    {"Status": {"select": {"name": "In Progress"}}}
                )
                self.ui.print_success("Task started! Status updated to 'In Progress'")
            
        except Exception as e:
            self.ui.print_error(f"Error: {e}")
        
        self.ui.pause()
    
    def complete_current_task(self):
        """Complete current task."""
        self.ui.clear_screen()
        print(f"{colors.BOLD}{colors.GREEN}✅ Complete Current Task{colors.END}\n")
        
        try:
            # Query tasks with status "In Progress"
            tasks = self.api.query_database(
                filter_dict={
                    "property": "Status",
                    "select": {"equals": "In Progress"}
                }
            )
            
            if not tasks:
                self.ui.print_warning("No tasks found with status 'In Progress'")
                self.ui.pause()
                return
            
            # Show all in-progress tasks
            print(f"{colors.BOLD}In Progress Tasks:{colors.END}\n")
            from core.utils import format_task_display
            for i, task in enumerate(tasks, 1):
                print(f"{i}. {format_task_display(task)}")
            
            choice = self.ui.get_input(f"\nSelect task to complete [1-{len(tasks)}]: ")
            
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(tasks):
                    task = tasks[idx]
                    
                    # Get actual hours
                    actual_hours = self.ui.get_input("Actual hours spent (optional): ", required=False)
                    
                    # Update properties
                    updates = {
                        "Status": {"select": {"name": "Complete"}}
                    }
                    
                    if actual_hours:
                        try:
                            updates["Actual Hours"] = {"number": float(actual_hours)}
                        except ValueError:
                            pass
                    
                    self.api.update_page(task["id"], updates)
                    self.ui.print_success("Task completed successfully!")
                else:
                    self.ui.print_error("Invalid task number")
            except ValueError:
                self.ui.print_error("Invalid input")
        
        except Exception as e:
            self.ui.print_error(f"Error: {e}")
        
        self.ui.pause()
    
    def view_dashboard(self):
        """View project dashboard."""
        self.ui.clear_screen()
        print(f"{colors.BOLD}{colors.CYAN}📊 Project Dashboard{colors.END}\n")
        
        try:
            # Get all tasks
            tasks = self.api.query_database()
            
            # Calculate statistics
            total = len(tasks)
            statuses = {}
            
            for task in tasks:
                status = task.get("properties", {}).get("Status", {}).get("select", {}).get("name", "Unknown")
                statuses[status] = statuses.get(status, 0) + 1
            
            # Display statistics
            print(f"{colors.BOLD}Task Statistics:{colors.END}")
            print(f"Total Tasks: {total}\n")
            
            for status, count in sorted(statuses.items()):
                percentage = (count / total * 100) if total > 0 else 0
                bar = self._create_progress_bar(count, total, width=20)
                print(f"{status:15} {count:3} {bar} {percentage:5.1f}%")
        
        except Exception as e:
            self.ui.print_error(f"Error: {e}")
        
        self.ui.pause()
    
    def generate_ai_prompt(self):
        """Generate AI prompt for task."""
        self.ui.clear_screen()
        print(f"{colors.BOLD}{colors.CYAN}🤖 AI Prompt Generator{colors.END}\n")
        self.ui.print_info("This feature will be implemented in Phase 2")
        self.ui.pause()
    
    def planning_menu(self):
        """Planning & scheduling menu."""
        self.ui.clear_screen()
        print(f"{colors.BOLD}{colors.CYAN}📅 Planning & Scheduling{colors.END}\n")
        self.ui.print_info("This feature will be implemented in Phase 5")
        self.ui.pause()
    
    def daily_standup(self):
        """Generate daily standup."""
        self.ui.clear_screen()
        print(f"{colors.BOLD}{colors.CYAN}📋 Daily Standup{colors.END}\n")
        self.ui.print_info("This feature will be implemented in Phase 5")
        self.ui.pause()
    
    def sprint_dashboard(self):
        """View sprint dashboard."""
        self.ui.clear_screen()
        print(f"{colors.BOLD}{colors.CYAN}🏃 Sprint Dashboard{colors.END}\n")
        self.ui.print_info("This feature will be implemented in Phase 2")
        self.ui.pause()
    
    def ai_workflow(self):
        """Start continuous AI workflow."""
        self.ui.clear_screen()
        print(f"{colors.BOLD}{colors.CYAN}🤖 Continuous AI Workflow{colors.END}\n")
        self.ui.print_info("This feature will be implemented in Phase 9 (MCP Integration)")
        self.ui.pause()
    
    def bulk_operations_menu(self):
        """Bulk operations menu."""
        self.ui.clear_screen()
        print(f"{colors.BOLD}{colors.CYAN}⚡ Bulk Operations{colors.END}\n")
        self.ui.print_info("This feature will be implemented in Phase 3")
        self.ui.pause()
    
    def more_features_menu(self):
        """More features menu."""
        self.ui.clear_screen()
        print(f"{colors.BOLD}{colors.CYAN}💎 More Features{colors.END}\n")
        self.ui.print_info("Additional features will be added in upcoming phases")
        self.ui.pause()
    
    @staticmethod
    def _create_progress_bar(value: float, max_value: float, width: int = 20) -> str:
        """Create progress bar string."""
        if max_value == 0:
            return "░" * width
        
        filled = int((value / max_value) * width)
        empty = width - filled
        return "█" * filled + "░" * empty
    
    @staticmethod
    def _get_health_status(score: float) -> str:
        """Get health status label from score."""
        if score >= 90:
            return f"{colors.GREEN}Excellent{colors.END}"
        elif score >= 75:
            return f"{colors.CYAN}Good{colors.END}"
        elif score >= 60:
            return f"{colors.YELLOW}Fair{colors.END}"
        else:
            return f"{colors.RED}Needs Attention{colors.END}"
