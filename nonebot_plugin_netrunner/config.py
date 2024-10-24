from pydantic import BaseModel

class Config(BaseModel):
    netrunner_resources_dir: str
