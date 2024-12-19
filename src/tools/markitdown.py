"""
# MarkItDown

Python tool for converting files and office documents to Markdown.

To install MarkItDown, use pip: `pip install markitdown`.

See [here](https://github.com/microsoft/markitdown) for more information.
"""
from markitdown import MarkItDown
import os

def convert_and_save(source_path):
    md = MarkItDown()
    result = md.convert(source_path)

    base_path = os.path.splitext(source_path)[0]
    output_path = base_path + '.md'
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(result.text_content)
    
    return output_path

# Usage
source = "/Users/alain/Workspace/SOSO/FASB_Projet_A_J0173027_EN COURS.docx"
source = "/Users/alain/Workspace/SOSO/FSAB_Budget_projet_A.xlsx"
output_file = convert_and_save(source)
print(f"Markdown file created : {output_file}")