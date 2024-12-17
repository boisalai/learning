import sys

def display_info():
    print("Hello, World!")
    print("Current Python virtual environment:", sys.prefix)
    print("Current Python interpreter:", sys.executable)
    print("Python version:", sys.version)
    print("Python search path:", sys.path)

if __name__ == "__main__":
    display_info()