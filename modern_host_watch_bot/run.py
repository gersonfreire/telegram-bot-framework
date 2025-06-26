#!/usr/bin/env python3
"""
Simple runner script for Modern Host Watch Bot.
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def main():
    """Main entry point."""
    try:
        # Check if .env exists
        env_file = Path(__file__).parent / ".env"
        if not env_file.exists():
            print("❌ Error: .env file not found!")
            print("Please copy env.example to .env and configure it.")
            sys.exit(1)
        
        # Import and run bot
        from src.core.bot import ModernHostWatchBot
        
        bot = ModernHostWatchBot()
        
        print("🤖 Starting Modern Host Watch Bot...")
        print("Press Ctrl+C to stop")
        
        # Run bot
        import asyncio
        asyncio.run(bot.start())
        
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 