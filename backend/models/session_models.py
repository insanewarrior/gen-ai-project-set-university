from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class SetEntry(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    set_number: int
    weight: float | None = None
    reps: int | None = None
    rpe: float | None = None


class ExerciseEntry(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    exercise_id: str
    exercise_name: str
    sport_type: str
    sets: list[SetEntry]


class SessionCreate(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    session_date: str
    sport: str
    exercises: list[ExerciseEntry] = Field(..., min_length=1)
    notes: str | None = Field(None, max_length=500)


class SessionResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    session_id: str
    session_date: str
    sport: str
    exercises: list[ExerciseEntry]
    notes: str | None = None
    created_at: str
