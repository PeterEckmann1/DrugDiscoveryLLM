import os
import sys
import requests
import base64


def get_docking_data(ligand, protein, iter):
    response = requests.get(f"{os.environ['API_URL']}?endpoint=run_docking&smiles={ligand}&target={protein}")

    open('view0.png', 'wb').write(base64.b64decode(response.json()['images']['view0']))
    open('view1.png', 'wb').write(base64.b64decode(response.json()['images']['view1']))
    open('view2.png', 'wb').write(base64.b64decode(response.json()['images']['view2']))

    open(f'imgs/view0_{iter}.png', 'wb').write(base64.b64decode(response.json()['images']['view0']))
    open(f'imgs/view1_{iter}.png', 'wb').write(base64.b64decode(response.json()['images']['view1']))
    open(f'imgs/view2_{iter}.png', 'wb').write(base64.b64decode(response.json()['images']['view2']))

    if response.status_code==200:
        data = response.json()
        if "error" in data:
            return None
        else:
            return data
    else:
        return None
