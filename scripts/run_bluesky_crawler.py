import time
from pathlib import Path
import logging
from bluesky_client import BlueskyClient, BlueskyConfig
from database_manager import DatabaseManager
import os
from dotenv import load_dotenv
import sys
from feed_processor import FeedProcessor

load_dotenv()


def setup_logging():
    """Configure logging settings"""
    LOG_DIR = Path(os.getenv("LOG_DIRECTORY", "logs"))
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [BLUESKY] %(levelname)s: %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(f"{LOG_DIR}/bluesky.log"),
        ],
    )


def main():
    """Main execution function"""
    setup_logging()
    start = time.perf_counter()

    try:
        # Initialize components
        config = BlueskyConfig(
            actor=os.getenv("BLUESKY_ACTOR"),
            posts_limit=int(os.getenv("POSTS_TO_GRAB", "5")),
        )

        client = BlueskyClient(config)
        db_manager = DatabaseManager(
            db_path=str(Path(os.getenv("DATABASE_DIRECTORY", "data")) / "bluesky.db")
        )
        db_manager.initialize()

        # Process feed
        processor = FeedProcessor(client, db_manager)
        processor.process_feed()

        stop = time.perf_counter()
        logging.info(f"Completed in {stop - start:0.4f} seconds")

    except Exception as e:
        logging.critical(f"Fatal error in main execution: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
