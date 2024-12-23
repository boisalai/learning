"""
Social Assistance Program

Parameters:
    - https://www.quebec.ca/famille-et-soutien-aux-personnes/aide-sociale-et-solidarite-sociale/information-aide-financiere/montants-prestations-aide-sociale
"""

from typing import Dict, List, Any
from tax_calculator.core import TaxProgram, Family, FamilyStatus, AdultInfo


class SocialAssistance(TaxProgram):
    PARAMS = {
        2025: {
            '?': 65700.0,
        },
        2024: {
            '?': 65700.0,
        },
        2023: {
            '?': 65700.0,
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

        benefit1 = 0.0
        benefit2 = 0.0
        
        return {
            'program': self.name,
            'tax_year': family.tax_year,
            'adult1': benefit1,
            'adult2': benefit2,
            'total': benefit1 + benefit2,
        }

if __name__ == "__main__":
    social_assistance = SocialAssistance()
    sa = social_assistance.calculate(Family(
        tax_year=2024,
        family_status=FamilyStatus.SINGLE,
        adult1=AdultInfo(age=30, gross_work_income=0.0),
        adult2=None,
        children=[]
    ))

    print(sa)