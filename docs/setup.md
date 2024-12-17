# Python Project Setup Guide

## Initial Setup

Begin by creating a new project folder using the terminal. Once created, navigate into the folder and open it in Visual Studio Code (VS Code).

Execute the following commands in the terminal:

```bash
mkdir my-project          # Create a new directory named 'my-project'
cd my-project             # Change the current working directory to 'my-project'
python3 -m venv .venv     # Create a virtual environment
source .venv/bin/activate # Activate the virtual environment (for MacOS/Linux)
# OR
.\.venv\Scripts\activate  # Activate the virtual environment (for Windows)
```

Verify the Python interpreter and pip installation in the virtual environment:

```bash
which python      # Check Python path
which pip         # Check pip path
```

Upgrade pip and initialize a new Git repository:

```bash
python -m pip install --upgrade pip  # Upgrade pip to the latest version
git init                             # Initialize Git repository
```

Open the project in Visual Studio Code:

```bash
code .
```

## Basic Python Script Setup

Create a new file named `main.py` with the following code:

```python
import sys

def display_info():
    print("Hello, World!")
    print("Current Python virtual environment:", sys.prefix)
    print("Current Python interpreter:", sys.executable)
    print("Python version:", sys.version)
    print("Python search path:", sys.path)

if __name__ == "__main__":
    display_info()
```

Run the script:

```bash
python main.py
```

## Standard Python Project Structure

Here's a typical well-organized structure for a standard Python project:

```plaintext
my_project/
├── .venv/                 # Virtual environment (locally generated, not versioned)
├── src/                   # Main project package
│   ├── __init__.py        # Marks the directory as a Python package
│   ├── main.py            # Main entry point
│   ├── module1.py         # Python module example
│   ├── module2.py         # Python module example
│   └── utils/             # Utilities sub-package
│       ├── __init__.py
│       ├── helper1.py
│       └── helper2.py
├── tests/                 # Unit and integration tests
│   ├── __init__.py
│   ├── test_module1.py
│   └── test_module2.py
├── data/                  # Project data
│   ├── raw/               # Raw data
│   └── processed/         # Processed data
├── docs/                  # Project documentation
│   └── README.md          # Additional documentation
├── notebooks/             # Jupyter notebooks for exploration
│   └── example.ipynb
├── .gitignore             # Git ignore patterns
├── requirements.txt       # Project dependencies
├── setup.py               # Project installation script
├── README.md              # Main project description
├── LICENSE                # Project license
└── pyproject.toml         # Standardized configuration
```

### Directory Details

- **`src/`**: Contains the main source code, with each file/subdirectory representing a module/package
- **`tests/`**: Contains automated tests following the `test_<module_name>.py` convention
- **`data/`**: Separates raw and processed data
- **`docs/`**: For additional documentation
- **`notebooks/`**: For Jupyter notebooks used in exploration/prototyping

### Configuration Files

- **`README.md`**: Project description, objectives, and usage instructions
- **`requirements.txt`**: Dependencies list (install via `pip install -r requirements.txt`)
- **`setup.py`**: Packaging and distribution script
- **`.gitignore`**: Prevents tracking of specified files
- **`pyproject.toml`**: Modern tool configurations (black, flake8, pytest, etc.)

## Git Setup

Create `.gitignore`:

```plaintext
# Python virtual environment
.venv/
pyvenv.cfg

# Python cache files
__pycache__/
*.pyc

# Environment variables
.env

# VS Code settings
.vscode/

# Log files
*.log

# macOS system files
.DS_Store
```

## Package Management

Install required packages and create requirements file:

```bash
python -m pip install numpy pandas
python -m pip freeze > requirements.txt
```

## Git Initial Commit and Remote Setup

```bash
git add .
git commit -m "initial commit"
git branch -M main
git remote add origin git@github.com:username/repository.git
git push -u origin main
```

For more information, see [Getting Started with Python in VS Code](https://code.visualstudio.com/docs/python/python-tutorial).