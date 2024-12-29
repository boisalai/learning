"""
GST/HST Credit Calculator

The GST/HST credit is a tax-free quarterly payment that helps individuals and families 
with low and modest incomes offset the goods and services tax/harmonized sales tax (GST/HST) 
that they pay.

References:
    - https://www.canada.ca/en/revenue-agency/services/child-family-benefits/goods-services-tax-harmonized-sales-tax-gst-hst-credit.html
    - https://www.canada.ca/en/revenue-agency/services/child-family-benefits/goods-services-tax-harmonized-sales-tax-gst-hst-credit/gst-hst-credit-calculation-sheets.html
"""

from typing import Dict, List
from tax_calculator.core import TaxProgram, Family, FamilyStatus, AdultInfo, ChildInfo

class GSTCredit(TaxProgram):
    """Calculator for GST/HST Credit"""
    
    PARAMS = {
        2024: {
            'base_credit': {
                'basic_amount': 340,
                'spouse_or_dependent_amount': 340,
                'child_amount': 179,
                'single_supplement': {
                    'max_amount': 179,
                    'base_income': 11039,
                    'rate': 0.02
                }
            },
            'phase_out': {
                'threshold': 44324,
                'rate': 0.05
            },
            'payment_threshold': 50.0  # Minimum for quarterly payments
        },
        2023: {
            'base_credit': {
                'basic_amount': 325,
                'spouse_or_dependent_amount': 325,
                'child_amount': 171,
                'single_supplement': {
                    'max_amount': 171,
                    'base_income': 10529,
                    'rate': 0.02
                }
            },
            'phase_out': {
                'threshold': 42416,
                'rate': 0.05
            },
            'payment_threshold': 50.0
        }
    }

    @property
    def name(self) -> str:
        return "GST/HST Credit"

    @property
    def supported_years(self) -> List[int]:
        return list(self.PARAMS.keys())

    def _calculate_base_amount(self, family: Family, params: dict) -> float:
        """Calculate base GST credit amount before phase-out."""
        amount = params['base_credit']['basic_amount']  # Everyone gets basic amount
        
        # Add spouse amount if applicable
        if family.adult2:
            amount += params['base_credit']['spouse_or_dependent_amount']
            
        # Add amounts for eligible children
        if family.children:
            # For single parents, first child gets dependent amount instead of child amount
            if not family.adult2 and len(family.children) > 0:
                amount += params['base_credit']['spouse_or_dependent_amount']
                # Rest of children get child amount
                amount += params['base_credit']['child_amount'] * (len(family.children) - 1)
            else:
                # All children get child amount
                amount += params['base_credit']['child_amount'] * len(family.children)

        return amount

    def _calculate_single_supplement(self, family: Family, family_income: float, params: dict) -> float:
        """Calculate single person supplement."""
        if family.adult2:
            return 0.0
            
        # Single parents always get full supplement
        if family.children:
            return params['base_credit']['single_supplement']['max_amount']
            
        # Calculate gradual increase for single person
        if family_income <= params['base_credit']['single_supplement']['base_income']:
            return 0.0
            
        supplement = (family_income - params['base_credit']['single_supplement']['base_income']) * \
                    params['base_credit']['single_supplement']['rate']
                    
        return min(supplement, params['base_credit']['single_supplement']['max_amount'])

    def _calculate_phase_out(self, base_amount: float, family_income: float, params: dict) -> float:
        """Calculate benefit reduction based on income."""
        if family_income <= params['phase_out']['threshold']:
            return 0.0
            
        reduction = (family_income - params['phase_out']['threshold']) * params['phase_out']['rate']
        return min(reduction, base_amount)

    def calculate(self, family: Family) -> Dict[str, float]:
        """Calculate GST credit for a family.
        
        The credit is generally paid in quarterly installments in July, October, January, and April.
        If the calculated quarterly amount is less than $50, the total will be paid in July.
        """
        self.validate_year(family.tax_year)
        
        # Basic eligibility check - must be 19 or older unless has spouse or child
        if family.adult1.age < 19 and not family.adult2 and not family.children:
            return {
                'program': self.name,
                'tax_year': family.tax_year,
                'adult1': 0.0,
                'adult2': 0.0,
                'total': 0.0
            }
            
        params = self.PARAMS[family.tax_year]
        
        # Calculate family income
        family_income = (family.adult1.income + 
                        (family.adult2.income if family.adult2 else 0.0))
        
        # Calculate components
        base_amount = self._calculate_base_amount(family, params)
        single_supplement = self._calculate_single_supplement(family, family_income, params)
        total_before_reduction = base_amount + single_supplement
        
        # Apply phase-out
        reduction = self._calculate_phase_out(total_before_reduction, family_income, params)
        total_credit = max(0, total_before_reduction - reduction)
        
        # Determine payment schedule
        quarterly_amount = total_credit / 4
        is_single_payment = quarterly_amount < params['payment_threshold']
        
        # Assign credits between spouses if applicable
        if family.adult2:
            adult1_share = total_credit / 2
            adult2_share = total_credit / 2
        else:
            adult1_share = total_credit
            adult2_share = 0.0

        return {
            'program': self.name,
            'tax_year': family.tax_year,
            'adult1': round(adult1_share, 2),
            'adult2': round(adult2_share, 2),
            'total': round(total_credit, 2),
            'details': {
                'base_amount': base_amount,
                'single_supplement': single_supplement,
                'total_before_reduction': total_before_reduction,
                'reduction': reduction,
                'quarterly_amount': quarterly_amount,
                'is_single_payment': is_single_payment
            }
        }

def chart():
    """Generate visualization of GST credit calculation for different scenarios."""
    import numpy as np
    import matplotlib.pyplot as plt
    
    gst = GSTCredit()
    incomes = np.arange(0, 80001, 1000)
    
    scenarios = {
        'Single Person': Family(
            family_status=FamilyStatus.SINGLE,
            adult1=AdultInfo(age=30, gross_work_income=0),
            adult2=None,
            children=None,
            tax_year=2024
        ),
        'Couple': Family(
            family_status=FamilyStatus.COUPLE,
            adult1=AdultInfo(age=30, gross_work_income=0),
            adult2=AdultInfo(age=30, gross_work_income=0),
            children=None,
            tax_year=2024
        ),
        'Single Parent with Child': Family(
            family_status=FamilyStatus.SINGLE_PARENT,
            adult1=AdultInfo(age=30, gross_work_income=0),
            adult2=None,
            children=[ChildInfo(age=5)],
            tax_year=2024
        ),
        'Couple with 2 Children': Family(
            family_status=FamilyStatus.COUPLE,
            adult1=AdultInfo(age=30, gross_work_income=0),
            adult2=AdultInfo(age=30, gross_work_income=0),
            children=[ChildInfo(age=5), ChildInfo(age=7)],
            tax_year=2024
        )
    }
    
    plt.figure(figsize=(12, 6))
    
    for label, family in scenarios.items():
        credits = []
        for income in incomes:
            if family.adult2:
                # Split income 60/40 between spouses
                family.adult1.gross_work_income = income * 0.6
                family.adult2.gross_work_income = income * 0.4
            else:
                family.adult1.gross_work_income = income
            
            result = gst.calculate(family)
            credits.append(result['total'])
            
        plt.plot(incomes, credits, label=label, linewidth=2)
    
    plt.xlabel('Family Income ($)')
    plt.ylabel('Annual Credit ($)')
    plt.title('GST/HST Credit by Family Type and Income (2024)')
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    plt.gca().xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    # Generate visualization
    chart()
    
    # Test with sample families
    calculator = GSTCredit()
    
    test_cases = [
        # Single person
        Family(
            family_status=FamilyStatus.SINGLE,
            adult1=AdultInfo(age=30, gross_work_income=25000),
            adult2=None,
            children=None,
            tax_year=2024
        ),
        # Couple with no children
        Family(
            family_status=FamilyStatus.COUPLE,
            adult1=AdultInfo(age=35, gross_work_income=30000),
            adult2=AdultInfo(age=33, gross_work_income=20000),
            children=None,
            tax_year=2024
        ),
        # Single parent with child
        Family(
            family_status=FamilyStatus.SINGLE_PARENT,
            adult1=AdultInfo(age=40, gross_work_income=35000),
            adult2=None,
            children=[ChildInfo(age=10)],
            tax_year=2024
        )
    ]
    
    print("\nGST/HST Credit Test Cases:")
    print("=" * 50)
    
    for case in test_cases:
        print(f"\nFamily Status: {case.family_status.name}")
        result = calculator.calculate(case)
        print(f"Total Credit: ${result['total']:,.2f}")
        print(f"Base Amount: ${result['details']['base_amount']:,.2f}")
        print(f"Single Supplement: ${result['details']['single_supplement']:,.2f}")
        if result['details']['is_single_payment']:
            print("Payment: Single payment in July")
        else:
            print(f"Payment: Quarterly payments of ${result['details']['quarterly_amount']:,.2f}")
        print("-" * 50)