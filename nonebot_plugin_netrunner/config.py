from pydantic import BaseModel

class Config(BaseModel):
    netrunner_resources_dir: str
    netrunner_database_master_key: str
    netrunner_database_host: str
    netrunner_database_port: int
