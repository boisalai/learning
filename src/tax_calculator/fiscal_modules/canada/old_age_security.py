"""
Old Age Security (OAS)

- Les paramètres sont révisés trimestriellement en fonction de l'indice des prix à la consommation.
- Cette implémentation:
    - Calcule les taux moyens annuels à partir des taux trimestriels
    - Calcule la SV de base pour chaque adulte admissible (65+ ans)
    - Applique l'impôt de récupération de la SV si le revenu dépasse le seuil
    - Calcule le SRG en tenant compte:
        - Des exemptions de revenu de travail
        - Des différents seuils selon la situation familiale
        - Du partage du SRG pour les couples
    - Calcule l'Allocation au conjoint si applicable (60-64 ans)
    - Retourne les montants pour chaque adulte avec les détails
- La méthode gère toutes les situations familiales possibles:
    - Personne seule de 65 ans et plus
    - Couple où les deux ont 65 ans et plus
    - Couple où un seul a 65 ans et plus (cas de l'Allocation)
- Les montants sont proratisés en fonction des changements trimestriels des prestations et l'implémentation
  tient compte des seuils de récupération et des exemptions de revenu appropriés.

References
    - [Sécurité de la vieillesse (SV) - Montants maximaux mensuels selon le type de prestations et le trimestre](https://ouvert.canada.ca/data/fr/dataset/ff1e4882-685c-4518-b741-c3cf9bb74c3e)
    - [Impôt de récupération de la Sécurité de la vieillesse](https://www.canada.ca/fr/services/prestations/pensionspubliques/rpc/securite-vieillesse/impot-recuperation.html)
    - [Statistiques concernant le programme de la Sécurité de la vieillesse et le Régime de pensions du Canada](https://www.canada.ca/fr/emploi-developpement-social/programmes/pensions/pension.html)
    - [Déclaration des revenus pour la Sécurité de la vieillesse (DRSV)](https://www.canada.ca/fr/agence-revenu/services/impot/impot-international-non-residents/particuliers-depart-canada-entree-canada-non-residents/declaration-revenus-securite-vieillesse-drsv.html)
    - [Impôt de récupération de la Sécurité de la vieillesse](https://www.canada.ca/fr/services/prestations/pensionspubliques/rpc/securite-vieillesse/impot-recuperation.html)
    - [Prestations du programme fédéral de la Sécurité de la vieillesse](https://www.rrq.gouv.qc.ca/fr/flashretraiteqc/Pages/capsule_retraite_007.aspx)
    - [Rajustement de montants en fonction de l’indexation pour l’impôt des particuliers et les prestations](https://www.canada.ca/fr/agence-revenu/services/impot/particuliers/foire-questions-particuliers/rajustement-montants-fonction-indexation-impot-particuliers-prestations.html)
    - [RCGT, Pension de la sécurité de vieillesse](https://www.rcgt.com/fr/planiguide/modules/module-12-programmes-et-charges-sociales/pension-de-la-securite-de-vieillesse/)
    - [SSQ Assurance. Bulletin 2020 des lois sociales](https://ssq.ca/fr/media/6421/download)
    - [Pension de la Sécurité de vieillesse : Aperçu](https://www.canada.ca/fr/services/prestations/pensionspubliques/rpc/securite-vieillesse.html)
    - [Régime de pensions du Canada, Sécurité de la vieillesse, bulletin statistique](http://www.publications.gc.ca/site/fra/9.500184/publication.html)
    - [Tableau des montants des prestations](https://www.canada.ca/content/dam/canada/employment-social-development/migration/documents/assets/portfolio/docs/en/cpp/oas/sv-oas-jan-mar-2021.pdf)

TODO: Ajouter le supplément de revenu garanti (65 ans et plus)
"""

from typing import Dict, List, Any
from tax_calculator.core import TaxProgram, Family, FamilyStatus, AdultInfo


class OldAgeSecurity(TaxProgram):
    PARAMS = {
        2024: {
            'jan_to_march': {
                'oas_under_75': 713.34,  # Old Age Security Pension (age 65 to 74)
                'oas_over_75': 784.67,  # Old Age Security Pension (age 75 and over)
                'gis_single_top_up': 165.04,  # Guaranteed Income Supplement, Single, Top-Up Amount
                'gis_single_max': 1065.47,  # Guaranteed Income Supplement, Single, Maximum Amount
                'gis_couple_top_up': 46.76,  # Guaranteed Income Supplement, Couple, Top-Up Amount
                'gis_couple_max': 641.35,  # Guaranteed Income Supplement, Couple, Maximum Amount
                'allowance_top_up': 46.76,  # Allowance, Married, Top-Up Amount
                'allowance_max': 1354.69,  # Allowance, Married, Maximum Amount
                'gis_single_threshold': 21624.0,  # Income threshold for single, widowed or divorced
                'gis_couple_threshold': 28560.0,  # Income threshold for couple with full OAS pension
                'allowance_threshold': 39984.0,   # Income threshold when spouse receives Allowance
            },
            'april_to_june': {
                'oas_under_75': 713.34,
                'oas_over_75': 784.67,
                'gis_single_top_up': 165.04,
                'gis_single_max': 1065.47,
                'gis_couple_top_up': 46.76,
                'gis_couple_max': 641.35,
                'allowance_top_up': 46.76,
                'allowance_max': 1354.69,
                'gis_single_threshold': 21624.0,  # Income threshold for single, widowed or divorced
                'gis_couple_threshold': 28560.0,  # Income threshold for couple with full OAS pension
                'allowance_threshold': 39984.0,   # Income threshold when spouse receives Allowance
            },
            'july_to_sept': {
                'oas_under_75': 718.33,
                'oas_over_75': 790.16,
                'gis_single_top_up': 166.20,
                'gis_single_max': 1072.93,
                'gis_couple_top_up': 47.09,
                'gis_couple_max': 645.84,
                'allowance_top_up': 47.09,
                'allowance_max': 1364.17,
                'gis_single_threshold': 21768.0,  # Income threshold for single, widowed or divorced
                'gis_couple_threshold': 28752.0,  # Income threshold for couple with full OAS pension
                'allowance_threshold': 40272.0,   # Income threshold when spouse receives Allowance
            },
            'oct_to_dec': {
                'oas_under_75': 727.67,
                'oas_over_75': 800.44,
                'gis_single_top_up': 168.36,
                'gis_single_max': 1086.88,
                'gis_couple_top_up': 47.70,
                'gis_couple_max': 654.23,
                'allowance_top_up': 47.70,
                'allowance_max': 1381.90,
                'gis_single_threshold': 22056.0,  # Income threshold for single, widowed or divorced
                'gis_couple_threshold': 29136.0,  # Income threshold for couple with full OAS pension
                'allowance_threshold': 40800.0,   # Income threshold when spouse receives Allowance
            },
            'oas_recovery_threshold': 90997.0,  # OAS Recovery Threshold
            'oas_recovery_rate': 0.15,  # OAS Recovery Rate
            'gis_work_income_deduction': 5000.0,  # GIS Work Deduction
            'gis_partial_work_income_exemption': 5000.0,  # GIS Partial Work Exemption
            'gis_partial_work_income_rate': 0.5,  # GIS Partial Work Deduction
        },
        2023: {
            'jan_to_march': {
                # https://www.canada.ca/en/employment-social-development/programs/pensions/pension/statistics/2023-quarterly-january-march.html
                'oas_under_75': 687.56,
                'oas_over_75': 756.32,
                'gis_single_top_up': 159.07,
                'gis_single_max': 1026.96,
                'gis_couple_top_up': 45.06,
                'gis_couple_max': 618.15,
                'allowance_top_up': 45.06,
                'allowance_max': 1556.51,
                'gis_single_threshold': 20832.0,  # Income threshold for single, widowed or divorced
                'gis_couple_threshold': 27552.0,  # Income threshold for couple with full OAS pension
                'allowance_threshold': 38592.0,   # Income threshold when spouse receives Allowance
            },
            'april_to_june': {
                # https://www.canada.ca/en/employment-social-development/programs/pensions/pension/statistics/2023-quarterly-april-june.html
                'oas_under_75': 691.00,
                'oas_over_75': 760.10,
                'gis_single_top_up': 159.87,
                'gis_single_max': 1032.10,
                'gis_couple_top_up': 45.29,
                'gis_couple_max': 621.25,
                'allowance_top_up': 45.29,
                'allowance_max': 1312.25,
                'gis_single_threshold': 20952.0,  # Income threshold for single, widowed or divorced
                'gis_couple_threshold': 27648.0,  # Income threshold for couple with full OAS pension
                'allowance_threshold': 38736.0,   # Income threshold when spouse receives Allowance
            },
            'july_to_sept': {
                'oas_under_75': 698.60,
                'oas_over_75': 768.46,
                'gis_single_top_up': 161.63,
                'gis_single_max': 1043.45,
                'gis_couple_top_up': 45.79,
                'gis_couple_max': 628.09,
                'allowance_top_up': 45.79,
                'allowance_max': 1326.69,
                'gis_single_threshold': 21168.0,  # Income threshold for single, widowed or divorced
                'gis_couple_threshold': 27984.0,  # Income threshold for couple with full OAS pension
                'allowance_threshold': 39168.0,   # Income threshold when spouse receives Allowance
            },
            'oct_to_dec': {
                # https://www.canada.ca/en/employment-social-development/programs/pensions/pension/statistics/2023-quarterly-october-december.html
                'oas_under_75': 707.68,
                'oas_over_75': 778.45,
                'gis_single_top_up': 163.73,
                'gis_single_max': 1057.01,
                'gis_couple_top_up': 46.39,
                'gis_couple_max': 636.26,
                'allowance_top_up': 46.39,
                'allowance_max': 1343.94,
                'gis_single_threshold': 21456.0,  # Income threshold for single, widowed or divorced
                'gis_couple_threshold': 28320.0,  # Income threshold for couple with full OAS pension
                'allowance_threshold': 39648.0,   # Income threshold when spouse receives Allowance
            },
            'oas_recovery_threshold': 86912.0,  # OAS Recovery Threshold
            'oas_recovery_rate': 0.15,  # OAS Recovery Rate
            'gis_work_deduction': 5000.0,  # GIS Work Deduction
            'gis_partial_work_income_exemption': 5000.0,  # GIS Partial Work Exemption
            'gis_partial_work_income_rate': 0.5,  # GIS Partial Work Deduction
        }
    }

    @property
    def name(self) -> str:
        return "Old Age Security"

    @property
    def supported_years(self) -> List[int]:
        return list(self.PARAMS.keys())

    def calculate(self, family: Family) -> Dict[str, float]:
        self.validate_year(family.tax_year)
        params = self.PARAMS[family.tax_year]

        def get_quarterly_rates(params, family_income):
            """Get average rates for the year accounting for quarterly changes"""
            quarters = ['jan_to_march', 'april_to_june', 'july_to_sept', 'oct_to_dec']
            avg_rates = {}
            for key in ['oas_under_75', 'oas_over_75', 'gis_single_max', 'gis_couple_max']:
                avg_rates[key] = sum(params[q][key] for q in quarters) / len(quarters)
            return avg_rates

        rates = get_quarterly_rates(params, family.adult1.income)

        # Initialize benefits
        oas1 = oas2 = gis = allowance = 0.0

        # Calculate OAS for primary adult if eligible
        if family.adult1.age >= 65:
            base_oas = rates['oas_over_75'] if family.adult1.age >= 75 else rates['oas_under_75']
            # Apply OAS recovery tax if income exceeds threshold
            if family.adult1.income > params['oas_recovery_threshold']:
                recovery = (family.adult1.income - params['oas_recovery_threshold']) * params['oas_recovery_rate']
                oas1 = max(0, base_oas * 12 - recovery)
            else:
                oas1 = base_oas * 12

        # Calculate OAS for secondary adult if eligible
        if family.adult2 and family.adult2.age >= 65:
            base_oas = rates['oas_over_75'] if family.adult2.age >= 75 else rates['oas_under_75']
            if family.adult2.income > params['oas_recovery_threshold']:
                recovery = (family.adult2.income - params['oas_recovery_threshold']) * params['oas_recovery_rate']
                oas2 = max(0, base_oas * 12 - recovery)
            else:
                oas2 = base_oas * 12

        # Calculate GIS
        family_income = family.adult1.income + (family.adult2.income if family.adult2 else 0)

        # Apply work income exemption for GIS
        work_income = family.adult1.gross_work_income + (family.adult2.gross_work_income if family.adult2 else 0)
        work_exemption = min(work_income, params['gis_work_income_deduction'])
        if work_income > params['gis_work_income_deduction']:
            additional_exemption = min(
                work_income - params['gis_work_income_deduction'],
                params['gis_partial_work_income_exemption']
            ) * params['gis_partial_work_income_rate']
            work_exemption += additional_exemption

        family_income_for_gis = max(0, family_income - work_exemption)

        if family.adult1.age >= 65:
            if not family.adult2:  # Single
                if family_income_for_gis <= params['oct_to_dec']['gis_single_threshold']:
                    gis = rates['gis_single_max'] * 12
            elif family.adult2.age >= 65:  # Couple, both over 65
                if family_income_for_gis <= params['oct_to_dec']['gis_couple_threshold']:
                    gis = rates['gis_couple_max'] * 12
            elif family.adult2.age >= 60:  # Spouse's allowance case
                if family_income_for_gis <= params['oct_to_dec']['allowance_threshold']:
                    allowance = rates['allowance_max'] * 12

        # Calculate benefit totals
        benefit1 = oas1 + (gis if not family.adult2 else gis/2)
        benefit2 = oas2 + (gis/2 if family.adult2 and family.adult2.age >= 65 else 0) + allowance
        
        return {
            'program': self.name,
            'tax_year': family.tax_year,
            'adult1': benefit1,
            'adult2': benefit1,
            'total': benefit1 + benefit2,
            'details': {
                'oas1': oas1,
                'oas2': oas2,
                'gis': gis,
                'allowance': allowance
            }
        }


