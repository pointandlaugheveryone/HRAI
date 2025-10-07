from pydantic import BaseModel
from typing import List, Dict, Any


class RequestModel(BaseModel):
    docs: List[str]
    request_nlp_model : str = 'cvnlp' # for future model development, currently only available


class ResponseModel(BaseModel):
    class Batch(BaseModel):
        text: str
        ents: List[Dict] = []

    result: List[Batch]