from pydantic import BaseConfig, BaseModel, Extra


class BasicModel(BaseModel):
    class Config(BaseConfig):
        extra = Extra.forbid  # forbid unknow fields
