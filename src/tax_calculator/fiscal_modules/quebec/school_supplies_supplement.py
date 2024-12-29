"""
Quebec School Supplies Supplement Calculator

A refundable tax credit that helps parents with the cost of school supplies.
Provides a fixed amount per eligible child between ages 4 and 16 (as of September 30).

References:
    - https://www.rrq.gouv.qc.ca/fr/enfants/Pages/supplement-achat-fournitures-scolaires.aspx
    - https://www.rcgt.com/fr/planiguide/modules/module-02-lindividu-et-la-famille/aide-aux-parents/
"""

from typing import Dict, List
from tax_calculator.core import TaxProgram, Family, FamilyStatus, AdultInfo, ChildInfo

class SchoolSuppliesSupplement(TaxProgram):
    """Calculator for Quebec's School Supplies Supplement"""
    
    PARAMS = {
        2025: {
            'amount_per_child': 121.0,
            'eligibility': {
                'min_age': 4,
                'max_age': 16,
                'reference_date': '09-30'  # September 30th
            }
        },
        2024: {
            'amount_per_child': 121.0,
            'eligibility': {
                'min_age': 4,
                'max_age': 16,
                'reference_date': '09-30'
            }
        },
        2023: {
            'amount_per_child': 116.0,
            'eligibility': {
                'min_age': 4,
                'max_age': 16,
                'reference_date': '09-30'
            }
        }
    }

    @property
    def name(self) -> str:
        return "School Supplies Supplement"

    @property
    def supported_years(self) -> List[int]:
        return list(self.PARAMS.keys())

    def _count_eligible_children(self, family: Family, params: dict) -> int:
        """Count number of eligible children (between min and max age as of reference date)."""
        if not family.children:
            return 0
            
        return sum(1 for child in family.children 
                  if params['eligibility']['min_age'] <= child.age <= params['eligibility']['max_age'])

    def calculate(self, family: Family) -> Dict[str, float]:
        """Calculate school supplies supplement for a family.
        
        The supplement:
        - Is a fixed amount per eligible child
        - Eligibility based on age as of September 30th
        - Paid as part of the family allowance payment
        """
        self.validate_year(family.tax_year)
        params = self.PARAMS[family.tax_year]

        # Count eligible children
        num_eligible = self._count_eligible_children(family, params)
        
        # Calculate total supplement
        total = num_eligible * params['amount_per_child']

        # For shared custody, split 50-50
        if family.adult2 and getattr(family, 'shared_custody', False):
            adult1_share = total / 2
            adult2_share = total / 2
        else:
            adult1_share = total
            adult2_share = 0.0

        return {
            'program': self.name,
            'tax_year': family.tax_year,
            'adult1': round(adult1_share, 2),
            'adult2': round(adult2_share, 2),
            'total': round(total, 2),
            'details': {
                'eligible_children': num_eligible,
                'amount_per_child': params['amount_per_child']
            }
        }

def chart():
    """Generate visualization of school supplies supplement calculation."""
    import matplotlib.pyplot as plt
    
    calculator = SchoolSuppliesSupplement()
    
    # Create test scenarios with different numbers of eligible children
    scenarios = {
        '1 eligible child': [ChildInfo(age=10)],
        '2 eligible children': [ChildInfo(age=5), ChildInfo(age=12)],
        '3 eligible children': [ChildInfo(age=4), ChildInfo(age=8), ChildInfo(age=15)],
        'Mixed eligibility': [ChildInfo(age=3), ChildInfo(age=7), ChildInfo(age=17)]
    }
    
    # Calculate supplements for each scenario
    results = []
    for label, children in scenarios.items():
        family = Family(
            family_status=FamilyStatus.SINGLE_PARENT,
            adult1=AdultInfo(age=35, gross_work_income=50000),
            adult2=None,
            children=children,
            tax_year=2024
        )
        result = calculator.calculate(family)
        results.append((label, result['total']))

    # Create bar plot
    plt.figure(figsize=(10, 6))
    labels, values = zip(*results)
    
    bars = plt.bar(labels, values, color='skyblue')
    
    plt.title('School Supplies Supplement by Family Composition (2024)', 
              fontsize=14, pad=20)
    plt.ylabel('Annual Supplement ($)', fontsize=12)
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'${height:,.2f}',
                ha='center', va='bottom')
    
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    # Generate visualization
    chart()
    
    # Test with sample cases
    calculator = SchoolSuppliesSupplement()
    
    test_cases = [
        {
            'name': 'Single parent - 2 eligible children',
            'family': Family(
                family_status=FamilyStatus.SINGLE_PARENT,
                adult1=AdultInfo(age=35, gross_work_income=45000),
                adult2=None,
                children=[
                    ChildInfo(age=6),
                    ChildInfo(age=8)
                ],
                tax_year=2024
            )
        },
        {
            'name': 'Couple - Mixed eligibility',
            'family': Family(
                family_status=FamilyStatus.COUPLE,
                adult1=AdultInfo(age=40, gross_work_income=60000),
                adult2=AdultInfo(age=38, gross_work_income=40000),
                children=[
                    ChildInfo(age=3),  # Not eligible
                    ChildInfo(age=5),  # Eligible
                    ChildInfo(age=17)  # Not eligible
                ],
                tax_year=2024
            )
        },
        {
            'name': 'Shared custody',
            'family': Family(
                family_status=FamilyStatus.COUPLE,
                adult1=AdultInfo(age=42, gross_work_income=55000),
                adult2=AdultInfo(age=40, gross_work_income=45000),
                children=[
                    ChildInfo(age=10),
                    ChildInfo(age=14)
                ],
                tax_year=2024,
                shared_custody=True
            )
        }
    ]
    
    print("\nSchool Supplies Supplement Test Cases:")
    print("=" * 70)
    
    for case in test_cases:
        print(f"\nScenario: {case['name']}")
        result = calculator.calculate(case['family'])
        print(f"Number of eligible children: {result['details']['eligible_children']}")
        print(f"Amount per child: ${result['details']['amount_per_child']:,.2f}")
        print(f"Total supplement: ${result['total']:,.2f}")
        if case['family'].adult2:
            print(f"Adult 1 share: ${result['adult1']:,.2f}")
            print(f"Adult 2 share: ${result['adult2']:,.2f}")
        print("-" * 70)