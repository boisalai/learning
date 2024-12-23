import json
from tax_calculator.calculators.python_calculator import PythonTaxCalculator
from tax_calculator.core import (
    Family,
    FamilyStatus,
    AdultInfo,
    ChildInfo,
    DaycareType,
    generate_standard_test_cases,
    generate_random_test_cases,
)


class CalculatorComparison:
    def __init__(self):
        """Initialize calculators"""
        self.py_calculator = PythonTaxCalculator()
        self.js_results = self.load_js_results("/Users/alain/Workspace/GitHub/Learning/src/tax_calculator/tests/js_results.json")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def load_js_results(self, file_path: str):
        """Load precomputed JavaScript results from a file"""
        with open(file_path, 'r') as f:
            return json.load(f)

    def normalize_results(self, results: dict) -> dict:
        def round_js_style(number):
            """
            Arrondit un nombre à la manière de JavaScript, en appliquant une symétrie pour les nombres négatifs.
            """
            if number >= 0:
                # Pour les nombres positifs, on applique la logique initiale
                return (
                    int(number + 0.5)
                    if abs(number - int(number)) == 0.5
                    else round(number)
                )
            else:
                # Pour les nombres négatifs, on inverse le signe avant d'arrondir et on le réapplique
                return (
                    -int(-number + 0.5)
                    if abs(number - int(number)) == 0.5
                    else round(number)
                )

        """Normalize the results to a comparable format"""
        normalized_results = {
            #'RD_new': results.get('disposable_income', 0),
            #'QC_total_new': results.get('disposable_income', 0),
            #'QC_impot_st_new': results.get('disposable_income', 0),
            #'QC_impot_new': results.get('disposable_income', 0),
            #'QC_imppot_bonif_new': results.get('disposable_income', 0),
            #'QC_adr_new': results.get('disposable_income', 0),
            #'QC_sae_new': results.get('disposable_income', 0),
            #'SFS_new': results.get('disposable_income', 0),
            #'QC_pt_new': results.get('disposable_income', 0),
            #'QC_sol_new': results.get('disposable_income', 0),
            #'QC_garde_new': results.get('disposable_income', 0),
            #'QC_al_new': results.get('disposable_income', 0),
            #'QC_medic_new': results.get('disposable_income', 0),
            #'QC_aines_new': results.get('disposable_income', 0),
            #'CA_total_new': results.get('disposable_income', 0),
            #'CA_impot_new': results.get('disposable_income', 0),
            #'CA_ace_new': results.get('disposable_income', 0),
            #'CA_tps_new': results.get('disposable_income', 0),
            #'CA_pfrt_new': results.get('disposable_income', 0),
            #'CA_psv_new': results.get('disposable_income', 0),
            #'CA_medic_new': results.get('disposable_income', 0),
            'Cotisation_new': round_js_style(
                results.get('contributions', {}).get('total', 0)
            ),
            'CA_ae_new': round_js_style(
                results.get('employment_insurance', {}).get('total', 0)
            ),
            'QC_rqap_new': round_js_style(
                results.get('parental_insurance', {}).get('total', 0)
            ),
            'CA_rrq_new': round_js_style(
                results.get('quebec_pension_plan', {}).get('total', 0)
            ),
            'QC_fss_new': round_js_style(
                results.get('health_services_fund', {}).get('total', 0)
            ),
            'QC_ramq_new': round_js_style(
                results.get('quebec_prescription_drug_insurance', {}).get('total', 0)
            ),
            #'Frais_garde_new': results.get('disposable_income', 0)
        }
        return normalized_results

    def compare_results(self, py_result, js_result, tolerance=0.01):
        """
        Compare results between Python and JavaScript calculators

        Args:
            py_result: Results from Python calculator
            js_result: Results from JavaScript calculator
            tolerance: Maximum acceptable difference (default: 0.01$)
        """
        differences = []
        common_keys = set(py_result.keys()).intersection(js_result.keys())

        for key in common_keys:
            py_val = py_result[key]
            js_val = js_result[key]

            if isinstance(py_val, (int, float)) and isinstance(js_val, (int, float)):
                diff = abs(py_val - js_val)
                if diff > tolerance:
                    differences.append(
                        f"\n{key}:\n  Python:     {py_val:>10}\n  JavaScript: {js_val:>10}\n  Difference: {diff:>10}"
                    )
            elif py_val != js_val:
                differences.append(
                    f"\n{key}:\n  Python:     {py_val}\n  JavaScript: {js_val}"
                )

        return "".join(differences)

    def reconstruct_family(self, family_dict):
        """Reconstruit un objet Family à partir du dictionnaire stocké dans le JSON"""
        # Convertir le family_status de string à enum
        family_dict['family_status'] = FamilyStatus[family_dict['family_status']]
        
        # Reconstruire adult1
        if 'adult1' in family_dict:
            adult1_dict = family_dict['adult1']
            # Retire les underscores des noms de propriétés
            cleaned_adult1_dict = {
                'age': adult1_dict['age'],
                'gross_work_income': adult1_dict.get('_gross_work_income', 0.0),
                'self_employed_income': adult1_dict.get('_self_employed_income', 0.0),
                'gross_retirement_income': adult1_dict.get('_gross_retirement_income', 0.0),
                'is_retired': adult1_dict.get('is_retired', False)
            }
            family_dict['adult1'] = AdultInfo(**cleaned_adult1_dict)
        
        # Reconstruire adult2 s'il existe
        if 'adult2' in family_dict and family_dict['adult2'] is not None:
            adult2_dict = family_dict['adult2']
            # Retire les underscores des noms de propriétés
            cleaned_adult2_dict = {
                'age': adult2_dict['age'],
                'gross_work_income': adult2_dict.get('_gross_work_income', 0.0),
                'self_employed_income': adult2_dict.get('_self_employed_income', 0.0),
                'gross_retirement_income': adult2_dict.get('_gross_retirement_income', 0.0),
                'is_retired': adult2_dict.get('is_retired', False)
            }
            family_dict['adult2'] = AdultInfo(**cleaned_adult2_dict)
        
        # Reconstruire les enfants s'ils existent
        if 'children' in family_dict and family_dict['children'] is not None:
            children = []
            for child_dict in family_dict['children']:
                # Convertir le daycare_type de string à enum s'il existe
                if 'daycare_type' in child_dict and child_dict['daycare_type'] is not None:
                    child_dict['daycare_type'] = DaycareType[child_dict['daycare_type']]
                children.append(ChildInfo(**child_dict))
            family_dict['children'] = children
        
        return Family(**family_dict)

    def run_comparisons(self, num_cases=5):
        """Compare calculations for multiple random test cases"""
        cases_with_diff = 0
        num_cases = len(self.js_results)

        print(f"\nComparaison de {num_cases} cas aléatoires...\n")
        print("-" * 80)

        for i, js_case in enumerate(self.js_results, 1):
            # Reconstruire l'objet Family à partir des données JSON
            family = self.reconstruct_family(js_case['family'])
            
            # Calculer avec Python
            py_result = self.py_calculator.calculate(family)
            
            # Normaliser les deux résultats
            py_normalized = self.normalize_results(py_result)
            js_normalized = js_case['result']

            differences = self.compare_results(py_normalized, js_normalized)
            if differences:
                cases_with_diff += 1
                if cases_with_diff <= 10:
                    print(f"\nCas #{i} avec différences:")
                    print(f"{family.describe()}")
                    print(f"Différences trouvées:{differences}")
                    print("-" * 80)

        print(f"\nRésumé:")
        print(f"  Cas testés: {num_cases}")
        print(f"  Cas avec différences: {cases_with_diff}")
        print(f"  Cas identiques: {num_cases - cases_with_diff}")
        if cases_with_diff == 0:
            print("\nTous les cas sont identiques entre Python et JavaScript!")


if __name__ == "__main__":
    with CalculatorComparison() as comparison:
        comparison.run_comparisons(5)
