import os

def generate_markdown(directory, output_file):
    with open(output_file, 'w') as md_file:
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, directory)
                    md_file.write(f"# Learning/src/tax_calculator/{relative_path}\n\n")
                    md_file.write("```python\n")
                    with open(file_path, 'r') as py_file:
                        md_file.write(py_file.read())
                    md_file.write("\n```\n\n")
    
if __name__ == "__main__":
    project_directory = "/Users/alain/Workspace/GitHub/Learning/src/tax_calculator"
    output_markdown_file = "/Users/alain/Downloads/python_scripts.md"
    generate_markdown(project_directory, output_markdown_file)