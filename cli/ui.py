"""UI utilities for CLI interface."""

import os
import sys
from typing import List, Optional


class colors:
    """ANSI color codes for terminal output."""
    # Basic colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    # Bright colors
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    
    # Styles
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"


class UI:
    """UI helper class for CLI interactions."""
    
    @staticmethod
    def clear_screen():
        """Clear terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    @staticmethod
    def print_success(message: str):
        """Print success message."""
        print(f"{colors.GREEN}✓ {message}{colors.END}")
    
    @staticmethod
    def print_error(message: str):
        """Print error message."""
        print(f"{colors.RED}✗ {message}{colors.END}")
    
    @staticmethod
    def print_warning(message: str):
        """Print warning message."""
        print(f"{colors.YELLOW}⚠ {message}{colors.END}")
    
    @staticmethod
    def print_info(message: str):
        """Print info message."""
        print(f"{colors.CYAN}ℹ {message}{colors.END}")
    
    @staticmethod
    def get_input(prompt: str, required: bool = True) -> str:
        """Get user input.
        
        Args:
            prompt: Input prompt to display
            required: Whether input is required
            
        Returns:
            User input string
        """
        while True:
            try:
                value = input(f"{colors.BOLD}{prompt}{colors.END}").strip()
                if value or not required:
                    return value
                print(f"{colors.RED}This field is required{colors.END}")
            except KeyboardInterrupt:
                print("\n")
                sys.exit(0)
    
    @staticmethod
    def confirm(prompt: str, default: bool = True) -> bool:
        """Ask for yes/no confirmation.
        
        Args:
            prompt: Confirmation prompt
            default: Default value if user just presses enter
            
        Returns:
            True if confirmed, False otherwise
        """
        suffix = " [Y/n]: " if default else " [y/N]: "
        
        while True:
            response = input(f"{colors.BOLD}{prompt}{suffix}{colors.END}").strip().lower()
            
            if not response:
                return default
            
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            
            print(f"{colors.RED}Please enter 'y' or 'n'{colors.END}")
    
    @staticmethod
    def pause(message: str = "Press Enter to continue..."):
        """Pause and wait for user."""
        input(f"\n{colors.BOLD}{message}{colors.END}")


def print_banner():
    """Print application banner."""
    banner = f"""
{colors.CYAN}{colors.BOLD}
╔══════════════════════════════════════════════════════════════════╗
║                  🎯 NOTION ULTIMATE TOOL v2.0                    ║
║                    Your AI-Powered Workflow                      ║
╚══════════════════════════════════════════════════════════════════╝
{colors.END}"""
    print(banner)


def print_table(headers: List[str], rows: List[List[str]], title: Optional[str] = None):
    """Print formatted table.
    
    Args:
        headers: List of header strings
        rows: List of rows (each row is a list of strings)
        title: Optional table title
    """
    if title:
        print(f"\n{colors.BOLD}{title}{colors.END}\n")
    
    # Calculate column widths
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(str(cell)))
    
    # Print header
    header_line = " | ".join(h.ljust(w) for h, w in zip(headers, widths))
    print(f"{colors.BOLD}{header_line}{colors.END}")
    print("-" * len(header_line))
    
    # Print rows
    for row in rows:
        row_line = " | ".join(str(cell).ljust(w) for cell, w in zip(row, widths))
        print(row_line)
    
    print()
