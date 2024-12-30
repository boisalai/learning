import os
import re
from pathlib import Path

def categorize_instructions(instructions):
    # Même fonction que précédemment
    categories = {
        'inputs': [],
        'consts': [],
        'calcs': [],
        'outputs': []
    }
    
    for inst in instructions:
        if 'data[' in inst:
            categories['inputs'].append(inst)
        elif re.search(r'var\s+c\dL\d+\s*=\s*\([\d.]+\)', inst):
            categories['consts'].append(inst)
        elif 'data[' not in inst and '=' in inst:
            categories['calcs'].append(inst)
        else:
            categories['outputs'].append(inst)
            
    return categories

def extract_dependencies(js_code, target_var):
    # Même logique de recherche
    instructions = []
    seen_vars = set()

    def find_definition(var):
        # Même fonction que précédemment
        if var in seen_vars:
            return
        seen_vars.add(var)

        # Ajouter un pattern pour les initialisations de tableaux
        array_pattern = rf"var\s+({re.escape(var)})\s*=\s*new\s+Array\([^;]+\);"
        
        patterns = [
            (rf"(?:var\s+)?{re.escape(var)}\s*=\s*([^;]+);", False),
            (rf"{re.escape(var)}\[[^\]]+\]\s*=\s*([^;]+);", True),
            (rf"{re.escape(var)}\s*=\s*([^;]+);", False),
            (array_pattern, False)  # Nouveau pattern
        ]

        for pattern, is_array in patterns:
            matches = re.finditer(pattern, js_code)
            for match in matches:
                definition = match.group(0)
                if definition not in instructions:
                    instructions.append(definition)

                vars_used = re.findall(r'[a-zA-Z][a-zA-Z0-9_]+(?:\[[^\]]+\])*', match.group(1))
                # Ajouter la recherche dans les initialisations de tableaux
                array_vars = re.findall(r'[a-zA-Z][a-zA-Z0-9_]+', match.group(0))
                vars_used.extend(array_vars)

                for v in vars_used:
                    if any(v.startswith(p) for p in ('c1', 'c2', 'c4', 'arr', 'sum', 'tmp')):
                        find_definition(v)

        if '[' in var and ']' in var:
            array_var = re.match(r'([^\[]+)', var).group(1)
            find_definition(array_var)

    find_definition(target_var)
    instructions.sort(key=lambda x: js_code.index(x))
    categories = categorize_instructions(instructions)

    # Définir le chemin du fichier de sortie
    downloads_path = str(Path.home() / "Downloads" / "instructions.js")

    # Écrire les instructions dans le fichier
    with open(downloads_path, "w") as f:
        f.write(
            "Ces instructions calculent [...].  Réécris ces instructions en python facile à comprendre."
        )
        f.write("// Input vars\n")
        f.write("\n".join(categories["inputs"]))
        f.write("\n\n// Const vars\n")
        f.write("\n".join(categories["consts"]))
        f.write("\n\n// Calc vars\n")
        f.write("\n".join(categories["calcs"]))
        f.write("\n\n// Output vars\n")
        f.write("\n".join(categories["outputs"]))

    return instructions

script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, '..', 'static', 'revdisp', 'js', 'revenu-disponible_dec2023.js')

with open(file_path, 'r') as f:
    js_code = f.read()

instructions = extract_dependencies(js_code, 'c1D41')
