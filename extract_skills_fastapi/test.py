import requests, rich


URL = 'http://127.0.0.1:8000'
with open('test.txt', 'r') as f:
    texts = [f.read().replace('\n',' ').replace('\t',' ')]

payload = {'docs': texts,'model':'cvnlp'}
r = requests.post(f'{URL}/post/',json=payload)
rich.print(r.text)