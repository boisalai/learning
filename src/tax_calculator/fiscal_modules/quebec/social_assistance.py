
"""
Social Assistance Program Calculator.
Implements aid social and solidarity social benefits calculation.

Parameters reference:
    - https://www.quebec.ca/famille-et-soutien-aux-personnes/aide-sociale-et-solidarite-sociale
"""

from typing import Dict, List, Any
from tax_calculator.core import TaxProgram, Family, FamilyStatus, AdultInfo


class SocialAssistance(TaxProgram):
    """Quebec Social Assistance Program calculator"""
    
    PARAMS = {
        2024: {
            'aide_sociale': {  # Regular social assistance
                'single_adult': {
                    'base': 762,
                    'adjustment': 45,
                    'temp_constraint_amount': 166
                },
                'couple': {
                    'base': 1179,
                    'adjustment': 45,
                    'temp_constraint_amount': 166
                },
                'student_spouse': {
                    'base': 210,
                    'adjustment': 45,
                    'temp_constraint_amount': 166
                }
            },
            'solidarite_sociale': {  # Social solidarity
                'single_adult': {
                    'base': 1158,
                    'adjustment': 103,
                },
                'couple': {
                    'base': 1731,
                    'adjustment': 118,
                },
                'student_spouse': {
                    'base': 586,
                    'adjustment': 103,
                }
            },
            'work_income_exemption': {
                'single': 200,
                'couple': 300
            }
        },
        2023: {
            'aide_sociale': {
                'single_adult': {
                    'base': 770,
                    'adjustment': 50,
                    'temp_constraint_amount': 153
                },
                'couple': {
                    'base': 1167,
                    'adjustment': 50,
                    'temp_constraint_amount': 264
                },
                'student_spouse': {
                    'base': 205,
                    'adjustment': 40,
                    'temp_constraint_amount': 153
                }
            },
            'solidarite_sociale': {
                'single_adult': {
                    'base': 1121,
                    'adjustment': 84,
                },
                'couple': {
                    'base': 1675,
                    'adjustment': 90,
                },
                'student_spouse': {
                    'base': 567,
                    'adjustment': 94,
                }
            },
            'work_income_exemption': {
                'single': 200,
                'couple': 300
            }
        }
    }

    @property
    def name(self) -> str:
        return "Social Assistance"

    @property
    def supported_years(self) -> List[int]:
        return list(self.PARAMS.keys())

    def _get_family_type(self, family: Family) -> str:
        """Determine family type for parameter selection"""
        if family.adult2:
            if getattr(family.adult2, 'is_student', False):
                return 'student_spouse'
            return 'couple'
        return 'single_adult'

    def _calculate_aid_amount(self, family: Family, params: dict) -> float:
        """Calculate the base social assistance amount based on family situation"""
        family_type = self._get_family_type(family)
        has_temp_constraints = (getattr(family.adult1, 'has_temp_constraints', False) or 
                              (family.adult2 and getattr(family.adult2, 'has_temp_constraints', False)))
        has_severe_constraints = (getattr(family.adult1, 'has_severe_constraints', False) or 
                                (family.adult2 and getattr(family.adult2, 'has_severe_constraints', False)))

        # Determine which program applies
        if has_severe_constraints:
            program_params = params['solidarite_sociale'][family_type]
            base_amount = program_params['base'] + program_params['adjustment']
        else:
            program_params = params['aide_sociale'][family_type]
            base_amount = program_params['base'] + program_params['adjustment']
            if has_temp_constraints:
                base_amount += program_params['temp_constraint_amount']

        return base_amount

    def _apply_work_exemption(self, family: Family, base_amount: float, params: dict) -> float:
        """Apply work income exemption and calculate final benefit"""
        # Determine work income exemption threshold
        exemption_type = 'couple' if family.adult2 else 'single'
        exemption = params['work_income_exemption'][exemption_type]

        # Calculate total work income
        work_income = family.adult1.gross_work_income
        if family.adult2:
            work_income += family.adult2.gross_work_income

        # Apply reduction if work income exceeds exemption
        if work_income > exemption:
            reduction = work_income - exemption
            base_amount = max(0, base_amount - reduction)

        return base_amount

    def calculate(self, family: Family) -> Dict[str, float]:
        """Calculate social assistance benefit for a family."""
        self.validate_year(family.tax_year)
        params = self.PARAMS[family.tax_year]

        # Calculate base amount
        base_amount = self._calculate_aid_amount(family, params)

        # Apply work income exemption
        final_amount = self._apply_work_exemption(family, base_amount, params)

        # Split between partners if applicable
        if family.adult2:
            adult1_amount = final_amount / 2
            adult2_amount = final_amount / 2
        else:
            adult1_amount = final_amount
            adult2_amount = 0.0

        return {
            'program': self.name,
            'tax_year': family.tax_year,
            'adult1': round(adult1_amount, 2),
            'adult2': round(adult2_amount, 2),
            'total': round(final_amount, 2),
            'details': {
                'base_amount': base_amount,
                'work_income_reduction': base_amount - final_amount if base_amount > final_amount else 0,
                'has_severe_constraints': (getattr(family.adult1, 'has_severe_constraints', False) or 
                                        (family.adult2 and getattr(family.adult2, 'has_severe_constraints', False))),
                'has_temp_constraints': (getattr(family.adult1, 'has_temp_constraints', False) or 
                                      (family.adult2 and getattr(family.adult2, 'has_temp_constraints', False)))
            }
        }