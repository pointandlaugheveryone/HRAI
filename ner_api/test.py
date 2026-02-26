import requests, rich, random, json
from pathlib import Path

parent_dir = Path.cwd().parent
URL = 'http://127.0.0.1:8000'
with open(str(parent_dir) + 'spacy_cnn_ner_en/data/resumes_en.json', 'r') as f:
    texts = json.loads(f.read())

payload = {'docs': texts[random.randint(1,2457)],
           'model':'cvnlp'
           }

r = requests.post(f'{URL}/post/',json=payload)
rich.print(r.text)