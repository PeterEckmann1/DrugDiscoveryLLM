import random
from google import genai
from google.genai import types
import os
import os
import requests
import json
import base64
import sys


def get_docking_data(ligand, protein):
    response = requests.get(f"{os.environ['API_URL']}?endpoint=run_docking&smiles={ligand}&target={protein}")
    if response.status_code == 200:
        data = response.json()
        if 'images' in data:
            for i, img in enumerate(data['images']):
                open(f'{img}.png', 'wb').write(base64.b64decode(data['images'][img]))
        if 'error' in data:
            return None
        return data
    else:
        return None


def run(config):
    log = open(f'logs/{config.split("/")[-1].replace(".json", ".txt")}', 'a')
    config = json.load(open(config, 'r'))

    for protein in config['proteins']:
        log.write(f'Starting protein {protein}\n\n')
        for trial in range(config['num_trials']):
            system_instructions = config['system_instructions'].replace('__PROTEIN__', protein)
            client = genai.Client(api_key=os.environ['API_KEY'])
            chat = client.chats.create(model=config['model'], config=types.GenerateContentConfig(system_instruction=system_instructions))
            prompt = [config['init_prompt'].replace('__PROTEIN__', protein)]
            log.write(f'Starting trial {trial}\n\n')

            for i in range(config['conversation_length']):
                response = chat.send_message(prompt)
                log.write('-------------------------------' + '\n')
                log.write('Promt: ' + prompt[0] + '\n' + '-------------------------------' + '\n')
                log.write('Response: ' + response.text + '\n\n')
                log.flush()
                ligand = response.text.replace('```', '').split()[-1]
                data = get_docking_data(ligand, protein)

                if data and data['binding_affinity'] != 0:
                    log.write(f'Docking result: {ligand} {data["binding_affinity"]} {data["hydrogen_bonds"]} {protein}\n\n')
                    prompt = [config['feedback_prompt'].replace('__SMILES__', ligand).replace('__BINDING_AFFINITY__', str(random.uniform(-15, -5)) if config['randomize_affinity'] else str(data['binding_affinity'])).replace('__PROTEIN__', protein).replace('__HYDROGEN_BONDS__', str(data['hydrogen_bonds']))]
                    if config['include_images']:
                        for img in data['images']:
                            prompt.append(types.Part.from_bytes(data=data['images'][img], mime_type="image/png"))
                else:
                    log.write(f'Docking result: {ligand} failed {protein}\n\n')
                    prompt = [config['invalid_prompt'].replace('__PROTEIN__', protein).replace('__SMILES__', ligand)]


run(sys.argv[1])