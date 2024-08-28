from pydantic import Extra, BaseModel
from typing import Optional


class Config(BaseModel, extra=Extra.ignore):
    oneapi_url: Optional[str] = ""
    oneapi_key: Optional[str] = ""
    oneapi_model: Optional[str] = "gpt-4o"


class ConfigError(Exception):
    pass
