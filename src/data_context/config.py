"""Configuration loader for L1 data sources."""
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class AlpacaConfig:
    api_key: str
    api_secret: str
    base_url: str = "https://paper-api.alpaca.markets"


@dataclass
class RedditConfig:
    client_id: str
    client_secret: str
    user_agent: str


@dataclass
class TwitterConfig:
    bearer_token: str


@dataclass
class BinanceConfig:
    api_key: str
    api_secret: str


@dataclass
class MongoConfig:
    uri: str
    db_name: str = "tinywindow"


def load_alpaca_config() -> AlpacaConfig:
    return AlpacaConfig(
        api_key=os.environ["ALPACA_API_KEY"],
        api_secret=os.environ["ALPACA_API_SECRET"],
        base_url=os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets"),
    )


def load_reddit_config() -> RedditConfig:
    return RedditConfig(
        client_id=os.environ["REDDIT_CLIENT_ID"],
        client_secret=os.environ["REDDIT_CLIENT_SECRET"],
        user_agent=os.environ["REDDIT_USER_AGENT"],
    )


def load_twitter_config() -> TwitterConfig:
    return TwitterConfig(bearer_token=os.environ["TWITTER_BEARER_TOKEN"])


def load_binance_config() -> BinanceConfig:
    return BinanceConfig(
        api_key=os.environ["BINANCE_API_KEY"],
        api_secret=os.environ["BINANCE_API_SECRET"],
    )


def load_mongo_config() -> MongoConfig:
    return MongoConfig(
        uri=os.environ["MONGODB_URI"],
        db_name=os.getenv("MONGODB_DB_NAME", "tinywindow"),
    )
