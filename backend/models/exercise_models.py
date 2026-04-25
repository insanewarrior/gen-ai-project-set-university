from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class Exercise(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    id: str
    name: str
    sport_type: str


class ExercisesData(BaseModel):
    exercises: dict[str, list[Exercise]]


class ExercisesResponse(BaseModel):
    data: ExercisesData
