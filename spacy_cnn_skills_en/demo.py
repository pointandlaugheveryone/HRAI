from typing import List, Dict, Any
import random

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

import spacy
from spacy.tokens import DocBin

app = FastAPI()
nlp = None

@app.on_event("startup")
def load_local_model():
    global nlp
    nlp = spacy.load(str("outputs/model-best"))
    if "entity_ruler" not in nlp.pipe_names:
        nlp.add_pipe("entity_ruler").from_disk("ngrams/patterns.jsonl")


def render_entities_html(text: str, ents: List[Dict[str, Any]]):
    colors = {"Hard Skill": "#a8d1d1", "Soft Skill": "#fd8a8a"}
    pieces = []
    last = 0
    ents_sorted = sorted(ents, key=lambda ent: ent["start"]) # sort to match text
    for e in ents_sorted:
        start, end, label = e["start"], e["end"], e["label"]

        # highlight individually
        pieces.append(text[last:start])
        color = colors.get(label, "#ffd966")
        pieces.append(f'<mark style="background:{color};padding:0 2px;border-radius:3px">{text[start:end]}</mark>')
        last = end

    pieces.append(text[last:])
    container = "<div style='line-height:1.5'>" + "".join(pieces) + "</div>"
    return container


def make_skill_lists(doc): # to display all extracted skills
    soft = []
    hard = []
    for e in doc.ents:
        if e.label_ == "Soft Skill":
            soft.append(e.text)
        elif e.label_ == "Hard Skill":
            hard.append(e.text)

    soft_str = "<h3>Soft skills: </h3>" + (", ".join(soft) if soft else "")
    hard_str = "<h3>Hard skills: </h3>" + (", ".join(hard) if hard else "")
    return {"soft": soft_str, "hard": hard_str}


def demo():
    doc_bin = DocBin().from_disk("test.spacy")
    docs = list(doc_bin.get_docs(nlp.vocab))

    # display a random doc from test set
    doc_gold = random.choice(docs)
    text = doc_gold.text

    # model predictions on the same text
    doc_pred = nlp(text)
    pred_ents = [{"label": e.label_, "start": e.start_char, "end": e.end_char, "text": e.text} for e in doc_pred.ents]

    # skill lists (from model predictions)
    skills = make_skill_lists(doc_pred)
    html_entities = render_entities_html(text, pred_ents)

    html = (
        f"<pre style='white-space:pre-wrap;background:#f7f7f7;padding:8px;border-radius:6px'>"
        f"{skills['soft']}\n\n{skills['hard']}</pre><hr>"
        f"{html_entities}"
        f"</div>"
    )

    return {
        "text": text,
        "pred_entities": pred_ents,
        "html": html,
        "soft_skills": skills["soft"],
        "hard_skills": skills["hard"],
    }


@app.get("/", response_class=HTMLResponse)
def render():
    try:
        resp = demo()
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return resp["html"]

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("demo:app", host="0.0.0.0", port=8088, reload=True)