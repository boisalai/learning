"""
Work Premium

Parameters:
    - https://cffp.recherche.usherbrooke.ca/outils-ressources/guide-mesures-fiscales/credit-impot-remboursable-prime-travail/
    - https://www.revenuquebec.ca/fr/citoyens/credits-dimpot/credits-dimpot-relatifs-a-la-prime-au-travail/montant/
    - https://cdn-contenu.quebec.ca/cdn-contenu/adm/min/finances/publications-adm/parametres/AUTFR_RegimeImpot2024.pdf
"""

from typing import Dict, List, Any
from tax_calculator.core import TaxProgram, Family, FamilyStatus, AdultInfo


class WorkPremium(TaxProgram):
    PARAMS = {
        2025: {
            'general': {
                'person_alone': {
                    'excluded_income': 2400.0,
                    'rate': 0.116,
                    'max_amount': 1185.52,
                    'reduction_threshold': 12620.0,
                    'reduction_rate': 0.10
                },
                'couple_no_children': {
                    'excluded_income': 3600.0,
                    'rate': 0.116,
                    'max_amount': 1848.34,
                    'reduction_threshold': 19534.0,
                    'reduction_rate': 0.10
                },
                'single_parent': {
                    'excluded_income': 2400.0,
                    'rate': 0.30,
                    'max_amount': 3066.00,
                    'reduction_threshold': 12620.0,
                    'reduction_rate': 0.10
                },
                'couple_with_children': {
                    'excluded_income': 3600.0,
                    'rate': 0.25,
                    'max_amount': 3983.50,
                    'reduction_threshold': 19534.0,
                    'reduction_rate': 0.10
                }
            },
            'adapted': {
                'person_alone': {
                    'excluded_income': 1200,
                    'rate': 0.136,
                    'max_amount': 2257.33,
                    'reduction_threshold': 17798.0,
                    'reduction_rate': 0.10
                },
                'couple_no_children': {
                    'excluded_income': 1200,
                    'rate': 0.136,
                    'max_amount': 3501.46,
                    'reduction_threshold': 26946.0,
                    'reduction_rate': 0.10
                },
                'single_parent': {
                    'excluded_income': 1200,
                    'rate': 0.25,
                    'max_amount': 4149.50,
                    'reduction_threshold': 17798.0,
                    'reduction_rate': 0.10
                },
                'couple_with_children': {
                    'excluded_income': 1200,
                    'rate': 0.20,
                    'max_amount': 5149.20,
                    'reduction_threshold': 26946.0,
                    'reduction_rate': 0.10
                }
            }
        },
        2024: {
            'general': {
                'person_alone': {
                    'excluded_income': 2400.0,
                    'rate': 0.116,
                    'max_amount': 1152.34,
                    'reduction_threshold': 12334.0,
                    'reduction_rate': 0.10
                },
                'couple_no_children': {
                    'excluded_income': 3600.0,
                    'rate': 0.116,
                    'max_amount': 1797.07,
                    'reduction_threshold': 19092.0,
                    'reduction_rate': 0.10
                },
                'single_parent': {
                    'excluded_income': 2400.0,
                    'rate': 0.30,
                    'max_amount': 2980.20,
                    'reduction_threshold': 12334.0,
                    'reduction_rate': 0.10
                },
                'couple_with_children': {
                    'excluded_income': 3600.0,
                    'rate': 0.25,
                    'max_amount': 3873.0,
                    'reduction_threshold': 19092.0,
                    'reduction_rate': 0.10
                }
            },
            'adapted': {
                'person_alone': {
                    'excluded_income': 1200.0,
                    'rate': 0.136,
                    'max_amount': 2200.21,
                    'reduction_threshold': 17378.0,
                    'reduction_rate': 0.10
                },
                'couple_no_children': {
                    'excluded_income': 1200.0,
                    'rate': 0.136,
                    'max_amount': 3414.96,
                    'reduction_threshold': 26310.0,
                    'reduction_rate': 0.10
                },
                'single_parent': {
                    'excluded_income': 1200.0,
                    'rate': 0.25,
                    'max_amount': 4044.50,
                    'reduction_threshold': 17378.0,
                    'reduction_rate': 0.10
                },
                'couple_with_children': {
                    'excluded_income': 1200.0,
                    'rate': 0.20,
                    'max_amount': 5022.0,
                    'reduction_threshold': 26310.0,
                    'reduction_rate': 0.10
                }
            }
        },
        2023: {
            'general': {
                'person_alone': {
                    'excluded_income': 2400,
                    'rate': 0.116,
                    'max_amount': 1095.27,
                    'reduction_threshold': 11842.0,
                    'reduction_rate': 0.10
                },
                'couple_no_children': {
                    'excluded_income': 3600,
                    'rate': 0.116,
                    'max_amount': 1709.61,
                    'reduction_threshold': 18338.0,
                    'reduction_rate': 0.10
                },
                'single_parent': {
                    'excluded_income': 2400,
                    'rate': 0.30,
                    'max_amount': 2832.60,
                    'reduction_threshold': 11842.0,
                    'reduction_rate': 0.10
                },
                'couple_with_children': {
                    'excluded_income': 3600,
                    'rate': 0.25,
                    'max_amount': 3684.50,
                    'reduction_threshold': 18338.0,
                    'reduction_rate': 0.10
                }
            },
            'adapted': {
                'person_alone': {
                    'excluded_income': 1200.0,
                    'rate': 0.136,
                    'max_amount': 2101.74,
                    'reduction_threshold': 16654.0,
                    'reduction_rate': 0.10
                },
                'couple_no_children': {
                    'excluded_income': 1200.0,
                    'rate': 0.136,
                    'max_amount': 3263.73,
                    'reduction_threshold': 25198.0,
                    'reduction_rate': 0.10
                },
                'single_parent': {
                    'excluded_income': 1200.0,
                    'rate': 0.25,
                    'max_amount': 3863.50,
                    'reduction_threshold': 16654.0,
                    'reduction_rate': 0.10
                },
                'couple_with_children': {
                    'excluded_income': 1200.0,
                    'rate': 0.20,
                    'max_amount': 4799.60,
                    'reduction_threshold': 25198.0,
                    'reduction_rate': 0.10
                }
            }
        }
    }

    @property
    def name(self) -> str:
        return "Work Premium"

    @property 
    def supported_years(self) -> List[int]:
        return list(self.PARAMS.keys())

    def _get_family_type(self, family: Family) -> str:
        """Determine family type for parameter selection"""
        has_children = bool(family.children and len(family.children) > 0)
        has_partner = family.adult2 is not None

        if has_partner:
            if has_children:
                return 'couple_with_children'
            return 'couple_no_children'
        else:
            if has_children:
                return 'single_parent'
            return 'person_alone'

    def _calculate_premium(self, family: Family, params: dict, work_income: float, has_disability: bool = False) -> float:
        """Calculate work premium amount for given parameters"""
        family_type = self._get_family_type(family)
        
        # Select regular or adapted parameters based on disability status
        premium_type = 'adapted' if has_disability else 'general'
        family_params = params[premium_type][family_type]

        # Calculate eligible work income
        eligible_income = max(0, work_income - family_params['excluded_income'])

        # Calculate initial premium
        premium = min(
            family_params['max_amount'],
            eligible_income * family_params['rate']
        )

        # Calculate total family income for reduction phase
        family_income = family.adult1.income
        if family.adult2:
            family_income += family.adult2.income

        # Apply reduction if income exceeds threshold
        if family_income > family_params['reduction_threshold']:
            reduction = (family_income - family_params['reduction_threshold']) * family_params['reduction_rate']
            premium = max(0, premium - reduction)

        return premium

    def calculate(self, family: Family) -> Dict[str, float]:
        """Calculate work premium benefit for a family"""
        self.validate_year(family.tax_year)
        params = self.PARAMS[family.tax_year]

        # Check eligibility conditions
        if family.adult1.age < 18 and not family.children and not family.adult2:
            return {
                'program': self.name,
                'tax_year': family.tax_year,
                'adult1': 0.0,
                'adult2': 0.0,
                'total': 0.0
            }

        # Calculate regular and adapted premiums
        regular_premium = self._calculate_premium(
            family,
            params,
            family.adult1.gross_work_income + (family.adult2.gross_work_income if family.adult2 else 0)
        )

        # Calculate adapted premium if eligible (disability criteria)
        has_disability = getattr(family.adult1, 'has_disability', False) or (
            family.adult2 and getattr(family.adult2, 'has_disability', False)
        )
        
        adapted_premium = 0.0
        if has_disability:
            adapted_premium = self._calculate_premium(
                family,
                params,
                family.adult1.gross_work_income + (family.adult2.gross_work_income if family.adult2 else 0),
                has_disability=True
            )

        # Use the higher of the two premiums
        total_premium = max(regular_premium, adapted_premium)

        # Split benefit between adults if couple
        if family.adult2:
            adult1_income = family.adult1.gross_work_income
            adult2_income = family.adult2.gross_work_income
            total_income = adult1_income + adult2_income
            if total_income > 0:
                adult1_share = (adult1_income / total_income) * total_premium
                adult2_share = (adult2_income / total_income) * total_premium
            else:
                adult1_share = total_premium / 2
                adult2_share = total_premium / 2
        else:
            adult1_share = total_premium
            adult2_share = 0.0

        return {
            'program': self.name,
            'tax_year': family.tax_year,
            'adult1': round(adult1_share, 2),
            'adult2': round(adult2_share, 2),
            'total': round(total_premium, 2)
        }