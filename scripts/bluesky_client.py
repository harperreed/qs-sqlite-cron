from dataclasses import dataclass
import logging
from typing import List, Optional, Dict
import requests
from requests.exceptions import RequestException
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter


@dataclass
class BlueskyConfig:
    """Configuration class for Bluesky client settings"""

    actor: str
    base_url: str = "https://public.api.bsky.app/xrpc"
    posts_limit: int = 5
    request_timeout: int = 10
    max_retries: int = 3
    backoff_factor: float = 0.3


class BlueskyClient:
    """Client for interacting with Bluesky API"""

    def __init__(self, config: BlueskyConfig):
        self.config = config
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """Create a requests session with retry logic"""
        session = requests.Session()
        retry_strategy = Retry(
            total=self.config.max_retries,
            backoff_factor=self.config.backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        return session

    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make HTTP request with error handling"""
        try:
            response = self.session.get(
                f"{self.config.base_url}/{endpoint}",
                params=params,
                timeout=self.config.request_timeout,
            )
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            logging.error(f"Request failed for endpoint {endpoint}: {str(e)}")
            raise

    def get_author_feed(self) -> List[Dict]:
        """Fetch posts from author's feed"""
        try:
            response = self._make_request(
                "app.bsky.feed.getAuthorFeed",
                params={"actor": self.config.actor, "limit": self.config.posts_limit},
            )
            return response.get("feed", [])
        except RequestException:
            logging.error(f"Failed to fetch feed for actor {self.config.actor}")
            return []

    def get_post_replies(self, uri: str) -> List[Dict]:
        """Fetch replies for a specific post"""
        try:
            response = self._make_request(
                "app.bsky.feed.getPostThread", params={"uri": uri}
            )
            return response.get("thread", {}).get("replies", [])
        except RequestException:
            logging.error(f"Failed to fetch replies for post {uri}")
            return []
