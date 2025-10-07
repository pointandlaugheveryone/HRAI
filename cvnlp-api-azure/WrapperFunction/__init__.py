import azure.functions as func
import spacy
from fastapi import FastAPI
from spacy.tokens import Doc
from models import RequestModel, ResponseModel


app = FastAPI()

@app.post("/post/", response_model=ResponseModel)
def text_post(query: RequestModel):
    nlp = spacy.load(query.request_nlp_model)

    if 'entity_ruler' not in nlp.pipe_names:
        ruler = nlp.add_pipe("entity_ruler").from_disk('patterns.jsonl') # type: ignore 

    response_body = []
    input = (text for text in query.docs)
    for input_doc in nlp.pipe(input):
        response_body.append(process_output(input_doc))
    return {"result": response_body}


def process_output(doc: Doc):
    ents = [
        {
            "start": ent.start_char,
            "end": ent.end_char,
            "label": ent.label_,
            "content": ent.text,
        }
        for ent in doc.ents
    ]
    return {"text": doc.text, "ents": ents}