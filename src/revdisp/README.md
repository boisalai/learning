# Revenu disponible

## Objectifs

- Déveloper le code python pour tous les programmes socio-fiscaux du Québec et du Canada en 2023 et 2024.
- Créer des tableaux et graphiques pour visualiser les résultats (y compris les taux marginaux d'imposition).
- Créer une interface web pour visualiser les résultats.
- Documenter chaque programme socio-fiscal : description, graphique, tableau, code, tests.
- Publier sur GitHub.

## Prompt

Nous avons 6 fichiers en contexte :

- "obfuscated.js" : un script complet mais obfuscated pour calculer les impôts, cotisations et transferts aux particuliers.
- "index.html" : un fichier HTML pemettant de visualiser les résultats des calculs.
- "script.py" : un script pour créer un fichier json avec les résultats des calculs.
- "revdisp.py" : un script incomplet pour calculer les impôts, cotisations et transferts aux particuliers.
- "test_framework.py" : un script pour automatiser les tests de "revdisp.py".
- "resultats_5_cas.json" : un fichier JSON contenant les résultats attendus des calculs.

Ajuste "revdisp.py" pour calculer la cotisation au 
Régime d'assurance médicaments du Québec
en t'inspirant du code dans "obfuscated.js" et dans "revdisp.py".

Tu trouveras dans "0.pdf" la cotisation pour 2023.

Ajuste "test_framework.py" pour valider les résultats obtenus avec "resultats.json".

## Aide mémoire

Exécuter le script.py pour générer des cas avec la commande suivante :

```bash
clear; python script.py --nobs 5
clear; python script.py --nobs 10
clear; python script.py --nobs 1000
```

Exécuter les tests avec la commande suivante :

```bash
clear && python test_framework.py --nobs 5
clear; python test_framework.py --nobs 10
clear; python test_framework.py --nobs 1000
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
