from typing import List
from uuid import uuid4
import random
from pydantic import BaseModel

class Data(BaseModel):
    text: str

    @classmethod
    def create(cls, text: str) -> "Data":
        return cls(text=text)


class Value(BaseModel):
    start: int
    end: int
    score: float
    text: str
    labels: List[str]

    @classmethod
    def create(cls, start: int, end: int, label: str, value: str) -> "Value":
        return cls(
            start=start,
            end=end,
            score=random.uniform(0.5, 0.9),
            text=value,
            labels=[label],
        )


class Result(BaseModel):
    id: str
    from_name: str = "label"
    to_name: str = "text"
    type: str = "labels"
    value: Value

    @classmethod
    def create(cls, start: int, end: int, label: str, value: str) -> "Result":
        return cls(
            id=str(uuid4()),
            value=Value.create(start, end, label, value),
        )


class Prediction(BaseModel):
    model_version: str
    score: float
    result: List[Result]

    @classmethod
    def create(cls, result: List[Result]) -> "Prediction":
        return cls(
            model_version="0.1",
            score=random.uniform(0.5, 0.9),
            result=result,
        )


class Document(BaseModel):
    data: Data
    predictions: List[Prediction]

    @classmethod
    def create(cls, data: str, results: List[Result]) -> "Document":
        return cls(
            data=Data.create(data),
            predictions=[Prediction.create(results)],
        )