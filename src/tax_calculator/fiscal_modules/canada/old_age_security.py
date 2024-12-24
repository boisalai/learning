"""
Old Age Security (OAS)

Notes
    - Les paramètres sont révisés trimestriellement en fonction de l'indice des prix à la consommation.

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
            'period1': {
                'oas_under_75': 713.34,  # Old Age Security Pension (age 65 to 74)
                'oas_over_75': 784.67,  # Old Age Security Pension (age 75 and over)
                'gis_single_top_up': 165.04,  # Guaranteed Income Supplement, Single, Top-Up Amount
                'gis_single_max': 1065.47,  # Guaranteed Income Supplement, Single, Maximum Amount
                'gis_couple_top_up': 46.76,  # Guaranteed Income Supplement, Couple, Top-Up Amount
                'gis_couple_max': 641.35,  # Guaranteed Income Supplement, Couple, Maximum Amount
                'allowance_top_up': 46.76,  # Allowance, Married, Top-Up Amount
                'allowance_max': 1354.69,  # Allowance, Married, Maximum Amount
            },
            'period2': {
                'oas_under_75': 713.34,
                'oas_over_75': 784.67,
                'gis_single_top_up': 165.04,
                'gis_single_max': 1065.47,
                'gis_couple_top_up': 46.76,
                'gis_couple_max': 641.35,
                'allowance_top_up': 46.76,
                'allowance_max': 1354.69,
            },
            'period3': {
                'oas_under_75': 718.33,
                'oas_over_75': 790.16,
                'gis_single_top_up': 166.20,
                'gis_single_max': 1072.93,
                'gis_couple_top_up': 47.09,
                'gis_couple_max': 645.84,
                'allowance_top_up': 47.09,
                'allowance_max': 1364.17,
            },
            'period4': {
                'oas_under_75': 727.67,
                'oas_over_75': 800.44,
                'gis_single_top_up': 168.36,
                'gis_single_max': 1086.88,
                'gis_couple_top_up': 47.70,
                'gis_couple_max': 654.23,
                'allowance_top_up': 47.70,
                'allowance_max': 1381.90,
                # https://www.canada.ca/fr/emploi-developpement-social/programmes/pensions/pension/statistiques/rapport-trimestriel/2024-trimestriel-octobre-decembre.html
            },
            'oas_recovery_threshold': 90997.0,  # OAS Recovery Threshold
            'oas_recovery_rate': 0.15,  # OAS Recovery Rate
            'gis_work_income_deduction': 5000.0,  # GIS Work Deduction
            'gis_partial_work_income_exemption': 5000.0,  # GIS Partial Work Exemption
            'gis_partial_work_income_rate': 0.5,  # GIS Partial Work Deduction
            'gis_single_threshold': 22056.0,  # GIS Single Threshold  Ce montant change d'un trimestre à l'autre
            'gis_couple_threshold': 29136.0,  # GIS Single Threshold
            'allowance_threshold': 40800.0,  # Allowance Threshold
            # See https://www.taxtips.ca/seniors/guaranteed-income-supplement.htm
        },
        2023: {
            'period1': {
                'oas_under_75': 687.56,
                'oas_over_75': 756.32,
                'gis_single_top_up': 159.07,
                'gis_single_max': 1026.96,
                'gis_couple_top_up': 45.06,
                'gis_couple_max': 618.15,
                'allowance_top_up': 45.06,
                'allowance_max': 1556.51,
            },
            'period2': {
                'oas_under_75': 691.00,
                'oas_over_75': 760.10,
                'gis_single_top_up': 159.87,
                'gis_single_max': 1032.10,
                'gis_couple_top_up': 45.29,
                'gis_couple_max': 621.25,
                'allowance_top_up': 45.29,
                'allowance_max': 1312.25,
            },
            'period3': {
                'oas_under_75': 698.60,
                'oas_over_75': 768.46,
                'gis_single_top_up': 161.63,
                'gis_single_max': 1043.45,
                'gis_couple_top_up': 45.79,
                'gis_couple_max': 628.09,
                'allowance_top_up': 45.79,
                'allowance_max': 1326.69,
            },
            'period4': {
                'oas_under_75': 707.68,
                'oas_over_75': 778.45,
                'gis_single_top_up': 163.73,
                'gis_single_max': 1057.01,
                'gis_couple_top_up': 46.39,
                'gis_couple_max': 636.26,
                'allowance_top_up': 46.39,
                'allowance_max': 1343.94,
            },
            'oas_recovery_threshold': 86912.0,  # OAS Recovery Threshold
            'oas_recovery_rate': 0.15,  # OAS Recovery Rate
            'gis_work_deduction': 5000.0,  # GIS Work Deduction
            'gis_partial_work_income_exemption': 5000.0,  # GIS Partial Work Exemption
            'gis_partial_work_income_rate': 0.5,  # GIS Partial Work Deduction
            'gis_single_threshold': ???.0,  # GIS Single Threshold
            'gis_couple_threshold': 28512.0,  # GIS Single Threshold
            'allowance_threshold': 39168.0,  # Allowance Threshold

            
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

        var oas1 = 0;
        var oas2 = 0;

        if (type.age1 >= 65 || type.age2 >= 65) {
            var p = param[year];

            // Prestation annuelle maximale.
            var ipc = Math.pow(1.02, 1 / 4);
            if (p.max2 == 0) p.max2 = p.max1 * ipc;
            if (p.max3 == 0) p.max3 = p.max2 * ipc;
            if (p.max4 == 0) p.max4 = p.max3 * ipc;
            var max = (p.max1 + p.max2 + p.max3 + p.max4) * 3;

            # Qu'entend-on par revenu net de toutes provenances?
            # Éventuellement, faudrait ajouter dividendes, emplois, etc...
            # https://www.canada.ca/fr/agence-revenu/services/formulaires-publications/publications/t4155/t4155-declaration-revenus-securite-vieillesse-non-residents.html#Rvnu_d_tts_prvnncs
            # https://www.canada.ca/fr/agence-revenu/services/formulaires-publications/formulaires/t1136.html */

            if (type.age1 >= 65) {
                /* Le remboursement est égal à 15 % de la partie de votre revenu net (incluant les prestations de la SV ) 
                qui dépasse 79 845 $ en 2021. */
                var netIncome1 = type.revenuTotal1;
                var reduction = Math.max(0, (netIncome1 + max - p.threshold) * p.rate);
                oas1 = Math.max(0, max - reduction);
            }

            if (type.nbAdultes == 2 && type.age1 >= 65) {
                var netIncome2 = type.revenuTotal2;
                var reduction = Math.max(0, (netIncome2 + max - p.threshold) * p.rate);
                oas2 = Math.max(0, max - reduction);
            }

            oas1 = round(oas1, 2);
            oas2 = round(oas2, 2);
        
        return {
            'program': self.name,
            'tax_year': family.tax_year,
            'adult1': oas1,
            'adult2': oas1,
            'total': oas1 + oas2,
        }


