from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.safari.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import telebot

TOKEN = '7574930334:AAFwl7p2VRwXy0B0Sb3vCElQ8v3X4cm6slo'.strip()

bot = telebot.TeleBot(TOKEN)

# Set up Selenium WebDriver for Safari
service = Service()  # No path needed for Safari
driver = webdriver.Safari(service=service)

# Function to parse cookies from the user's input
def parse_cookies(cookie_str):
    cookies = {}
    try:
        pairs = cookie_str.split(';')
        for pair in pairs:
            key, value = pair.strip().split('=')
            cookies[key] = value
    except Exception as e:
        raise ValueError("Invalid cookie format. Please provide cookies in the format: PHPSESSID=value; sessionToken=value;")
    return cookies

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Welcome! Please provide your cookies in this format: `PHPSESSID=value; sessionToken=value;`")

@bot.message_handler(func=lambda message: True)
def set_cookies(message):
    try:
        cookies_dict = parse_cookies(message.text)
        bot.reply_to(message, "Cookies set successfully! Now fetching job listings.")
        send_internshala_job_listings(message, cookies_dict)
    except ValueError as e:
        bot.reply_to(message, f"Error: {str(e)}")

def fetch_internshala_jobs(cookies,limit=5):
    url = "https://internshala.com/internships"
    driver.get(url)

    # Add the cookies to the Selenium session
    for key, value in cookies.items():
        driver.add_cookie({'name': key, 'value': value})

    driver.refresh()  # Refresh the page to load with the new cookies

    job_listings = []
    try:
        # Wait until the job cards are loaded
        wait = WebDriverWait(driver, 10)
        job_cards = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'internship_meta')))
        print("Job cards found!")
        for index, job_card in enumerate(job_cards):
            if index >= limit:
                break
            try:
                # Fetch details
                title_element = job_card.find_element(By.CLASS_NAME, 'job-title-href')
                title = title_element.text.strip()
                print("Job Title found")

                company_element = job_card.find_element(By.CLASS_NAME, 'company-name')
                company = company_element.text.strip()
                print("Company found")

                # stipend_element = job_card.find_element(By.CLASS_NAME, 'desktop')
                # stipend = stipend_element.text.strip()
                

                # experience_element = job_card.find_element(By.CSS_SELECTOR, 'div.detail-row-1 > div:nth-child(2) > span')
                # experience = experience_element.text.strip()

                # location_element = job_card.find_element(By.CSS_SELECTOR, 'div.detail-row-1 > p > span > a')
                # location = location_element.text.strip()

                job_info = {
                    "title": title,
                    "company": company,
                    # "stipend":stipend,
                    # "experience":experience,
                    # "location":location
                }

                job_listings.append(job_info)

            except Exception as e:
                print(f"Error fetching details for job card: {str(e)}")
    except Exception as e:
        print(f"Error fetching job cards: {str(e)}")

    return job_listings

def send_internshala_job_listings(message, cookies_dict):
    limit=5
    job_listings = fetch_internshala_jobs(cookies_dict,limit)
    
    if job_listings:
        for job in job_listings:
            bot.reply_to(message, str(job))
    else:
        bot.reply_to(message, "No jobs found. Please check your cookies or try again later.")

bot.polling()

# Driver.quit() is handled outside polling loop
driver.quit()
