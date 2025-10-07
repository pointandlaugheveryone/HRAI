import json, spacy


with open('skill_db_relax_20.json', 'r') as f:
    skills = list(json.loads(f.read()).values())

nlp = spacy.load('en_core_web_lg')

if 'entity_ruler' in nlp.pipe_names:
    nlp.disable_pipe('entity_ruler')
ruler = nlp.add_pipe('entity_ruler')

patterns = []
for s in skills:
    label = s['skill_type']
    if label == "Certification": 
        continue
    pattern = str(s['skill_name']).lower()
    p_list = pattern.split(' ')
    p_dict = []
    for p in p_list:
        p_dict.append({"LOWER":p})
    patterns.append({
        'label':label,
        'pattern':p_dict
        })
    
ruler.add_patterns(patterns)
ruler.to_disk("patterns.jsonl")