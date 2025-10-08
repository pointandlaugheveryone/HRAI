import json
from pathlib import Path
from typing import List, Dict, Any
import random

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse

import spacy
from spacy.tokens import DocBin
from spacy.training import Example


app = FastAPI()

BASE_DIR = Path(__file__).parent
MODEL_DIR = BASE_DIR / "outputs" / "model-best"
nlp = None
LOAD_ERROR = None

@app.on_event("startup")
def load_local_model():
    global nlp, LOAD_ERROR
    try:
        nlp = spacy.load(str(MODEL_DIR))
        ruler = nlp.add_pipe("entity_ruler").from_disk("patterns.jsonl") # type: ignore
        LOAD_ERROR = None
    except Exception as e:
        nlp = None
        LOAD_ERROR = str(e)


def render_html(text: str, ents: List[Dict[str, Any]]) -> str:
    colors = {"Hard Skill": "#cfffdc", "Soft Skill": "#68ba7f", "Certification": "#253d2c"}
    pieces = []
    last = 0
    ents_sorted = sorted(ents, key=lambda e: e["start"])
    for e in ents_sorted:
        start, end, label = e["start"], e["end"], e["label"]
        pieces.append(text[last:start])
        color = colors.get(label, "#ffd966")
        pieces.append(f'<mark style="background:{color};padding:0 2px;border-radius:3px">{text[start:end]}</mark>')
        last = end
    pieces.append(text[last:])
    return "<div style='font-family:system-ui, -apple-system, Segoe UI, Roboto, sans-serif;line-height:1.5'>" + "".join(pieces) + "</div>"

@app.get("/demo", response_class=JSONResponse)
def demo():
    if nlp is None:
        raise HTTPException(status_code=500, detail=f"Model failed to load: {LOAD_ERROR}")

    # random file for demo
    data_dir = "/home/ronji/repos/CarP/NER-spacy-CNN/DATA/data_en"
    i = random.randrange(2450) 
    filename = f"{i+1}.txt"
    sample-path = f"{data_dir}/{filename}"


    text = sample_path.read_text(encoding="utf-8")
    doc = nlp(text)

    ents = [{"label": e.label_, "start": e.start_char, "end": e.end_char, "text": e.text} for e in doc.ents]
    html = render_html(text, ents)

    return {"text": text, "entities": ents, "html": html, "test_file": filename}

@app.get("/render", response_class=HTMLResponse)
def render():
    """
    Same as /demo but returns the rendered HTML directly for easy demo in a browser.
    """
    resp = demo()
    html = f"<h2>Model demo</h2>{resp['html']}<hr><pre style='white-space:pre-wrap'>{resp['text']}</pre>"
    return html

@app.get("/evaluate", response_class=JSONResponse)
def evaluate():
    """
    Evaluate the loaded model against a test.spacy DocBin located only in the same directory.
    """
    if nlp is None:
        raise HTTPException(status_code=500, detail=f"Model failed to load: {LOAD_ERROR}")

    # Only accept a local test.spacy in this project directory
    test_path = "/home/ronji/repos/CarP/NER-spacy-CNN/train.spacy"
    doc_bin = DocBin().from_disk(str(test_path))
    gold_docs = list(doc_bin.get_docs(nlp.vocab))

    examples: List[Example] = []
    for gold in gold_docs:
        pred = nlp(gold.text)
        examples.append(Example(pred, gold))

    results = nlp.evaluate(examples)

    # make results JSON serializable
    ents_per_type = results.get("ents_per_type", {})
    ents_per_type_clean = {k: {kk: float(vv) for kk, vv in d.items()} for k, d in ents_per_type.items()}

    payload = {
        "precision": float(results.get("ents_p", 0.0)),
        "recall": float(results.get("ents_r", 0.0)),
        "f1": float(results.get("ents_f", 0.0)),
        "ents_per_type": ents_per_type_clean,
        "n_examples": len(examples),
        "test_path": str(test_path),
    }
    return payload