import json

import requests, uuid, time, os
import asyncio

from srsly import json_dumps


async def azure_translate(texts, lang_from, lang_to):
    resource_key = os.getenv('TRANSLATE_KEY')
    resource_loc = 'germanywestcentral' # resource 
    endpoint = 'https://api.cognitive.microsofttranslator.com'
    path = '/translate?api-version=3.0'
    params = f'&from={lang_from}&to={lang_to}'
    url = endpoint + path + params
    headers = {
        'Ocp-Apim-Subscription-Key': resource_key,
        'Ocp-Apim-Subscription-Region': resource_loc,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }

    results = []
    for text in texts:
        body = [{ 'text' : text }]
        request = requests.post(url, headers=headers, json=body)

        if request.status_code != 200:
            print(f"Error: {request.status_code}, {request.text}")

        response = request.json()[0]["translations"][0]["text"]
        results.append(response)

    return results
    

async def main():
    with open('data/resumes_en.json', 'r') as r:
        data = json.loads(r.read())
    en = await azure_translate(data, 'en', 'cs')

    with open('data/resumes_cs.json', 'w') as w:
        w.write(json_dumps(en))

asyncio.run(main())
 