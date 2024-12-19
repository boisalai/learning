"""
Quebec Prescription Drug Insurance calculator.

Parameters reference:
    https://cffp.recherche.usherbrooke.ca/outils-ressources/guide-mesures-fiscales/cotisation-regime-assurance-medicaments-quebec/
"""

from typing import Dict, List
from tax_calculator.core import TaxProgram, Family, FamilyStatus, AdultInfo

class QuebecPrescriptionDrugInsurance(TaxProgram):
    """Quebec Prescription Drug Insurance (RAMQ) calculator"""

    PARAMS = {
        2024: {
            'max_contribution': 731.0,
            'exemption_single': 19790.0,
            'exemption_couple': 32080.0,
            'exemption_single_one_child': 32080.0,
            'exemption_single_multiple_children': 36185.0,
            'exemption_couple_one_child': 36185.0,
            'exemption_couple_multiple_children': 39975.0,
            'first_threshold': 5000.0,
            'base_rate_single': 0.0747,  # r11 pour personne seule 
            'additional_rate_single': 0.1122,  # r12 pour personne seule
            'base_rate_couple': 0.0375,  # r21 pour couple
            'additional_rate_couple': 0.0562,  # r22 pour couple
            'base_max_single': 373.50,
            'base_max_couple': 186.75,
            'monthly_adjustment': 60.92
        },
        2023: {
            'max_contribution': 720.50,
            'exemption_single': 18910.0,
            'exemption_couple': 30640.0,
            'exemption_single_one_child': 30640.0,
            'exemption_single_multiple_children': 34545.0,
            'exemption_couple_one_child': 34545.0,
            'exemption_couple_multiple_children': 38150.0,
            'first_threshold': 5000.0,
            'base_rate_single': 0.0747,
            'additional_rate_single': 0.1122,
            'base_rate_couple': 0.0375,
            'additional_rate_couple': 0.0562,
            'base_max_single': 373.50,
            'base_max_couple': 186.75,
            'monthly_adjustment': 60.04
        }
    }

    @property
    def name(self) -> str:
        return "Quebec Prescription Drug Insurance"

    @property
    def supported_years(self) -> List[int]:
        return list(self.PARAMS.keys())

    def calculate(self, family: Family) -> Dict[str, float]:
        """Calculate QPDI contributions for a family"""
        self.validate_year(family.tax_year)
        params = self.PARAMS[family.tax_year]

        # Determine family type and corresponding exemption
        is_couple = family.adult2 is not None
        num_children = len(family.children) if family.children else 0

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

        # Calculate family net income
        # TODO À remplacer avec le revenu familial net à l'impôt du Québec
        family_net_income = family.adult1.income
        if family.adult2:
            family_net_income += family.adult2.income

        # If income is below exemption, no contribution
        if family_net_income <= exemption:
            return {
                'program': self.name,
                'tax_year': family.tax_year,
                'adult1': 0.0,
                'adult2': 0.0,
                'total': 0.0
            }

        # Calculate excess income
        excess_income = family_net_income - exemption

        # Calculate contribution based on family type
        if is_couple:
            if excess_income <= params['first_threshold']:
                contribution = excess_income * params['base_rate_couple']
            else:
                contribution = (params['first_threshold'] * params['base_rate_couple'] +
                              (excess_income - params['first_threshold']) * params['additional_rate_couple'])
            contribution = min(contribution, params['base_max_couple'])
        else:
            if excess_income <= params['first_threshold']:
                contribution = excess_income * params['base_rate_single']
            else:
                contribution = (params['first_threshold'] * params['base_rate_single'] +
                              (excess_income - params['first_threshold']) * params['additional_rate_single'])
            contribution = min(contribution, params['base_max_single'])

        # Add monthly adjustment and ensure not exceeding maximum contribution
        contribution += params['monthly_adjustment']
        contribution = min(contribution, params['max_contribution'])
        contribution = -1 * contribution  # Make negative as it's a deduction

        return {
            'program': self.name,
            'tax_year': family.tax_year,
            'adult1': round(contribution, 2) if not family.adult2 else round(contribution / 2, 2),
            'adult2': 0.0 if not family.adult2 else round(contribution / 2, 2),
            'total': round(contribution, 2)
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
            "status": FamilyStatus.SINGLE,
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
            "status": FamilyStatus.COUPLE,
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