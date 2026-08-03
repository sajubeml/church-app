import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os

options = Options()
options.add_argument("--headless=new")
driver = webdriver.Chrome(options=options)

file_url = "file:///" + os.path.abspath("index.html").replace("\\", "/")
print("Opening:", file_url)
driver.get(file_url)

logs = driver.get_log("browser")
print("Browser logs:")
for entry in logs:
    print(entry)

driver.quit()
