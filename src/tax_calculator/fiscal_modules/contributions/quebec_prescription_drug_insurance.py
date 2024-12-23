"""
Quebec Prescription Drug Insurance calculator.

TODO:
    - Cette cotisation doit être calculée sur le revenu familial net de l'impôt du Québec.

Parameters reference:
    - [Bulletin d'information 2024-9](https://cdn-contenu.quebec.ca/cdn-contenu/adm/min/finances/publications-adm/Bulletins/FR/BULFR_2024-9.pdf)
    - [Bulletin d'information 2023-6](https://cdn-contenu.quebec.ca/cdn-contenu/adm/min/finances/publications-adm/Bulletins/FR/BULFR_2023-6-f-b.pdf)
    - [Cotisation au régime d’assurance médicaments du Québec](https://cffp.recherche.usherbrooke.ca/outils-ressources/guide-mesures-fiscales/cotisation-regime-assurance-medicaments-quebec/)
"""

from typing import Dict, List
from tax_calculator.core import TaxProgram, Family, FamilyStatus, AdultInfo

class QuebecPrescriptionDrugInsurance(TaxProgram):
    """Quebec Prescription Drug Insurance (RAMQ) calculator"""

    PARAMS = {
        2024: {
            'max_contribution': 731.0,
            'exemption_single': 19500.0,
            'exemption_single_one_child': 31610.0,
            'exemption_single_multiple_children': 35715.0,
            'exemption_couple': 31610.0,
            'exemption_couple_one_child': 35715.0,
            'exemption_couple_multiple_children': 39505.0,
            'first_threshold': 5000.0,
            'base_rate_single': 0.0765,
            'additional_rate_single': 0.1148,
            'base_rate_couple': 0.0384,
            'additional_rate_couple': 0.0575,
            'monthly_adjustment': 60.92
        },
        2023: {
            'max_contribution': 720.50,
            'exemption_single': 18910.0,
            'exemption_single_one_child': 30640.0,
            'exemption_single_multiple_children': 34545.0,
            'exemption_couple': 30640.0,
            'exemption_couple_one_child': 34545.0,
            'exemption_couple_multiple_children': 38150.0,
            'first_threshold': 5000.0,
            'base_rate_single': 0.0747,
            'additional_rate_single': 0.1122,
            'base_rate_couple': 0.0375,
            'additional_rate_couple': 0.0562,
            'monthly_adjustment': 60.04
        }
    }

    @property
    def name(self) -> str:
        return "Quebec Prescription Drug Insurance"

    @property
    def supported_years(self) -> List[int]:
        return list(self.PARAMS.keys())

    def calculate_income_based_contribution(self, excess_income: float, is_couple: bool, params: dict) -> float:
        """Calcule la contribution basée sur le revenu excédentaire"""
        if excess_income <= 0:
            return 0

        if is_couple:
            base_rate = params['base_rate_couple']
            additional_rate = params['additional_rate_couple']
        else:
            base_rate = params['base_rate_single']
            additional_rate = params['additional_rate_single']

        if excess_income <= params['first_threshold']:
            return excess_income * base_rate
        else:
            return (params['first_threshold'] * base_rate + 
                   (excess_income - params['first_threshold']) * additional_rate)

    def calculate(self, family: Family) -> Dict[str, float]:
        """Calculate QPDI contributions for a family"""
        self.validate_year(family.tax_year)
        params = self.PARAMS[family.tax_year]

        # Determine family type and corresponding exemption
        is_couple = family.adult2 is not None
        num_children = len(family.children) if family.children else 0

        # Family net income
        family_net_income = family.adult1.income
        if family.adult2:
            family_net_income += family.adult2.income

        # Determine exemption
        if is_couple:
            if num_children == 0:
                exemption = params['exemption_couple']
            elif num_children == 1:
                exemption = params['exemption_couple_one_child']
            else:
                exemption = params['exemption_couple_multiple_children']
        else:
            if num_children == 0:
                exemption = params['exemption_single']
            elif num_children == 1:
                exemption = params['exemption_single_one_child']
            else:
                exemption = params['exemption_single_multiple_children']

        # Calcul du revenu excédentaire
        excess_income = max(0, family_net_income - exemption)

        # Calcul de la contribution basée sur le revenu
        contribution = self.calculate_income_based_contribution(excess_income, is_couple, params)

        # Pour un couple, diviser la contribution
        if is_couple:
            contribution = contribution / 2

        # Si le revenu excède l'exemption, ajouter l'ajustement mensuel
        if contribution > 0:
            contribution += params['monthly_adjustment'] * 12

        # Application du maximum
        contribution = min(contribution, params['max_contribution'])

        if is_couple:
            adult1_contribution = -1 * contribution if contribution > 0 else 0
            adult2_contribution = -1 * contribution if contribution > 0 else 0
        else:
            adult1_contribution = -1 * contribution if contribution > 0 else 0
            adult2_contribution = 0.0

        # Arrondir les montants
        adult1_contribution = round(adult1_contribution, 2)
        adult2_contribution = round(adult2_contribution, 2)

        return {
            'program': self.name,
            'tax_year': family.tax_year,
            'adult1': adult1_contribution,
            'adult2': adult2_contribution,
            'total': adult1_contribution + adult2_contribution
        }


def chart():
    """Visualize Quebec Prescription Drug Insurance contributions calculation"""
    import numpy as np
    import matplotlib.pyplot as plt

    incomes = np.arange(0, 100001, 1000)
    contributions_single = []
    contributions_couple = []
    
    qpdi = QuebecPrescriptionDrugInsurance()
    
    # Calculate for single person
    for income in incomes:
        adult = AdultInfo(age=30, gross_work_income=income)
        test_case = {
            "family_status": FamilyStatus.SINGLE,
            "adult1": adult,
            "tax_year": 2024
        }
        family = Family(**test_case)
        result = qpdi.calculate(family)
        contributions_single.append(abs(result['total']))

    # Calculate for couple
    for income in incomes:
        adult1 = AdultInfo(age=30, gross_work_income=income/2)
        adult2 = AdultInfo(age=30, gross_work_income=income/2)
        test_case = {
            "family_status": FamilyStatus.COUPLE,
            "adult1": adult1,
            "adult2": adult2,
            "tax_year": 2024
        }
        family = Family(**test_case)
        result = qpdi.calculate(family)
        contributions_couple.append(abs(result['total']))

    plt.style.use('seaborn-v0_8-paper')
    fig, ax = plt.subplots(figsize=(6, 5), dpi=100)
    
    plt.plot(incomes, contributions_single, 
            color='blue',
            linewidth=2,
            label='Single Person')
    
    plt.plot(incomes, contributions_couple, 
            color='green',
            linewidth=2,
            label='Couple')
    
    plt.grid(True, which='major', linestyle=':', alpha=0.6, color='gray')
    ax.minorticks_on()
    ax.tick_params(axis='both', which='major', length=6, labelsize=11)
    ax.tick_params(axis='both', which='minor', length=3)

    plt.xlabel('Family Net Income ($)', fontsize=12, labelpad=10, fontweight='bold')
    plt.ylabel('QPDI Contribution ($)', fontsize=12, labelpad=10, fontweight='bold')
    plt.title('Quebec Prescription Drug Insurance Contributions 2024', fontsize=14, pad=10, fontweight='bold')
    
    def format_currency(x, p):
        return f"${format(int(x), ',')}"
    
    plt.gca().xaxis.set_major_formatter(plt.FuncFormatter(format_currency))
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(format_currency))
    
    max_contribution = qpdi.PARAMS[2024]['max_contribution']
    plt.axhline(y=max_contribution, 
                color='red',
                linestyle='--', 
                linewidth=2,
                label='Maximum Contribution')
    
    plt.ylim(0, max_contribution * 1.2)
    
    plt.text(0,
            max_contribution * 1.05,
            f'Maximum Contribution: ${max_contribution:,.2f}',
            color='red',
            fontsize=11,
            fontweight='bold')
    
    plt.legend(loc='lower right', fontsize=11)
    plt.tight_layout()
    plt.show()

    print("\nKey values for 2024:")
    print(f"Maximum Contribution: ${qpdi.PARAMS[2024]['max_contribution']:,.2f}")
    print(f"Single Person Exemption: ${qpdi.PARAMS[2024]['exemption_single']:,.2f}")
    print(f"Couple Exemption: ${qpdi.PARAMS[2024]['exemption_couple']:,.2f}")
    print(f"Base Rate (Single): {qpdi.PARAMS[2024]['base_rate_single']*100:.2f}%")
    print(f"Base Rate (Couple): {qpdi.PARAMS[2024]['base_rate_couple']*100:.2f}%")

if __name__ == "__main__":
    chart()