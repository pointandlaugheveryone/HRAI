import json
from models.LabelStudio import *

with open('DATA/cleaned_resumes.json','r') as j:
    labeled_resumes = json.loads(j.read())

documents = []

for r in labeled_resumes:
    name, text, labels = r['id'], r['content'], r['labels']
    
    results = []
    for l in labels:
        start, end, label, value = l["start"], l["end"], l["label"], l["value"]
        results.append(Result.create(start, end, label, value))
    
    documents.append(Document.create(text, results).model_dump())
    
with open('export_labelstudio.json', 'w') as f:
    f.write(json.dumps(documents))