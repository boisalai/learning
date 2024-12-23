"""
Employment Insurance premiums calculator.

Parameters reference:
    https://www.canada.ca/en/revenue-agency/services/tax/businesses/topics/payroll/payroll-deductions-contributions/employment-insurance-ei/ei-premium-rates-maximums.html
"""

from typing import Dict, List, Any
from tax_calculator.core import TaxProgram, Family, FamilyStatus, AdultInfo


class EmploymentInsurance(TaxProgram):
    PARAMS = {
        2025: {
            'max_insurable_earnings': 65700.0,
            'employee_rate': 0.0131,
            'max_employee_contribution': 860.67,
            'min_insurable_earnings': 2000,
            'employer_rate_multiplier': 1.4
        },
        2024: {
            'max_insurable_earnings': 63200.0,
            'employee_rate': 0.0132,
            'max_employee_contribution': 834.24,
            'min_insurable_earnings': 2000,
            'employer_rate_multiplier': 1.4
        },
        2023: {
            'max_insurable_earnings': 61500.0,
            'employee_rate': 0.0127,
            'max_employee_contribution': 781.05,
            'min_insurable_earnings': 2000,
            'employer_rate_multiplier': 1.4
        }
    }

    @property
    def name(self) -> str:
        return "Employment Insurance"

    @property
    def supported_years(self) -> List[int]:
        return list(self.PARAMS.keys())

    def calculate(self, family: Family) -> Dict[str, float]:
        self.validate_year(family.tax_year)
        params = self.PARAMS[family.tax_year]

        def calculate_premium(income: float) -> float:
            if income <= params['min_insurable_earnings']:
                return 0

            insurable_earnings = min(income, params['max_insurable_earnings'])
            return min(insurable_earnings * params['employee_rate'], params['max_employee_contribution'])

        premium1 = calculate_premium(family.adult1.gross_work_income)
        premium2 = calculate_premium(family.adult2.gross_work_income) if family.adult2 else 0

        premium1 = -1 * round(premium1, 2)
        premium2 = -1 * round(premium2, 2)
        
        return {
            'program': self.name,
            'tax_year': family.tax_year,
            'adult1': premium1,
            'adult2': premium2,
            'total': premium1 + premium2,
        }

def chart():
    """Visualize Employment Insurance premiums calculation"""
    import numpy as np
    import matplotlib.pyplot as plt

    # Create arrays for incomes and corresponding premiums
    incomes = np.arange(0, 100001, 1000)
    premiums = []
    
    ei = EmploymentInsurance()
    
    # Calculate premium for each income level
    for income in incomes:
        adult = AdultInfo(age=30, gross_work_income=income)
        test_case = {
            "family_status": FamilyStatus.SINGLE,
            "adult1": adult,
            "tax_year": 2024
        }
        family = Family(**test_case)
        result = ei.calculate(family)
        premiums.append(abs(result['total']))

    # Set the style to seaborn paper
    plt.style.use('seaborn-v0_8-paper')
    fig, ax = plt.subplots(figsize=(6, 5), dpi=100)
    
    # Plot main line
    plt.plot(incomes, premiums, 
            color='blue',
            linewidth=2,
            label='Premium Amount')
    
    # Configure grid for major lines only
    plt.grid(True, which='major', linestyle=':', alpha=0.6, color='gray')
    
    # Enable minor ticks on axes
    ax.minorticks_on()
    
    # Configure tick parameters
    ax.tick_params(axis='both', which='major', length=6, labelsize=11)  # Increased from default
    ax.tick_params(axis='both', which='minor', length=3)

    # Add labels and title with bold font
    plt.xlabel('Work Income ($)', fontsize=12, labelpad=10, fontweight='bold')  # Increased from 10
    plt.ylabel('Employment Insurance Premium ($)', fontsize=12, labelpad=10, fontweight='bold')  # Increased from 10
    plt.title('Employment Insurance Premiums 2024', fontsize=14, pad=10, fontweight='bold')  # Increased from 12
    
    # Format axis with thousand separator
    def format_currency(x, p):
        return f"${format(int(x), ',')}"
    
    plt.gca().xaxis.set_major_formatter(plt.FuncFormatter(format_currency))
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(format_currency))
    
    # Add maximum contribution line
    max_contribution = ei.PARAMS[2024]['max_employee_contribution']
    plt.axhline(y=max_contribution, 
                color='red',
                linestyle='--', 
                linewidth=2,
                label='Maximum Contribution')
    
    # Set y-axis limit to provide space for label
    plt.ylim(0, max_contribution * 1.2)  # 20% more than max contribution
    
    # Add maximum contribution text with larger font
    plt.text(0,  # Start of x-axis
            max_contribution * 1.05,  # 5% above the line
            f'Maximum Contribution: ${max_contribution:,.2f}',
            color='red',
            fontsize=11,  # Increased from 10
            fontweight='bold')
    
    # Add legend with increased font size
    plt.legend(loc='lower right', fontsize=11)  # Increased from 10
    
    # Adjust layout
    plt.tight_layout()
    
    # Show the plot
    plt.show()

    # Print key values
    print("\nKey values for 2024:")
    print(f"Maximum Insurable Earnings: ${ei.PARAMS[2024]['max_insurable_earnings']:,.2f}")
    print(f"Contribution Rate: {ei.PARAMS[2024]['employee_rate']*100:.2f}%")
    print(f"Maximum Contribution: ${ei.PARAMS[2024]['max_employee_contribution']:,.2f}")

if __name__ == "__main__":
    chart()