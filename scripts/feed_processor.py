# feed_processor.py
import logging
from typing import Dict, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select
from database_manager import Post, Reply


class FeedProcessor:
    """Process and store Bluesky feed data"""

    def __init__(self, client, db_manager):
        self.client = client
        self.db_manager = db_manager

    def process_feed(self):
        """Process the author's feed and store posts and replies"""
        feed = self.client.get_author_feed()
        if not feed:
            logging.warning("No feed items returned")
            return

        logging.info(f"Processing {len(feed)} feed items")

        with self.db_manager.get_session() as session:
            for idx, feed_item in enumerate(reversed(feed), 1):
                try:
                    self._process_feed_item(session, feed_item, idx, len(feed))
                    session.commit()
                except Exception as e:
                    logging.error(
                        f"Error processing feed item: {str(e)}", exc_info=True
                    )
                    session.rollback()
                    continue

    def _get_existing_post(self, session: Session, post_id: str) -> Optional[Post]:
        """Check if post already exists and return it if found"""
        Post = self.db_manager.Post  # Get Post model from db_manager
        stmt = select(Post).where(Post.post_id == post_id)
        return session.scalar(stmt)

    def _get_existing_reply(self, session: Session, reply_id: str) -> Optional[Reply]:
        """Check if reply already exists and return it if found"""
        Reply = self.db_manager.Reply  # Get Reply model from db_manager
        stmt = select(Reply).where(Reply.reply_id == reply_id)
        return session.scalar(stmt)

    def _process_feed_item(
        self, session: Session, feed_item: Dict, idx: int, total: int
    ):
        """Process individual feed item and its replies"""
        post = feed_item.get("post", {})
        if not post:
            logging.warning("Empty post object in feed item")
            return

        post_id = post.get("uri")
        timestamp_str = post.get("indexedAt")

        if not (post_id and timestamp_str):
            logging.warning("Missing required post data")
            return

        logging.info(f"Processing post {idx}/{total} (id: {post_id})")

        try:
            timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))

            # Check if post already exists
            existing_post = self._get_existing_post(session, post_id)

            Post = self.db_manager.Post  # Get Post model from db_manager
            if existing_post:
                logging.debug(f"Post {post_id} already exists, updating if needed")
                existing_post.timestamp = timestamp
                existing_post.content = post.get("record", {})
            else:
                # Create new post
                db_post = Post(
                    post_id=post_id, timestamp=timestamp, content=post.get("record", {})
                )
                session.add(db_post)

            # Process replies
            self._process_replies(session, post_id)

        except Exception as e:
            logging.error(f"Error processing post {post_id}: {str(e)}", exc_info=True)
            raise

    def _process_replies(self, session: Session, post_id: str):
        """Process and store replies for a post"""
        replies = self.client.get_post_replies(post_id)
        if replies:
            logging.info(f"Processing {len(replies)} replies for post {post_id}")
            for reply in replies:
                try:
                    self._save_reply(session, post_id, reply)
                except Exception as e:
                    logging.error(
                        f"Error processing reply for post {post_id}: {str(e)}",
                        exc_info=True,
                    )
                    continue

    def _save_reply(self, session: Session, post_id: str, reply: Dict):
        """Save individual reply to database"""
        reply_post = reply.get("post", {})
        reply_id = reply_post.get("uri")
        reply_timestamp = reply_post.get("indexedAt")

        if not (reply_id and reply_timestamp):
            logging.warning("Missing required reply data")
            return

        try:
            # Check if reply already exists
            existing_reply = self._get_existing_reply(session, reply_id)

            Reply = self.db_manager.Reply  # Get Reply model from db_manager
            timestamp = datetime.fromisoformat(reply_timestamp.replace("Z", "+00:00"))

            if existing_reply:
                logging.debug(f"Reply {reply_id} already exists, updating if needed")
                existing_reply.timestamp = timestamp
                existing_reply.content = reply_post.get("record", {})
            else:
                # Create new reply
                db_reply = Reply(
                    post_id=post_id,
                    reply_id=reply_id,
                    timestamp=timestamp,
                    content=reply_post.get("record", {}),
                )
                session.add(db_reply)

        except Exception as e:
            logging.error(f"Error saving reply {reply_id}: {str(e)}", exc_info=True)
            raise
