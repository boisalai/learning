from setuptools import setup, find_packages

setup(
    name="tax_calculator",
    version="0.1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        'core',
    ],
    extras_require={
        'dev': [
            'pytest',
        ],
    },
) 