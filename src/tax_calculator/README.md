# Revenu disponible

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

<!--
See https://github.com/chonkie-ai/chonkie
-->

## Objectifs

- Déveloper le code python pour tous les programmes socio-fiscaux du Québec et du Canada en 2023 et 2024.
- Créer des tableaux et graphiques pour visualiser les résultats (y compris les taux marginaux d'imposition).
- Créer une interface web pour visualiser les résultats.
- Documenter chaque programme socio-fiscal : description, graphique, tableau, code, tests.

## Structure

```plaintext
Learning/
├── src/
│   └── tax_calculator/
│       ├── __init__.py           # Marque le répertoire comme package Python
│       ├── core.py               # Nos définitions de base
│       ├── calculators/
│       │   ├── __init__.py
│       │   ├── python_calculator.py
│       │   └── js_calculator.py
│       └── programs/
│           ├── __init__.py
│           ├── ei_premiums.py
│           └── quebec_tax.py
├── setup.py                      # Configuration du package
└── requirements.txt
``` 

## Progression

- **Régime fiscal du Québec**
  - Impôt sur le revenu des particuliers
    - Montant avant la baisse d'impôt
    - Baisse d'impôt
  - Aide sociale
  - Allocation famille
  - Supplément pour l'achat de fournitures scolaires
  - Prime au travail
  - Crédit pour la solidarité
  - Crédit d'impôt pour frais de garde d'enfants
  - Allocation-logement 
  - Crédit d'impôt remboursable pour frais médicaux
  - Montant pour le soutien des aînés
- **Régime fiscal fédéral**
  - Impôt sur le revenu des particuliers
  - Allocation canadienne pour enfants
  - Crédit pour la TPS
  - Allocation canadienne pour les travailleurs 
  - Programme de la Sécurité de la vieillesse
  - Supplément remboursable pour frais médicaux
- **Cotisations**
  - (OK) Assurance-emploi
  - (OK) Régime québécois d'assurance parentale
  - (OK) Régime de rentes du Québec
  - (OK) Fonds des services de santé
  - (OK) Régime d'assurance médicaments du Québec
- **Frais de garde**

## See also

- https://ici.radio-canada.ca/nouvelle/2128404/changement-finance-portefeuille-2025
