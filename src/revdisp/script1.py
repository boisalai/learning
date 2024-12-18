import os
import time
import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
import pandas as pd
from pathlib import Path
import json
from tqdm import tqdm
import numpy as np


class CalculateurFiscal:
    def __init__(self, html_path):
        self.html_path = html_path
        
        print("Configuration de Firefox...")
        options = Options()
        options.add_argument('--headless')
        
        # Optimisations Firefox
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-logging')
        options.set_preference('javascript.enabled', True)
        options.set_preference('dom.max_script_run_time', 20)
        options.set_preference('browser.cache.disk.enable', False)
        options.set_preference('browser.cache.memory.enable', False)
        options.set_preference('browser.cache.offline.enable', False)
        options.set_preference('network.http.use-cache', False)

        # Spécifier le chemin vers Firefox sur macOS
        firefox_paths = [
            '/Applications/Firefox.app/Contents/MacOS/firefox',
            '/Applications/Firefox.app/Contents/MacOS/firefox-bin'
        ]
        
        firefox_binary = next((path for path in firefox_paths if os.path.exists(path)), None)
        if not firefox_binary:
            raise Exception("Firefox n'a pas été trouvé.")
                
        options.binary_location = firefox_binary
        service = Service('/opt/homebrew/bin/geckodriver')
        
        print("Initialisation du navigateur Firefox...")
        try:
            self.driver = webdriver.Firefox(
                options=options,
                service=service
            )
            # Réduire les temps d'attente implicites
            self.driver.implicitly_wait(0.5)
            self.driver.set_script_timeout(20)
            print("Firefox initialisé avec succès!")
        except Exception as e:
            print(f"Erreur lors de l'initialisation de Firefox: {str(e)}")
            raise Exception("Erreur d'initialisation. Assurez-vous que Firefox est installé et à jour.")
        
    def start(self):
        print(f"Chargement de la page: {self.html_path}")
        file_path = f"file:///{Path(self.html_path).absolute()}"
        self.driver.get(file_path)
        
        # Attendre que les éléments clés soient chargés
        try:
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.ID, "Situation"))
            )
            print("Page chargée avec succès!")
        except Exception as e:
            print("Erreur lors du chargement de la page:")
            print(e)
            self.close()
            raise
        
    def set_value(self, element_id, value):
        """Définit une valeur dans un champ et attend la mise à jour"""
        try:
            element = self.driver.find_element(By.ID, element_id)
            if element.tag_name == 'select':
                self.driver.execute_script(
                    f"arguments[0].value = '{value}'; "
                    f"arguments[0].dispatchEvent(new Event('change'));", 
                    element
                )
            else:
                self.driver.execute_script(
                    f"arguments[0].value = '{value}'; "
                    f"recalc_onclick('{element_id}');", 
                    element
                )
            time.sleep(0.01)  # Court délai pour laisser le temps aux calculs
        except Exception as e:
            print(f"Erreur lors de la définition de la valeur pour {element_id}:")
            print(e)
            raise

    def _clean_numeric_value(self, value):
        """Nettoie et convertit une valeur en nombre"""
        if not value or value == "―" or value == "−":
            return 0
        
        # Supprimer les espaces et remplacer les symboles négatifs Unicode
        if isinstance(value, str):
            value = value.replace(" ", "").replace("−", "-")
        
        try:
            return float(value or 0)
        except (ValueError, TypeError):
            return 0

    def _process_section(self, section_dict):
        """Traite récursivement un dictionnaire pour nettoyer les valeurs numériques"""
        processed = {}
        for key, value in section_dict.items():
            if isinstance(value, dict):
                processed[key] = self._process_section(value)
            elif isinstance(value, list):
                if key in ['type_garde']:  # Liste de chaînes à préserver
                    processed[key] = value
                else:  # Liste de valeurs numériques à nettoyer
                    processed[key] = [self._clean_numeric_value(v) for v in value]
            else:
                if key in ['situation', 'nb_enfants']:  # Préserver les chaînes
                    processed[key] = value
                else:  # Nettoyer les valeurs numériques
                    processed[key] = self._clean_numeric_value(value)
        return processed
    
    def get_results(self):
        """Récupère tous les résultats calculés"""
        try:
            # Helper function to convert old/new to years
            def convert_to_years(section):
                return {
                    'ecart': self._clean_numeric_value(section['ecart']),
                    '2023': self._clean_numeric_value(section['old']),
                    '2024': self._clean_numeric_value(section['new'])
                }

            raw_results = {
                'parametres': {
                    'situation': self.driver.find_element(By.ID, 'Situation').get_attribute('value'),
                    'age_adulte1': self.driver.find_element(By.ID, 'AgeAdulte1').get_attribute('value'),
                    'age_adulte2': self.driver.find_element(By.ID, 'AgeAdulte2').get_attribute('value'),
                    'revenu1': self.driver.find_element(By.ID, 'Revenu1').get_attribute('value'),
                    'revenu2': self.driver.find_element(By.ID, 'Revenu2').get_attribute('value'),
                    'nb_enfants': self.driver.find_element(By.ID, 'NbEnfants').get_attribute('value'),
                    'ages_enfants': [
                        self.driver.find_element(By.ID, f'AgeEnfant{i}').get_attribute('value')
                        for i in range(1, 6)
                    ],
                    'frais_garde': [
                        self.driver.find_element(By.ID, f'Frais{i}').get_attribute('value')
                        for i in range(1, 6)
                    ],
                    'type_garde': [
                        self.driver.find_element(By.ID, f'type_garde{i}').get_attribute('value')
                        for i in range(1, 6)
                    ]
                },
                'resultats': {
                    'revenu_brut': convert_to_years({
                        'ecart': self.driver.find_element(By.ID, 'RB_ecart').get_attribute('value'),
                        'old': self.driver.find_element(By.ID, 'RB_old').get_attribute('value'),
                        'new': self.driver.find_element(By.ID, 'RB_new').get_attribute('value')
                    }),
                    'revenu_disponible': convert_to_years({
                        'ecart': self.driver.find_element(By.ID, 'RD_ecart').get_attribute('value'),
                        'old': self.driver.find_element(By.ID, 'RD_old').get_attribute('value'),
                        'new': self.driver.find_element(By.ID, 'RD_new').get_attribute('value')
                    }),
                    'quebec': {
                        'impot_standard': convert_to_years({
                            'ecart': self.driver.find_element(By.ID, 'QC_impot_st_ecart').get_attribute('value'),
                            'old': self.driver.find_element(By.ID, 'QC_impot_st_old').get_attribute('value'),
                            'new': self.driver.find_element(By.ID, 'QC_impot_st_new').get_attribute('value')
                        }),
                        'impot': convert_to_years({
                            'ecart': self.driver.find_element(By.ID, 'QC_impot_ecart').get_attribute('value'),
                            'old': self.driver.find_element(By.ID, 'QC_impot_old').get_attribute('value'),
                            'new': self.driver.find_element(By.ID, 'QC_impot_new').get_attribute('value')
                        }),
                        'impot_bonif': convert_to_years({
                            'ecart': self.driver.find_element(By.ID, 'QC_impot_bonif_ecart').get_attribute('value'),
                            'old': self.driver.find_element(By.ID, 'QC_impot_bonif_old').get_attribute('value'),
                            'new': self.driver.find_element(By.ID, 'QC_imppot_bonif_new').get_attribute('value')
                        }),
                        'aide_sociale': convert_to_years({
                            'ecart': self.driver.find_element(By.ID, 'QC_adr_ecart').get_attribute('value'),
                            'old': self.driver.find_element(By.ID, 'QC_adr_old').get_attribute('value'),
                            'new': self.driver.find_element(By.ID, 'QC_adr_new').get_attribute('value')
                        }),
                        'allocation_familiale': convert_to_years({
                            'ecart': self.driver.find_element(By.ID, 'QC_sae_ecart').get_attribute('value'),
                            'old': self.driver.find_element(By.ID, 'QC_sae_old').get_attribute('value'),
                            'new': self.driver.find_element(By.ID, 'QC_sae_new').get_attribute('value')
                        }),
                        'fournitures_scolaires': convert_to_years({
                            'ecart': self.driver.find_element(By.ID, 'SFS_ecart').get_attribute('value'),
                            'old': self.driver.find_element(By.ID, 'SFS_old').get_attribute('value'),
                            'new': self.driver.find_element(By.ID, 'SFS_new').get_attribute('value')
                        }),
                        'prime_travail': convert_to_years({
                            'ecart': self.driver.find_element(By.ID, 'QC_pt_ecart').get_attribute('value'),
                            'old': self.driver.find_element(By.ID, 'QC_pt_old').get_attribute('value'),
                            'new': self.driver.find_element(By.ID, 'QC_pt_new').get_attribute('value')
                        }),
                        'credit_solidarite': convert_to_years({
                            'ecart': self.driver.find_element(By.ID, 'QC_sol_ecart').get_attribute('value'),
                            'old': self.driver.find_element(By.ID, 'QC_sol_old').get_attribute('value'),
                            'new': self.driver.find_element(By.ID, 'QC_sol_new').get_attribute('value')
                        }),
                        'credit_garde': convert_to_years({
                            'ecart': self.driver.find_element(By.ID, 'QC_garde_ecart').get_attribute('value'),
                            'old': self.driver.find_element(By.ID, 'QC_garde_old').get_attribute('value'),
                            'new': self.driver.find_element(By.ID, 'QC_garde_new').get_attribute('value')
                        }),
                        'allocation_logement': convert_to_years({
                            'ecart': self.driver.find_element(By.ID, 'QC_al_ecart').get_attribute('value'),
                            'old': self.driver.find_element(By.ID, 'QC_al_old').get_attribute('value'),
                            'new': self.driver.find_element(By.ID, 'QC_al_new').get_attribute('value')
                        }),
                        'credit_medical': convert_to_years({
                            'ecart': self.driver.find_element(By.ID, 'QC_medic_ecart').get_attribute('value'),
                            'old': self.driver.find_element(By.ID, 'QC_medic_old').get_attribute('value'),
                            'new': self.driver.find_element(By.ID, 'QC_medic_new').get_attribute('value')
                        }),
                        'soutien_aines': convert_to_years({
                            'ecart': self.driver.find_element(By.ID, 'QC_aines_ecart').get_attribute('value'),
                            'old': self.driver.find_element(By.ID, 'QC_aines_old').get_attribute('value'),
                            'new': self.driver.find_element(By.ID, 'QC_aines_new').get_attribute('value')
                        }),
                        'total': convert_to_years({
                            'ecart': self.driver.find_element(By.ID, 'QC_total_ecart').get_attribute('value'),
                            'old': self.driver.find_element(By.ID, 'QC_total_old').get_attribute('value'),
                            'new': self.driver.find_element(By.ID, 'QC_total_new').get_attribute('value')
                        })
                    },
                    'canada': {
                        'impot': convert_to_years({
                            'ecart': self.driver.find_element(By.ID, 'CA_impot_ecart').get_attribute('value'),
                            'old': self.driver.find_element(By.ID, 'CA_impot_old').get_attribute('value'),
                            'new': self.driver.find_element(By.ID, 'CA_impot_new').get_attribute('value')
                        }),
                        'allocation_enfants': convert_to_years({
                            'ecart': self.driver.find_element(By.ID, 'CA_ace_ecart').get_attribute('value'),
                            'old': self.driver.find_element(By.ID, 'CA_ace_old').get_attribute('value'),
                            'new': self.driver.find_element(By.ID, 'CA_ace_new').get_attribute('value')
                        }),
                        'credit_tps': convert_to_years({
                            'ecart': self.driver.find_element(By.ID, 'CA_tps_ecart').get_attribute('value'),
                            'old': self.driver.find_element(By.ID, 'CA_tps_old').get_attribute('value'),
                            'new': self.driver.find_element(By.ID, 'CA_tps_new').get_attribute('value')
                        }),
                        'allocation_travailleurs': convert_to_years({
                            'ecart': self.driver.find_element(By.ID, 'CA_pfrt_ecart').get_attribute('value'),
                            'old': self.driver.find_element(By.ID, 'CA_pfrt_old').get_attribute('value'),
                            'new': self.driver.find_element(By.ID, 'CA_pfrt_new').get_attribute('value')
                        }),
                        'securite_vieillesse': convert_to_years({
                            'ecart': self.driver.find_element(By.ID, 'CA_psv_ecart').get_attribute('value'),
                            'old': self.driver.find_element(By.ID, 'CA_psv_old').get_attribute('value'),
                            'new': self.driver.find_element(By.ID, 'CA_psv_new').get_attribute('value')
                        }),
                        'credit_medical': convert_to_years({
                            'ecart': self.driver.find_element(By.ID, 'CA_medic_ecart').get_attribute('value'),
                            'old': self.driver.find_element(By.ID, 'CA_medic_old').get_attribute('value'),
                            'new': self.driver.find_element(By.ID, 'CA_medic_new').get_attribute('value')
                        }),
                        'total': convert_to_years({
                            'ecart': self.driver.find_element(By.ID, 'CA_total_ecart').get_attribute('value'),
                            'old': self.driver.find_element(By.ID, 'CA_total_old').get_attribute('value'),
                            'new': self.driver.find_element(By.ID, 'CA_total_new').get_attribute('value')
                        })
                    },
                    'cotisations': {
                        'assurance_emploi': convert_to_years({
                            'ecart': self.driver.find_element(By.ID, 'CA_ae_ecart').get_attribute('value'),
                            'old': self.driver.find_element(By.ID, 'CA_ae_old').get_attribute('value'),
                            'new': self.driver.find_element(By.ID, 'CA_ae_new').get_attribute('value')
                        }),
                        'rqap': convert_to_years({
                            'ecart': self.driver.find_element(By.ID, 'QC_rqap_ecart').get_attribute('value'),
                            'old': self.driver.find_element(By.ID, 'QC_rqap_old').get_attribute('value'),
                            'new': self.driver.find_element(By.ID, 'QC_rqap_new').get_attribute('value')
                        }),
                        'rrq': convert_to_years({
                            'ecart': self.driver.find_element(By.ID, 'CA_rrq_ecart').get_attribute('value'),
                            'old': self.driver.find_element(By.ID, 'CA_rrq_old').get_attribute('value'),
                            'new': self.driver.find_element(By.ID, 'CA_rrq_new').get_attribute('value')
                        }),
                        'fss': convert_to_years({
                            'ecart': self.driver.find_element(By.ID, 'QC_fss_ecart').get_attribute('value'),
                            'old': self.driver.find_element(By.ID, 'QC_fss_old').get_attribute('value'),
                            'new': self.driver.find_element(By.ID, 'QC_fss_new').get_attribute('value')
                        }),
                        'ramq': convert_to_years({
                            'ecart': self.driver.find_element(By.ID, 'QC_ramq_ecart').get_attribute('value'),
                            'old': self.driver.find_element(By.ID, 'QC_ramq_old').get_attribute('value'),
                            'new': self.driver.find_element(By.ID, 'QC_ramq_new').get_attribute('value')
                        }),
                        'total': convert_to_years({
                            'ecart': self.driver.find_element(By.ID, 'Cotisation_ecart').get_attribute('value'),
                            'old': self.driver.find_element(By.ID, 'Cotisation_old').get_attribute('value'),
                            'new': self.driver.find_element(By.ID, 'Cotisation_new').get_attribute('value')
                        })
                    },
                    'frais_garde': convert_to_years({
                        'ecart': self.driver.find_element(By.ID, 'Frais_garde_ecart').get_attribute('value'),
                        'old': self.driver.find_element(By.ID, 'Frais_garde_old').get_attribute('value'),
                        'new': self.driver.find_element(By.ID, 'Frais_garde_new').get_attribute('value')
                    })
                }
            }
            # Nettoyer toutes les valeurs numériques
            return self._process_section(raw_results)
        
        except Exception as e:
            print("Erreur lors de la récupération des résultats:")
            print(e)
            raise
    
    def close(self):
        """Ferme proprement le navigateur"""
        try:
            self.driver.quit()
            print("Navigateur fermé avec succès!")
        except Exception as e:
            print("Erreur lors de la fermeture du navigateur:")
            print(e)

def generate_test_cases(nobs):
    """Génère des cas de test de manière stratégique avec la distinction des revenus de travail et de retraite"""
    
    # Configuration des paramètres de base
    situations = [
        'Personne vivant seule', 
        'Famille monoparentale', 
        'Couple',
        'Retraité vivant seul',
        'Couple de retraités'
    ]
    
    # Labels pour le nombre d'enfants
    enfants = [
        'Aucun enfant',
        'Un enfant',
        'Deux enfants',
        'Trois enfants',
        'Quatre enfants',
        'Cinq enfants'
    ]
    
    # Générer des points d'échantillonnage stratégiques pour les revenus
    revenus = np.concatenate([
        [0],  # Pas de revenu
        np.linspace(1000, 20000, 8),  # Focus sur les bas revenus
        np.linspace(25000, 50000, 6),  # Revenus moyens
        np.linspace(60000, 90000, 4)   # Hauts revenus
    ]).astype(int)
    
    # Points d'échantillonnage pour les âges
    ages_travailleur = [18, 25, 30, 35, 40, 45, 50, 55, 60, 64]
    ages_retraite = [65, 70, 75, 80, 85, 90]
    
    # Points d'échantillonnage pour les âges des enfants
    ages_enfant = [0, 2, 4, 6, 8, 10, 12, 14, 16, 17]
    
    frais_garde = [0, 5000, 10000, 15000]
    types_garde = ['Subventionné', 'Non subventionné']
    
    test_cases = []
    cas_par_situation = max(1, nobs // len(situations))
    
    for situation in situations:
        # Déterminer les caractéristiques de la situation
        est_retraite = 'retraité' in situation.lower()
        est_couple = situation in ['Couple', 'Couple de retraités']
        peut_avoir_enfants = not est_retraite and situation != 'Personne vivant seule'
        
        # Sélectionner la plage d'âges appropriée
        ages = ages_retraite if est_retraite else ages_travailleur
        
        # Définir les options pour le nombre d'enfants selon la situation
        if not peut_avoir_enfants:
            nb_enfants_possibles = [enfants[0]]  # 'Aucun enfant'
        else:
            nb_enfants_possibles = enfants[1:] if situation == 'Famille monoparentale' else enfants
        
        for _ in range(cas_par_situation):
            # Paramètres de base
            age1 = int(np.random.choice(ages))
            revenu = int(np.random.choice(revenus))
            
            # Distribution des revenus selon l'âge
            revenu_brut_travail1 = int(revenu if age1 < 65 else 0)
            revenu_brut_retraite1 = int(revenu if age1 >= 65 else 0)
            
            # Paramètres du conjoint - uniquement pour les couples
            if est_couple:
                if est_retraite:
                    age2 = int(np.random.choice([a for a in ages_retraite]))
                else:
                    age2 = int(np.random.choice([a for a in ages_travailleur]))
                    
                revenu = int(np.random.choice(revenus))
                revenu_brut_travail2 = int(revenu if age2 < 65 else 0)
                revenu_brut_retraite2 = int(revenu if age2 >= 65 else 0)
            else:
                age2 = 0
                revenu_brut_travail2 = 0
                revenu_brut_retraite2 = 0

            # Sélection du nombre d'enfants
            nb_enfant = np.random.choice(nb_enfants_possibles)
            nb_enfant_int = enfants.index(nb_enfant)

            # Création du cas de test avec conversion explicite des types numpy
            case = {
                'Situation': situation,
                'AgeAdulte1': float(age1),  # Conversion en float pour compatibilité
                'revenu_brut_travail1': revenu_brut_travail1,
                'revenu_brut_retraite1': revenu_brut_retraite1,
                'AgeAdulte2': float(age2),  # Conversion en float pour compatibilité
                'revenu_brut_travail2': revenu_brut_travail2,
                'revenu_brut_retraite2': revenu_brut_retraite2,
                'NbEnfants': nb_enfant
            }

            # Ajout des enfants et frais de garde
            for i in range(1, 6):
                if i <= nb_enfant_int and peut_avoir_enfants:
                    age_enfant = int(np.random.choice(ages_enfant))
                    case[f'AgeEnfant{i}'] = float(age_enfant)  # Conversion en float pour compatibilité
                    
                    if age_enfant < 6:
                        case[f'Frais{i}'] = float(np.random.choice(frais_garde))
                        case[f'type_garde{i}'] = np.random.choice(types_garde)
                    else:
                        case[f'Frais{i}'] = 0.0
                        case[f'type_garde{i}'] = types_garde[0]
                else:
                    case[f'AgeEnfant{i}'] = 0.0
                    case[f'Frais{i}'] = 0.0
                    case[f'type_garde{i}'] = types_garde[0]
            
            test_cases.append(case)
    
    return test_cases

def main():
    parser = argparse.ArgumentParser(description='Calculateur fiscal avec nombre de cas configurable')
    parser.add_argument('--nobs', type=int, default=5,
                       help='Nombre de cas à générer (défaut: 5)')
    args = parser.parse_args()
    
    html_path = "index.html"
    nobs = args.nobs
    print(f"Démarrage du calculateur fiscal (maximum {nobs} cas)...")
    
    calc = None
    try:
        calc = CalculateurFiscal(html_path)
        calc.start()
        
        test_cases = generate_test_cases(nobs)
        resultats = []
        
        with tqdm(total=len(test_cases), desc="Progression") as pbar:
            for cas_index, case in enumerate(test_cases, 1): 
                try:
                    # Définir les valeurs une par une
                    calc.set_value('Situation', case['Situation'])
                    calc.set_value('AgeAdulte1', case['AgeAdulte1'])
                    calc.set_value('Revenu1', float(case['revenu_brut_travail1'] + case['revenu_brut_retraite1']))
                    calc.set_value('AgeAdulte2', case['AgeAdulte2'])
                    calc.set_value('Revenu2', float(case['revenu_brut_travail2'] + case['revenu_brut_retraite2']))
                    calc.set_value('NbEnfants', case['NbEnfants'])
                    
                    # Définir les valeurs pour chaque enfant
                    for i in range(1, 6):
                        if f'AgeEnfant{i}' in case:
                            calc.set_value(f'AgeEnfant{i}', case[f'AgeEnfant{i}'])
                            calc.set_value(f'Frais{i}', case[f'Frais{i}'])
                            calc.set_value(f'type_garde{i}', case[f'type_garde{i}'])
                    
                    # Récupérer les résultats et ajouter les nouveaux champs de revenus
                    res = calc.get_results()
                    cas_complet = {
                        'id': cas_index,  # Ajouter l'id en premier
                        'parametres': {
                            'revenu_brut_travail1': float(case['revenu_brut_travail1']),
                            'revenu_brut_retraite1': float(case['revenu_brut_retraite1']),
                            'revenu_brut_travail2': float(case['revenu_brut_travail2']),
                            'revenu_brut_retraite2': float(case['revenu_brut_retraite2']),
                            **{k: v for k, v in res['parametres'].items() if k not in ['revenu1', 'revenu2']}
                        },
                        'resultats': res['resultats']
                    }

                    resultats.append(cas_complet)
                    pbar.update(1)
                except Exception as e:
                    print(f"Erreur pour le cas {cas_index}: {case}")
                    print(e)
                    continue
        
        print(f"\nSauvegarde des {len(resultats)} cas traités...")
        output_filename = f'resultats_{nobs}_cas.json'
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(resultats, f, ensure_ascii=False, indent=2)
        print(f"Résultats sauvegardés dans {output_filename}")
        
    except Exception as e:
        print("Une erreur est survenue:")
        print(e)
    finally:
        if calc:
            calc.close()

if __name__ == "__main__":
    main()