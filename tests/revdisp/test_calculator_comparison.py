class TaxCalculatorComparison:
    """Compare results between JavaScript and Python implementations"""
    
    def __init__(self, js_calculator: JSTaxCalculator, 
                 python_calculator: PythonTaxCalculator):
        self.js_calc = js_calculator
        self.py_calc = python_calculator
    
    def compare_results(self, test_cases: list) -> Dict[str, list]:
        """
        Compare results between implementations for multiple test cases
        
        Args:
            test_cases: List of test case dictionaries
        
        Returns:
            Dictionary containing lists of differences for each metric
        """
        differences = {
            'RD_new': [],
            'QC_total_new': [],
            'CA_total_new': [],
            'Cotisation_new': []
        }
        
        for case in test_cases:
            js_results = self.js_calc.calculate_disposable_income(case)
            py_results = self.py_calc.calculate_disposable_income(case)
            
            for metric in differences.keys():
                diff = float(js_results[metric]) - float(py_results[metric])
                differences[metric].append(diff)
        
        return differences