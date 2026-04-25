from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class QueryRequest(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    query: str = Field(..., max_length=2000)


class AnalyzeRequest(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    program: str = Field(..., max_length=2000)


class PersonalCitation(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    session_date: str
    exercise: str
    detail: str


class KnowledgeCitation(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    source: str
    principle: str


class Citations(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    personal: list[PersonalCitation]
    knowledge: list[KnowledgeCitation]


class CoachingResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    response: str
    citations: Citations
    confidence: str
    queries_remaining: int
