from google import genai
from google.genai import types
import os
import matplotlib.pyplot as plt

from api import get_docking_data

protein = "c-met"

for outer_iter in range(10):
    system_instructions = "You are an assistant helping a lab generate ligands that can bind to certain proteins with high binding affinity."
    client = genai.Client(api_key=os.environ["API_KEY"])
    chat = client.chats.create(model="gemini-2.0-flash-thinking-exp", config=types.GenerateContentConfig(system_instruction=system_instructions))

    if outer_iter == 0:
        init_prompt = f"We will collaborate on generating a ligand for the {protein} protein with high binding affinity. I will give you the output from docking software after each attempt. Make sure your response contains a SMILES string at the end, and make sure that the SMILES string is valid. Start by generating an initial ligand."
    else:
        init_prompt = f"We will collaborate on generating a ligand for the {protein} protein with high binding affinity. I will give you the output from docking software after each attempt. Make sure your response contains a SMILES string at the end, and make sure that the SMILES string is valid. The last ligand you generated was {best_molecule}, so start from there."
    response = chat.send_message(init_prompt)

    ligand = response.text.split()[-1]

    data = get_docking_data(ligand, protein, 0)
    invalid_ligand = False
    if data:
        print(f'Initial generation: Molecule: {ligand} | Binding affinity: {data["binding_affinity"] if not invalid_ligand else 0}')
    else:
        print("Initial generation: Invalid ligand")
        invalid_ligand = True


    num_iterations = 20
    affinities = [data["binding_affinity"]] if not invalid_ligand else []
    best_affinity = data["binding_affinity"] if not invalid_ligand else 0
    best_molecule = ligand
    best_iteration = 0
    for i in range(num_iterations):
        iterated_prompt = ""
        if not invalid_ligand:
            # iterated_prompt = [f"""Software shows that the molecule you generated, {ligand}, had a binding affinity of {data["binding_affinity"]} to {protein}.
            #                     Additionally, the torsional energy was {data["torsional_energy"]}, the number of rotatable bonds was {data["number_of_rotatable_bonds"]},
            #                     the number of hydrogen bonds was {data["hydrogen_bonds"]}, the number of pi pi stacking interactions was {data["pi_pi_stacking_interactions"]},
            #                     the number of salt bridges was {data["salt_bridges"]}, and the number of t stacking interactions was {data["t_stacking_interactions"]}. 
            #                     Three pictures of the interaction between the ligand and protein are also included.
            #                     Based on this information, generate a better ligand, following the same answer format""",
            #                     types.Part.from_bytes(data=data["images"]["view0"], mime_type="image/jpeg"), types.Part.from_bytes(data=data["images"]["view1"], mime_type="image/jpeg"), types.Part.from_bytes(data=data["images"]["view2"], mime_type="image/jpeg")]

            iterated_prompt = [f"""Software shows that the molecule you generated, {ligand}, had a binding affinity of {data["binding_affinity"]} to {protein} and formed {data["hydrogen_bonds"]} hydrogen bonds.
                                Pictures of the interaction between the ligand and protein are also included, and the protein surface is colored by electrostatics. First, describe what you see in the image, and relate it to the observed binding affinity. Then discuss how to improve the binding.
                                Based on this information, generate a better ligand, following the same answer format. Please keep trying improvements, and never say the ligand is final. Ensure the last word of your response is a valid SMILES string.""",
                                types.Part.from_bytes(data=data["images"]["view0"], mime_type="image/png"), types.Part.from_bytes(data=data["images"]["view1"], mime_type="image/png"), types.Part.from_bytes(data=data["images"]["view2"], mime_type="image/png")]
            
            # iterated_prompt = f"""Software shows that the molecule you generated, {ligand}, had a binding affinity of {data["binding_affinity"]} to {protein}.
            # Based on this information, generate a better ligand, following the same answer format. Use the following images of the docked pose to guide your generation. Try to optimize the number of hydrogen bonds made with the protein, which are shown in the images."""
        else:
            iterated_prompt = f"Software shows that the molecule you generated, {ligand}, had a binding affinity of 0 to {protein}. Generate a new ligand, following the same answer format."
        # try:
        response = chat.send_message(iterated_prompt)

        open(f'imgs/{i+1}.txt', 'w').write(response.text)

        ligand = response.text.split()[-1]

        try:
            data = get_docking_data(ligand, protein, i+1)
        except:
            data = None
        if(data):
            invalid_ligand=False
            affinities.append(data["binding_affinity"])
            if data["binding_affinity"]<best_affinity:
                best_affinity = data["binding_affinity"]
                best_molecule = ligand
                best_iteration = i+1
            print(f'Iteration {i+1}: Molecule: {ligand} | Binding affinity: {data["binding_affinity"]} | Hydrogen bonds: {data["hydrogen_bonds"]}')
        else:
            invalid_ligand=True
            print(f"Iteration {i+1}: Invalid ligand")
        #except:
        #    break