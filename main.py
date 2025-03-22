from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
import requests
import os
import time
from dotenv import load_dotenv


load_dotenv()

email = os.getenv("EMAIL")
password = os.getenv("PASSWORD")

# Set up Chrome
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Go to PASSport login page
driver.get("https://www.publix.org/azure/AzureLogIn")

# Wait for the login button and click it
wait = WebDriverWait(driver, timeout = 360)
login_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(., "Log in")]')))
login_button.click()

# Wait for email input
email_field = wait.until(EC.presence_of_element_located((By.ID, "i0116")))
email_field.send_keys(email)
time.sleep(1.5)

# Click "Next"
next_btn = wait.until(EC.element_to_be_clickable((By.ID, "idSIButton9")))
next_btn.click()
time.sleep(1.5)

# Wait for password input
password_field = wait.until(EC.presence_of_element_located((By.ID, "i0118")))
password_field.send_keys(password)  # Or use getpass.getpass() for privacy
time.sleep(1.5)

# Click "Sign-in"
next_btn = wait.until(EC.element_to_be_clickable((By.ID, "idSIButton9")))
next_btn.click()
time.sleep(1.5)

# Click "Text feature"
text_option = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "tile")))
text_option.click()

# Click "Asks for 2a code"
code_input = wait.until(EC.presence_of_element_located((By.NAME, "otc")))
auth_code = input("📲 Enter the 2FA code you received via text: ")
code_input.send_keys(auth_code)

verify_btn = wait.until(EC.element_to_be_clickable((By.ID, "idSubmit_SAOTCC_Continue")))
verify_btn.click()

# Click "Hovers over workplace"
workplace_tab = wait.until(EC.presence_of_element_located((By.XPATH, '//strong[text()="Workplace"]/ancestor::div[contains(@class, "menu-desktop-item")]')))
ActionChains(driver).move_to_element(workplace_tab).perform()
time.sleep(2)

# Click "Clicks Schedule"
schedule_link = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Schedule")))
schedule_link.click()
time.sleep(2)

schedule_container = wait.until(
    EC.presence_of_element_located((By.CLASS_NAME, "tab-content"))
)

# NEW: Wait for actual visible text inside it
wait.until(lambda driver: schedule_container.text.strip() != "")
# Take a screenshot of just the schedule section
schedule_container.screenshot("schedule_section.png")

webhook_url = "https://discord.com/api/webhooks/1352881535220711424/t4NPuJQHyTOvPKyIx6H6bHWQLI73IeuXm468OibNaREnyVj-Ph8B1jrk4UKeQ2U3ahLD"  # Replace with your actual webhook

screenshot_path = "schedule_section.png"

driver.execute_script("arguments[0].scrollIntoView(true);", schedule_container)
time.sleep(3)  # wait a few seconds to let it fully render
schedule_container.screenshot("schedule_section.png")

with open("schedule_section.png", "rb") as f:
    file = {"file": f}
    payload = {
        "content": "📅 Here's your work schedule loser!",
        "username": "Publix"
    }

    response = requests.post(webhook_url, data=payload, files=file)

if response.status_code == 200:
    print("✅ Schedule successfully posted to Discord!")
    try:
        os.remove("schedule_section.png")
        print("🗑️ Screenshot deleted after upload.")
    except Exception as e:
        print("⚠️ Could not delete screenshot:", e)
else:
    print(f"❌ Failed to post to Discord. Status code: {response.status_code}")
    print(response.text)  # See the actual error message

input("⏸ Press Enter to quit...")
