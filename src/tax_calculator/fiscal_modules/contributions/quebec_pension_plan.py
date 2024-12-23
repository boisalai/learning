"""
Quebec Pension Plan calculator.

Parameters reference:
    https://www.rrq.gouv.qc.ca/fr/programmes/regime_rentes/regime_chiffres/Pages/regime_chiffres.aspx
"""

from typing import Dict, List
from tax_calculator.core import TaxProgram, Family, FamilyStatus, AdultInfo

class QuebecPensionPlan(TaxProgram):
    """Quebec Pension Plan (RRQ) calculator"""

    PARAMS = {
        2025: {
            # See https://www.revenuquebec.ca/fr/entreprises/retenues-et-cotisations/trousse-employeur/principaux-changements-pour-lannee-2025-trousse-employeur/
            'max_pensionable_earnings': 71300.0, 
            'basic_exemption': 3500.0,
            'base_rate': 0.054,
            'enhancement_rate': 0.01,
            'additional_max_annual_pensionable_earnings': 81200.0,
            'additional_base_rate': 0.04,
            'max_contribution': 4735.20,
        },
        2024: {
            # See https://www.revenuquebec.ca/fr/entreprises/retenues-et-cotisations/calculer-les-retenues-a-la-source-et-vos-cotisations-demployeur/regime-de-rentes-du-quebec/maximum-du-salaire-admissible-et-taux-de-cotisation/
            # See https://www.usherbrooke.ca/srh/nouvelles/details/52328
            'max_pensionable_earnings': 68500.0, 
            'basic_exemption': 3500.0,
            'base_rate': 0.054,
            'enhancement_rate': 0.01,
            'additional_max_annual_pensionable_earnings': 73200.0,
            'additional_base_rate': 0.04,
            'max_contribution': 4348.00,
        },
        2023: {
            'max_pensionable_earnings': 66600.0,
            'basic_exemption': 3500.0,
            'base_rate': 0.054,
            'enhancement_rate': 0.01,
            'additional_max_annual_pensionable_earnings': 0.0,
            'additional_base_rate': 0.0,
            'max_contribution': 4038.40,
        }
    }

    @property
    def name(self) -> str:
        return "Quebec Pension Plan"

    @property
    def supported_years(self) -> List[int]:
        return list(self.PARAMS.keys())

    def calculate(self, family: Family) -> Dict[str, float]:
        """Calculate QPP contributions for a family"""
        self.validate_year(family.tax_year)
        params = self.PARAMS[family.tax_year]

        def calculate_contribution(income: float) -> float:
            if income <= params['basic_exemption']:
                return 0.0
                
            pensionable_earnings = min(income, params['max_pensionable_earnings'])
            rate = params['base_rate'] + params['enhancement_rate'] 
            contribution = (pensionable_earnings - params['basic_exemption']) * rate
            if income > params['max_pensionable_earnings']:
                additional_pensionable_earnings = min(income, params['additional_max_annual_pensionable_earnings']) - params['max_pensionable_earnings']
                contribution += additional_pensionable_earnings * params['additional_base_rate']

            return min(contribution, params['max_contribution'])

        contribution1 = calculate_contribution(family.adult1.gross_work_income)
        contribution2 = calculate_contribution(family.adult2.gross_work_income) if family.adult2 else 0.0

        contribution1 = -1 * round(contribution1, 2)
        contribution2 = -1 * round(contribution2, 2)

        return {
            'program': self.name,
            'tax_year': family.tax_year,
            'adult1': round(contribution1, 2),
            'adult2': round(contribution2, 2),
            'total': round(contribution1 + contribution2, 2)
        }

def chart():
    """Visualize Quebec Pension Plan contributions calculation"""
    import numpy as np
    import matplotlib.pyplot as plt

    incomes = np.arange(0, 100001, 1000)
    contributions = []
    
    qpp = QuebecPensionPlan()
    
    for income in incomes:
        adult = AdultInfo(age=30, gross_work_income=income)
        test_case = {
            "family_status": FamilyStatus.SINGLE,
            "adult1": adult,
            "tax_year": 2024
        }
        family = Family(**test_case)
        result = qpp.calculate(family)
        contributions.append(abs(result['total']))

    plt.style.use('seaborn-v0_8-paper')
    fig, ax = plt.subplots(figsize=(6, 5), dpi=100)
    
    plt.plot(incomes, contributions, 
            color='blue',
            linewidth=2,
            label='Contribution Amount')
    
    plt.grid(True, which='major', linestyle=':', alpha=0.6, color='gray')
    ax.minorticks_on()
    ax.tick_params(axis='both', which='major', length=6, labelsize=11)
    ax.tick_params(axis='both', which='minor', length=3)

    plt.xlabel('Work Income ($)', fontsize=12, labelpad=10, fontweight='bold')
    plt.ylabel('QPP Contribution ($)', fontsize=12, labelpad=10, fontweight='bold')
    plt.title('Quebec Pension Plan Contributions 2024', fontsize=14, pad=10, fontweight='bold')
    
    def format_currency(x, p):
        return f"${format(int(x), ',')}"
    
    plt.gca().xaxis.set_major_formatter(plt.FuncFormatter(format_currency))
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(format_currency))
    
    max_contribution = qpp.PARAMS[2024]['max_contribution']
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
    print(f"Maximum Pensionable Earnings: ${qpp.PARAMS[2024]['max_pensionable_earnings']:,.2f}")
    print(f"Basic Exemption: ${qpp.PARAMS[2024]['basic_exemption']:,.2f}")
    print(f"Total Contribution Rate: {qpp.PARAMS[2024]['total_rate']*100:.2f}%")
    print(f"Maximum Contribution: ${qpp.PARAMS[2024]['max_contribution']:,.2f}")

if __name__ == "__main__":
    chart()