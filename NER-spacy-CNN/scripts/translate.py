import requests, uuid, time, os
from azure.identity import DefaultAzureCredential
import azure.keyvault.secrets as azk
import asyncio
from uuid import uuid4


def get_key(keyname: str):
    vault_name = 'CVbutbetter'
    vault_uri = f'https://{vault_name}.vault.azure.net'
    client = azk.SecretClient(vault_uri, DefaultAzureCredential())
    secret = client.get_secret(keyname)
    key = secret.value
    return key


def parse_files():
    dir_path = f'{os.getcwd()}/DATA/data_en'
    texts_en = []
    filenames = []
    for filename in os.listdir(dir_path):
        filepath = os.path.join(dir_path, filename)
        with open(filepath, 'r', encoding='utf-8') as file:
            filenames.append(file.name)
            texts_en.append(file.read())
    return texts_en, filenames


async def azure_translate(text:str,filename_id:str):
    resource_key = get_key('translationKey')
    resource_loc = 'germanywestcentral' # resource 
    endpoint = 'https://api.cognitive.microsofttranslator.com'
    path = '/translate?api-version=3.0'
    params = '&from=en&to=cs'
    constructed_url = endpoint + path + params
    headers = {
        'Ocp-Apim-Subscription-Key': resource_key,
        'Ocp-Apim-Subscription-Region': resource_loc,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }
    body = [{ 'text' : text }]
    request = requests.post(constructed_url, headers=headers, json=body)

    if request.status_code != 200:
        print(f"Error: {request.status_code}, {filename_id}.txt, {request.text}")

    
    response = request.json()   
    with open(f'{os.getcwd()}/data_cs/{filename_id}.txt','w') as newf:
        newf.write(response[0]["translations"][0]["text"])
    return response[0]["translations"][0]["text"]
    
   

async def main():
    with open('m.txt','r') as f:
        t = f.read()
    en = await azure_translate(t,'m')
    print(en)
   
        

asyncio.run(main())
 