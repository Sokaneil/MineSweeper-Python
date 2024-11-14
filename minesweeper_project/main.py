#!/usr/bin/env python3

import sys
import logging
from datetime import datetime
import os
from gui import MinesweeperGUI


def setup_logging():
    """Setup basic logging configuration."""
    if not os.path.exists('logs'):
        os.makedirs('logs')

    log_file = f'logs/minesweeper_{datetime.now().strftime("%Y%m%d")}.log'
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )


def main():
    """Main entry point for the Minesweeper game."""
    try:
        setup_logging()
        logging.info("Starting Minesweeper game")

        game = MinesweeperGUI()
        logging.info("Game initialized successfully")

        game.run()

    except Exception as e:
        logging.error(f"Game crashed: {str(e)}", exc_info=True)
        sys.exit(1)
    finally:
        logging.info("Game session ended")


if __name__ == "__main__":
    main()