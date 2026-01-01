#!/usr/bin/env python3
"""Main entry point for Notion Ultimate Tool."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core import Config, NotionAPI, Logger
from cli.menu import MainMenu


def main():
    """Main entry point."""
    logger = Logger("NotionTool")
    
    try:
        # Initialize configuration
        logger.info("Initializing Notion Ultimate Tool v2.0...")
        config = Config()
        
        # Initialize Notion API
        api = NotionAPI(config)
        
        # Start CLI menu
        menu = MainMenu(api, config)
        menu.run()
        
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        logger.error("Please ensure NOTION_TOKEN and DATABASE_ID are set in your .env file")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("\n\nExiting... Goodbye!")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
