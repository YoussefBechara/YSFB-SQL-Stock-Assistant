from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
from webdriver_manager.firefox import GeckoDriverManager
from PIL import Image
from IPython.display import display
import io
import os
import time
# Set up headless Firefox
options = FirefoxOptions()
options.add_argument("--headless")

# Use GeckoDriverManager to handle driver installation
service = FirefoxService(GeckoDriverManager().install())

# Create the driver instance
driver = webdriver.Firefox(service=service, options=options)

# Open a website
driver.get('http://www2.keiyaku.city.osaka.lg.jp/OsakaCity-PPI/PPI228index.html')
big_frames = driver.find_elements(By.TAG_NAME,'frame')
driver.switch_to.frame(big_frames[1])
small_frames = driver.find_elements(By.TAG_NAME,'frame')
driver.switch_to.frame(small_frames[0])
#print(website.page_source)
buttons = driver.find_element(By.XPATH, '/html/body/table[2]/tbody/tr[2]/td/a')
#[b1, b2, b3 ....]
buttons.click()
time.sleep(10)
# Take a screenshot
screenshot = driver.get_screenshot_as_png()

# Save the screenshot to a file to verify
screenshot_path = "screenshot.png"
with open(screenshot_path, "wb") as file:
    file.write(screenshot)

# Close the browser
driver.quit()

# Display the screenshot
try:
    image = Image.open(io.BytesIO(screenshot))
    display(image)
except Exception as e:
    print(f"An error occurred: {e}")

# Confirm the screenshot file exists and is not empty
if os.path.exists(screenshot_path):
    print(f"Screenshot saved successfully at: {os.path.abspath(screenshot_path)}")
else:
    print("Screenshot was not saved.")
