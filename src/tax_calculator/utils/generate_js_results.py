import json
from tqdm import tqdm
from tax_calculator.calculators.js_calculator import JSTaxCalculator
from tax_calculator.core import FamilyStatus, AdultInfo, ChildInfo, DaycareType, Family, generate_random_test_cases

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (FamilyStatus, DaycareType)):  # Gère les enums
            return obj.name
        if hasattr(obj, '__dict__'):  # Gère les dataclasses et autres objets
            return obj.__dict__
        return super().default(obj)

def generate_js_results(num_cases: int, output_file: str):
    js_calculator = JSTaxCalculator()
    test_cases = generate_random_test_cases(num_cases)
    results = []

    for family in tqdm(test_cases, desc="Generating test cases"):
        js_result = js_calculator.calculate(family)
        results.append({
            'family': family.__dict__,
            'result': js_result
        })

    with open(output_file, 'w') as f:
        json.dump(results, f, indent=4, cls=CustomJSONEncoder)

if __name__ == "__main__":
    output_file = "/Users/alain/Workspace/GitHub/Learning/src/tax_calculator/tests/js_results.json"
    generate_js_results(100, output_file)