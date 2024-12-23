"""Personal income tax.

References:
    - https://www.canada.ca/en/revenue-agency/services/tax/individuals/frequently-asked-questions-individuals/adjustment-personal-income-tax-benefit-amounts.html
    - https://cqff.com/centre-dinformation/
    - https://turboimpot.intuit.ca/ressources-impot/calculatrice-impot-quebec
"""


class FederalIncomeTax(TaxProgram):
    PARAMS = {
        2024: {
            'brackets': [
                (55867, 0.15),
                (111733, 0.2050),
                (173205, 0.26),
                (246752, 0.29),
                (float('inf'), 0.33)
            ],
