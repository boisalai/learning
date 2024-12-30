# Revenu disponible

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## Objectifs

- Déveloper le code python pour tous les programmes socio-fiscaux du Québec et du Canada en 2023 et 2024.
- Créer des tableaux et graphiques pour visualiser les résultats (y compris les taux marginaux d'imposition).
- Créer une interface web pour visualiser les résultats.
- Documenter chaque programme socio-fiscal : description, graphique, tableau, code, tests.
- Publier sur GitHub.

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
  - Régime d'assurance médicaments du Québec
- **Frais de garde**




Très bien. Le code javascript obfusqué contient les paramètres et règles de calculs de chacun de ces programmes socio-fiscaux pour 2023 et 2024.

- **Régime fiscal du Québec**
  - (OK) Impôt sur le revenu des particuliers
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
  - Régime d'assurance médicaments du Québec
- **Frais de garde**

Peux-tu faire la même chose, créer un code python complet incluant tous les paramètres pour calculer l'aide sociale?

## DeepSeek

### Impôt sur le revenu du Québec

```python
class QuebecIncomeTaxCalculator:
    def __init__(self, year):
        self.year = year
        self.tax_brackets = self.get_tax_brackets()

    def get_tax_brackets(self):
        if self.year == 2023:
            return [
                {"min": 0, "max": 46295, "rate": 0.15},
                {"min": 46295, "max": 92580, "rate": 0.20},
                {"min": 92580, "max": 112655, "rate": 0.24},
                {"min": 112655, "max": float('inf'), "rate": 0.2575}
            ]
        elif self.year == 2024:
            return [
                {"min": 0, "max": 47000, "rate": 0.15},
                {"min": 47000, "max": 94000, "rate": 0.20},
                {"min": 94000, "max": 114000, "rate": 0.24},
                {"min": 114000, "max": float('inf'), "rate": 0.2575}
            ]
        else:
            raise ValueError("Year not supported")

    def calculate_tax(self, income):
        tax = 0
        for bracket in self.tax_brackets:
            if income > bracket["min"]:
                taxable_amount = min(income, bracket["max"]) - bracket["min"]
                tax += taxable_amount * bracket["rate"]
        return tax

    def calculate_tax_reduction(self, income):
        if self.year == 2023:
            reduction_rate = 0.165
            reduction_threshold = 16143
        elif self.year == 2024:
            reduction_rate = 0.165
            reduction_threshold = 16400
        else:
            raise ValueError("Year not supported")

        if income <= reduction_threshold:
            return income * reduction_rate
        else:
            return reduction_threshold * reduction_rate

    def calculate_total_tax(self, income):
        tax = self.calculate_tax(income)
        reduction = self.calculate_tax_reduction(income)
        return tax - reduction

# Exemple d'utilisation
year = 2023
income = 80000
calculator = QuebecIncomeTaxCalculator(year)
total_tax = calculator.calculate_total_tax(income)
print(f"Total tax for {year}: {total_tax:.2f} CAD")
```

### Aide sociale

Excellent! Peux-tu faire la même chose, créer un code python complet incluant tous les paramètres pour calculer l'aide sociale?




## See also

- [Revenu disponible 2023 et 2024 du MFQ](https://www.finances.gouv.qc.ca/ministere/outils_services/outils_calcul/revenu_disponible/index.asp)
- [Paramètres du régime d'imposition des particuliers - 2024](https://cdn-contenu.quebec.ca/cdn-contenu/adm/min/finances/publications-adm/parametres/AUTFR_RegimeImpot2024.pdf)
- [Guide des mesures fiscales](https://cffp.recherche.usherbrooke.ca/outils-ressources/guide-mesures-fiscales/)


## CLAUDE

J'ai ce code pour tester.

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from pathlib import Path
import time
import random


class TaxCalculatorTest:
    def __init__(self, url):
        self.driver = webdriver.Firefox()
        self.driver.get(url)
        
    def select_by_text(self, element_id, text):
        element = self.driver.find_element(By.ID, element_id)
        for option in element.find_elements(By.TAG_NAME, 'option'):
            if option.text.strip() == text.strip():
                option.click()
                break
        self.driver.execute_script(f"recalc_onclick('{element_id}')")
        
    def fill_field(self, selector, value):
        element = self.driver.find_element(By.ID, selector)
        element.clear()
        element.send_keys(str(value))
        self.driver.execute_script(f"recalc_onclick('{selector}')")
        
    def extract_results(self):
        results = {}
        result_fields = ['RD_new', 'QC_total_new', 'CA_total_new', 'Cotisation_new']
        for field in result_fields:
            element = self.driver.find_element(By.ID, field)
            results[field] = element.get_attribute('value')
        return results
    
    def close(self):
        self.driver.quit()

def generate_test_cases(nobs=10):
    """Génère des cas de test pour le calculateur fiscal"""
    
    situations = [
        'Personne vivant seule',
        'Famille monoparentale',
        'Couple',
        'Retraité vivant seul',
        'Couple de retraités'
    ]
    
    revenus = [0, 15000, 30000, 45000, 60000, 75000, 90000]
    ages_travailleur = [25, 35, 45, 55]
    ages_retraite = [65, 75, 85]
    ages_enfant = [2, 5, 10, 15]
    nb_enfants = range(4)  # 0 à 3 enfants
    frais_garde = [0, 8000, 15000]
    types_garde = ['Subventionnée', 'Non subventionnée']

    test_cases = []
    
    # Générer les cas de test
    for _ in range(nobs):
        situation = random.choice(situations)
        est_retraite = 'retraité' in situation.lower()
        est_couple = 'Couple' in situation
        peut_avoir_enfants = not est_retraite and situation != 'Personne vivant seule'

        case = {
            'situation': situation,
            'revenu1': random.choice(revenus),
            'age1': random.choice(ages_retraite if est_retraite else ages_travailleur),
            'revenu2': random.choice(revenus) if est_couple else 0,
            'age2': random.choice(ages_retraite if est_retraite else ages_travailleur) if est_couple else 0,
            'nb_enfants': 0
        }

        if peut_avoir_enfants:
            case['nb_enfants'] = random.choice(nb_enfants)
            for i in range(1, case['nb_enfants'] + 1):
                age_enfant = random.choice(ages_enfant)
                case[f'age_enfant{i}'] = age_enfant
                if age_enfant <= 5:
                    case[f'frais{i}'] = random.choice(frais_garde)
                    case[f'type_garde{i}'] = random.choice(types_garde)
                else:
                    case[f'frais{i}'] = 0
                    case[f'type_garde{i}'] = 'Subventionnée'
            
        test_cases.append(case)
    
    return test_cases

def run_tests():
    """Exécute les tests générés"""
    current_dir = Path(__file__).parent
    file_path = current_dir / "../../utils/revdisp/index.html"
    absolute_path = file_path.resolve()
    url = f"file://{absolute_path}"
    
    test_cases = generate_test_cases(5)  # Générer 5 cas de test
    results = []
    
    tester = TaxCalculatorTest(url)
    
    try:
        for case in test_cases:
            # Configuration de base
            tester.select_by_text('Situation', case['situation'])
            tester.fill_field('Revenu1', case['revenu1'])
            tester.fill_field('AgeAdulte1', case['age1'])
            
            if case['revenu2'] > 0:
                tester.fill_field('Revenu2', case['revenu2'])
                tester.fill_field('AgeAdulte2', case['age2'])
            
            # Configuration des enfants
            tester.select_by_text('NbEnfants', f"{case['nb_enfants']} enfant{'s' if case['nb_enfants'] > 1 else ''}" if case['nb_enfants'] > 0 else 'Aucun enfant')
            
            for i in range(1, case['nb_enfants'] + 1):
                tester.fill_field(f'AgeEnfant{i}', case[f'age_enfant{i}'])
                if case.get(f'frais{i}', 0) > 0:
                    tester.fill_field(f'Frais{i}', case[f'frais{i}'])
                    tester.select_by_text(f'type_garde{i}', case[f'type_garde{i}'])
            
            time.sleep(0.05) 
            
            # Récupérer les résultats
            test_results = tester.extract_results()
            case.update(test_results)
            results.append(case)
            
    finally:
        tester.close()
    
    # Sauvegarder les résultats
    #df = pd.DataFrame(results)
    #df.to_csv('test_results.csv', index=False)
    return results

if __name__ == "__main__":
    results = run_tests()
    print(f"Tests completed. Generated {len(results)} test cases.")
```

La classe `TaxCalculatorTest` exécute un modèle javascript d'une page HTML pour calculer le revenu dispnonible et les divers programmes socio-fiscaux (impôt, transferts et cotisations).

Je souhaite développer une autre classe qui referait les mêmes calculs mais en python.

Je souhaite aussi vérifier les résultats de cette classe avec les résultats obtenus avec le modèle javascript.

Peux-tu m'aider?

- Proposes des noms de fichiers pour les scripts python et les classes.
- Proposes des noms de fonctions pour les méthodes de ces classes.
- Dis dans quels répertoire du projet je dois mettre ces fichiers.
- Les commentaires dans le code doivent être en anglais