from typing import Dict, List
from decimal import Decimal
from tax_calculator.core import TaxProgram, Family, FamilyStatus, AdultInfo

class HealthServicesFund(TaxProgram):
    """Quebec Health Services Fund (FSS) calculator"""
    
    PARAMS = {
        2024: {
            'first_threshold': 17630.0,
            'second_threshold': 61315.0,
            'rate': 0.01,
            'base_contribution': 150.0,
            'max_contribution': 1000.0
        },
        2023: {
            'first_threshold': 16780.0,
            'second_threshold': 58350.0,
            'rate': 0.01,
            'base_contribution': 150.0,
            'max_contribution': 1000.0,
        }
    }

    @property
    def name(self) -> str:
        return "Health Services Fund"

    @property
    def supported_years(self) -> List[int]:
        return list(self.PARAMS.keys())

    def calculate(self, family: Family) -> Dict[str, float]:
        """Calculate HSF contribution for a family"""
        self.validate_year(family.tax_year)
        params = self.PARAMS[family.tax_year]

        def calculate_contribution(adult: AdultInfo) -> float:
            if not adult.is_retired or adult.age < 65:
                return 0.0

            total_income = adult.gross_retirement_income + adult.self_employed_income

            if total_income <= params['first_threshold']:
                return 0.0

            if total_income <= params['second_threshold']:
                contribution = (total_income - params['first_threshold']) * params['rate']
                return min(contribution, params['base_contribution'])

            contribution = params['base_contribution'] + (total_income - params['second_threshold']) * params['rate']
            return min(contribution, params['max_contribution'])

        contribution1 = calculate_contribution(family.adult1)
        contribution2 = calculate_contribution(family.adult2) if family.adult2 else 0.0

        return {
            'program': self.name,
            'tax_year': family.tax_year,
            'adult1': round(contribution1, 2),
            'adult2': round(contribution2, 2),
            'total': round(contribution1 + contribution2, 2)
        }

def chart():
    """Visualize Health Services Fund contributions calculation"""
    import numpy as np
    import matplotlib.pyplot as plt

    incomes = np.arange(0, 180001, 1000)
    contributions = []
    
    hsf = HealthServicesFund()
    
    for income in incomes:
        adult = AdultInfo(age=65, gross_retirement_income=income, is_retired=True)
        test_case = {
            "status": FamilyStatus.SINGLE,
            "adult1": adult,
            "tax_year": 2024
        }
        family = Family(**test_case)
        result = hsf.calculate(family)
        contributions.append(result['total'])

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

    plt.xlabel('Retirement Income ($)', fontsize=12, labelpad=10, fontweight='bold')
    plt.ylabel('Health Services Fund Contribution ($)', fontsize=12, labelpad=10, fontweight='bold')
    plt.title('Health Services Fund Contributions 2024', fontsize=13, pad=10, fontweight='bold')
    
    def format_currency(x, p):
        return f"${format(int(x), ',')}"
    
    ax.xaxis.set_major_locator(plt.MultipleLocator(50000))
    ax.xaxis.set_major_formatter(plt.FuncFormatter(format_currency))
    ax.yaxis.set_major_formatter(plt.FuncFormatter(format_currency))
    
    max_contribution = float(hsf.PARAMS[2024]['max_contribution'])
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
    print(f"First Threshold: ${float(hsf.PARAMS[2024]['first_threshold']):,.2f}")
    print(f"Second Threshold: ${float(hsf.PARAMS[2024]['second_threshold']):,.2f}")
    print(f"Contribution Rate: {float(hsf.PARAMS[2024]['rate'])*100:.2f}%")
    print(f"Maximum Contribution: ${float(hsf.PARAMS[2024]['max_contribution']):,.2f}")

if __name__ == "__main__":
    chart()
