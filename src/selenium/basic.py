from selenium import webdriver
from selenium.webdriver.common.by import By
import time

class SimpleBot:
    def __init__(self, url):
        self.driver = webdriver.Firefox()
        self.driver.get(url)

    def fill_field(self, selector, value):
        element = self.driver.find_element(By.ID, selector)
        element.clear()
        element.send_keys(value)

    def extract_data(self, selector, attribute="value"):
        element = self.driver.find_element(By.ID, selector)
        return element.get_attribute(attribute)

    def close(self):
        self.driver.quit()

if __name__ == "__main__":
    # Initialize bot with URL
    bot = SimpleBot("https://www.finances.gouv.qc.ca/ministere/outils_services/outils_calcul/revenu_disponible/outil_revenu.asp")

    # Fill a form field
    bot.fill_field("Revenu1", "75000")
    time.sleep(0.5)  # Simple pause

    # Extract data from field
    result = bot.extract_data("RD_new")
    print(f"Extracted data: {result}")

    # Close browser
    bot.close()