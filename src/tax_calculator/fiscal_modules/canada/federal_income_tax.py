"""Personal income tax.

References:
    - https://www.canada.ca/en/revenue-agency/services/tax/individuals/frequently-asked-questions-individuals/adjustment-personal-income-tax-benefit-amounts.html
    - https://cqff.com/centre-dinformation/
    - https://turboimpot.intuit.ca/ressources-impot/calculatrice-impot-quebec

TODO:
    - Inclure les gains en capital
    - Inclure les dividendes de source canadienne
    - Voir https://www.taxtips.ca/taxrates/canada.htm
"""

from typing import Dict, List, Any
from tax_calculator.core import TaxProgram, Family, FamilyStatus, AdultInfo, ChildInfo


class FederalIncomeTax(TaxProgram):
    PARAMS = {
        2025: {
            'brackets': [
                (57375, 0.15),
                (114750, 0.205),
                (177882, 0.26),
                (253414, 0.29),
                (float('inf'), 0.33)
            ],
            'basic_personal_amount': 15569
        },
        2024: {
            'brackets': [
                (55867, 0.15),
                (111733, 0.205),
                (173205, 0.26),
                (246752, 0.29),
                (float('inf'), 0.33),
            ],
            'basic_personal_max_amount': 15705.0,
            'basic_personal_min_amount': 14156.0,
            'basic_personal_reduction_threshold': 173205.0,
            'basic_personal_reduction_rate': 0.05,
            'medical_expenses_rate': 0.03,
            'medical_expenses_max': 2759.0,
            'age_amount': 8790.0,
        },
        2023: {
            'brackets': [
                (53359, 0.15),
                (106717, 0.205),
                (165430, 0.26),
                (235675, 0.29),
                (float('inf'), 0.33)
            ],
            'basic_personal_max_amount': 15000.0,
            'basic_personal_min_amount': 13520.0,
            'basic_personal_reduction_threshold': 172000.0,
            'basic_personal_reduction_rate': 0.05,
            'medical_expenses_rate': 0.03,
            'medical_expenses_max': 2635.0,
            'age_amount': 8396.0,
        }
    }
