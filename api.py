import os
import sys
import requests


def get_docking_data(ligand, protein):
    response = requests.get(f"{os.environ["API_URL"]}?endpoint=run_docking&smiles={ligand}&target={protein}")
    if response.status_code==200:
        data = response.json()
        if "error" in data:
            return None
        else:
            return data
    else:
        return None
