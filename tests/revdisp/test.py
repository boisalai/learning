from selenium import webdriver
from selenium.webdriver.common.by import By
from pathlib import Path
import time
import random


class TaxCalculatorTest:
    def __init__(self, url):
        self.driver = webdriver.Firefox()
        self.driver.get(url)
        
    def select_by_text(self, element_id, text):
        element = self.driver.find_element(By.ID, element_id)
        for option in element.find_elements(By.TAG_NAME, 'option'):
            if option.text.strip() == text.strip():
                option.click()
                break
        self.driver.execute_script(f"recalc_onclick('{element_id}')")
        
    def fill_field(self, selector, value):
        element = self.driver.find_element(By.ID, selector)
        element.clear()
        element.send_keys(str(value))
        self.driver.execute_script(f"recalc_onclick('{selector}')")
        
    def extract_results(self):
        results = {}
        result_fields = ['RD_new', 'QC_total_new', 'CA_total_new', 'Cotisation_new']
        for field in result_fields:
            element = self.driver.find_element(By.ID, field)
            results[field] = element.get_attribute('value')
        return results
    
    def close(self):
        self.driver.quit()
