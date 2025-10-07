import os, json, rich, unicodedata
from tqdm import tqdm
import spacy
from spacy.matcher import PhraseMatcher
from skillNer.general_params import SKILL_DB
from skillNer.skill_extractor_class import SkillExtractor
from skillNer.text_class import Text, Word
from itertools import islice


def batch_docs(iterable, batch_size=50):
    it = iter(iterable) #yield sized chunks
    while True:
        batch = list(islice(it, batch_size))
        if not batch:
            break
        yield batch


nlp = spacy.load('en_core_web_lg')
skill_extractor = SkillExtractor(nlp, SKILL_DB, PhraseMatcher)

with open('DATA/resumes.json','r') as f:
    data = json.loads(f.read())

documents = []
i = 0

for batch in batch_docs(data):
    try:
        texts = [
            unicodedata.normalize('NFKD', d).encode('ascii', 'ignore').decode("utf-8") 
                    # ascii decode necessary to avoid index errors caused by unhandled spacy updates in skillNer
            for d in batch
        ]
        docs = list(nlp.pipe(texts))

        for text, doc in zip(texts, docs):
            entities = []
            doc_text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode("utf-8")
            annotations = skill_extractor.annotate(doc_text)

            for n in annotations['results']['full_matches']:
                value = n['doc_node_value']
                label = SKILL_DB[n["skill_id"]]["skill_type"]
                start = doc_text.find(value)
                if start == -1:
                    continue
                else:
                    end = start + len(value)
                    entities.append([start, end, label, value])

            for m in annotations['results']['ngram_scored']:
                value = m['doc_node_value']
                start = m['doc_node_id'][0]
                end = start + len(m['doc_node_value'])
                label = SKILL_DB[m["skill_id"]]["skill_type"]
                entities.append([start, end, label, value])

            documents.append([doc_text, entities])

    except IndexError:
        with open(f'DATA/docs_{i}.json', 'x') as j:
            print('invalid document text')
            i += 1
            j.write(json.dumps(documents))

