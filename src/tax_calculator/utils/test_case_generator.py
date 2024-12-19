import random
from typing import List, Dict, Any

def generate_test_cases(num_cases: int = 10) -> List[Dict[str, Any]]:
    """
    Generates test cases for the tax calculator
    
    Args:
        num_cases: Number of test cases to generate
        
    Returns:
        List of dictionaries containing test case parameters
    """
    
    family_situations = [
        'Personne vivant seule',      # Single person
        'Famille monoparentale',      # Single parent
        'Couple',                     # Couple
        'Retraité vivant seul',       # Single retired
        'Couple de retraités'         # Retired couple
    ]
    
    incomes = [0, 15000, 30000, 45000, 60000, 75000, 90000]
    worker_ages = [25, 35, 45, 55]
    retirement_ages = [65, 75, 85]
    child_ages = [2, 5, 10, 15]
    num_children = range(6)  # 0 to 5 children
    daycare_fees = [0, 8000, 15000]
    daycare_types = ['Subventionnée', 'Non subventionnée']  # Subsidized, Non-subsidized

    test_cases = []
    
    for _ in range(num_cases):
        situation = random.choice(family_situations)
        is_retired = 'retraité' in situation.lower()
        is_couple = 'Couple' in situation
        can_have_children = not is_retired and situation != 'Personne vivant seule'

        case = {
            'situation': situation,
            'income1': random.choice(incomes),
            'age1': random.choice(retirement_ages if is_retired else worker_ages),
            'income2': random.choice(incomes) if is_couple else 0,
            'age2': random.choice(retirement_ages if is_retired else worker_ages) if is_couple else 0,
            'num_children': 0
        }

        if can_have_children:
            case['num_children'] = random.choice(num_children)
            for i in range(1, case['num_children'] + 1):
                child_age = random.choice(child_ages)
                case[f'child_age{i}'] = child_age
                if child_age <= 5:
                    case[f'daycare_fee{i}'] = random.choice(daycare_fees)
                    case[f'daycare_type{i}'] = random.choice(daycare_types)
                else:
                    case[f'daycare_fee{i}'] = 0
                    case[f'daycare_type{i}'] = 'Subventionnée'
            
        test_cases.append(case)
    
    return test_cases

if __name__ == "__main__":
    # Test the generator
    cases = generate_test_cases(3)
    for i, case in enumerate(cases, 1):
        print(f"\nTest Case {i}:")
        for key, value in case.items():
            print(f"{key}: {value}")