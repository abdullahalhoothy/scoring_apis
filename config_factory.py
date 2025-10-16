import json
from dataclasses import dataclass
from pathlib import Path

@dataclass
class ApiConfig:
    secrets_dir: str = "secrets"
    database_url: str = ""
    
    # API endpoints
    fetch_dataset: str = "/demographics/score"
    competition_score: str = "/competition/score"
    complementary_score: str = "/complementary/score"
    income_score: str = "/income/score"
    traffic_score: str = "/traffic/score"
    
    # External traffic API configuration
    traffic_api_base_url: str = "http://49.12.190.229:8000"
    
    # External API configuration
    external_api_base_url: str = "http://37.27.195.216:8000"

    @classmethod
    def load(cls, secrets_dir: str = "secrets"):
        config = cls(secrets_dir=secrets_dir)
        
        config_file = Path(secrets_dir) / "postgres_db.json"
        if config_file.exists():
            data = json.loads(config_file.read_text(encoding="utf-8"))
            config.database_url = data.get("DATABASE_URL", "")

        return config

CONF = ApiConfig.load()
