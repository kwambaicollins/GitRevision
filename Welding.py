import time
import os
import requests
from twocaptcha import TwoCaptcha
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Constants
API_KEY = "bfd817800959c6538809ae4c0fa53231a"  # Your 2Captcha API key
SITE_KEY = "f9441a9e-cf26-451a-9aa4-6e526ec0e222"  # hCaptcha site key from iframe
PAGE_URL = "https://satuk-awards.vercel.app/vote"
MAX_CAPTCHA_RETRIES = 3  # Maximum retries for solving captcha

def solve_captcha(api_key, site_key, page_url, max_retries=3):
    """
    Solves the hCaptcha using the 2Captcha API.
    Returns the captcha solution if successful, else None.
    """
    for attempt in range(max_retries):
        print(f"Requesting hCaptcha solution (Attempt {attempt + 1})")
        
        # Request captcha solving task from 2Captcha
        response = requests.get(
            f"http://2captcha.com/in.php?key={api_key}&method=hcaptcha&sitekey={site_key}&pageurl={page_url}"
        )
        
        if response.text.startswith("OK|"):
            captcha_id = response.text.split('|')[1]

            # Poll for the captcha result
            captcha_response = None
            for _ in range(10):  # 10 attempts, wait 5 seconds each
                time.sleep(5)
                result = requests.get(f"http://2captcha.com/res.php?key={api_key}&action=get&id={captcha_id}")
                
                if result.text.startswith("OK|"):
                    captcha_response = result.text.split('|')[1]
                    break
                elif result.text != "CAPCHA_NOT_READY":
                    raise Exception(f"Error solving captcha: {result.text}")

            if captcha_response:
                print("Captcha solved successfully.")
                return captcha_response
            else:
                print("Captcha solving failed, retrying...")
        else:
            print("Error requesting captcha solution:", response.text)

    print(f"Failed to solve captcha after {max_retries} attempts.")
    return None

def submit_form_with_captcha_solution(captcha_solution):
    browser = webdriver.Chrome()

    # Open the voting page
    browser.get(PAGE_URL)

    # Wait for iframe to load
    WebDriverWait(browser, 10).until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, '#root > div > div > div > form > div:nth-child(26) > div > iframe')))

    # Inject the captcha solution into the page
    browser.execute_script(
        f"document.querySelector('[name=\"g-recaptcha-response\"]').innerHTML = '{captcha_solution}'"
    )

    # Click the submit button
    submit_button = browser.find_element(
        By.CSS_SELECTOR, "#root > div > div > div > form > button"
    )
    submit_button.click()

    print("Form submitted successfully.")

if __name__ == "__main__":
    # Step 1: Solve the captcha
    captcha_response = solve_captcha(API_KEY, SITE_KEY, PAGE_URL)
    if captcha_response:
        print("Captcha solution:", captcha_response)

        # Step 2: Submit the form with the solved captcha
        submit_form_with_captcha_solution(captcha_response)
    else:
        print("Failed to solve captcha.")
