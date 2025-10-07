import requests, rich


params = {
    'code': 'nzAgufs0zl7xHKG0cjNilcxSCIoBWqxe88PpdYWOB_--AzFu9iw9GQ=='
}

with open('test_data.txt', 'r') as f:
    texts = [f.read().replace('\n',' ').replace('\t',' ')]

payload = {'docs': texts,'model':'cvnlp'}
r = requests.post('http://cvnlp.azurewebsites.net/api/post/',params=params,json=payload)
if r.status_code == 200:
    rich.print(r.text)
else: 
    print(r.json)