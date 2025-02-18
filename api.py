import os
import sys
import requests


def calculate_affinity(ligand, protein):
    response = requests.get(f"{os.environ["API_URL"]}?endpoint=run_docking&smiles={ligand}&target={protein}")
    if response.status_code==200:
        affinity = response.json()
        if "error" in affinity:
            return 0
        else:
            return affinity['binding_affinity']
    else:
        print("Error: ", response.status_code)
        sys.exit()
