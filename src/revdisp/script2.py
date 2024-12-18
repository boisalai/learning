from selenium import webdriver
from selenium.webdriver.common.by import By
from pathlib import Path
import time

class SimpleBot:
    def __init__(self, url):
        self.driver = webdriver.Firefox()
        self.driver.get(url)

    def fill_field(self, selector, value):
        element = self.driver.find_element(By.ID, selector)
        element.clear()
        element.send_keys(value)
        self.driver.execute_script(f"recalc_onclick('{selector}')")

    def extract_data(self, selector, attribute="value"):
        element = self.driver.find_element(By.ID, selector)
        return element.get_attribute(attribute)

    def close(self):
        self.driver.quit()

if __name__ == "__main__":
    current_dir = Path(__file__).parent
    file_path = current_dir / "../../utils/revdisp/index.html"
    absolute_path = file_path.resolve()
    url = f"file://{absolute_path}"

    bot = SimpleBot(url)
    bot.fill_field("Revenu1", "75000")
    # time.sleep(0.05)
    # input("Press Enter to continue...") 

    result = bot.extract_data("RD_new")
    print(f"Extracted data: {result}")

    bot.close()