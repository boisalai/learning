import re

def extract_dependencies(js_code, target_var):
    # Pour stocker les instructions trouvées
    instructions = []
    # Pour éviter les boucles infinies
    seen_vars = set()
    
    def find_definition(var):
        if var in seen_vars:
            return
        seen_vars.add(var)
        
        # Cherche la définition de la variable 
        pattern = rf"(?:var\s+)?{re.escape(var)}\s*=\s*([^;]+);"
        match = re.search(pattern, js_code)
        if not match:
            return
            
        definition = match.group(0)
        instructions.append(definition)
        
        # Extrait toutes les variables utilisées dans la définition
        vars_used = re.findall(r'[a-zA-Z][a-zA-Z0-9_]*', match.group(1))
        
        # Recherche récursive des dépendances
        for v in vars_used:
            if v.startswith(('c1', 'c2', 'c4', 'arr')):
                find_definition(v)
    
    # Initialise avec la variable cible
    find_definition(target_var)
    
    # Trie selon l'ordre dans le fichier source
    instructions.sort(key=lambda x: js_code.index(x))
    
    return instructions

# Exemple d'utilisation
with open('../static/revdisp/js/obfuscated.js', 'r') as f:
    js_code = f.read()
    
# Extrait les instructions liées à QC_ramq_new
target = 'c1D43'
instructions = extract_dependencies(js_code, target)
for inst in instructions:
    print(inst)