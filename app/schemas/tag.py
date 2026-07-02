from pydantic import BaseModel, ConfigDict, Field


class TagBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str = Field(min_length=1, max_length=100)


class TagResponse(TagBase):
    id: int
