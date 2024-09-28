from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.safari.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import telebot
import os

TOKEN = '7574930334:AAFwl7p2VRwXy0B0Sb3vCElQ8v3X4cm6slo'.strip()

bot = telebot.TeleBot(TOKEN)
cookies_dict = {}  # Global variable to store cookies
waiting_for_cookies = True  # Track if bot is waiting for cookies anymore
job_listings = []  # List to store job listings

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
    except Exception:
        raise ValueError("Invalid cookie format. Please provide cookies in the format: PHPSESSID=value; sessionToken=value;")
    return cookies

@bot.message_handler(commands=['start'])
def start(message):
    welcome_message = """
    Welcome to the Job Find Application Bot! 🎉

    Hi there! I'm here to simplify your job search and help you find the perfect opportunity. Whether you’re hunting for internships or full-time roles, I can assist you in applying on LinkedIn and Internshala with ease.

    ✨ How it works:
    1. Please provide your cookies in this format: `PHPSESSID=value; sessionToken=value;`
    2. Pick a job from the list I will share to start your application.
    3. Sit back and relax while I take care of the rest!

    Let’s kick off your job search :)
    """
    bot.reply_to(message, welcome_message)

@bot.message_handler(func=lambda message: waiting_for_cookies)
def set_cookies(message):
    global cookies_dict, waiting_for_cookies
    try:
        cookies_dict = parse_cookies(message.text)
        bot.reply_to(message, "Cookies set successfully! Now fetching job listings.")
        waiting_for_cookies = False  # Now not waiting for cookies anymore
        send_internshala_job_listings(message, cookies_dict)
    except ValueError as e:
        bot.reply_to(message, f"Error: {str(e)}")

@bot.message_handler(func=lambda message: not waiting_for_cookies)
def select_job(message):
    job_number = message.text.strip()
    try:
        job_number = int(job_number)  # Convert input to an integer
        apply_for_job(message, job_number)
    except ValueError:
        bot.reply_to(message, "Please select a valid job number.")

def fetch_internshala_jobs(cookies, limit=5):
    url = "https://internshala.com/internships"
    driver.get(url)

    # Add the cookies to the Selenium session
    for key, value in cookies.items():
        driver.add_cookie({'name': key, 'value': value})

    driver.refresh()  # Refresh the page to load with the new cookies

    global job_listings  # Use the global job_listings list
    job_listings = []  # Clear the previous listings
    try:
        # Wait until the job cards are loaded
        wait = WebDriverWait(driver, 10)
        job_cards = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'internship_meta')))
        print("Job cards found!")
        for index, job_card in enumerate(job_cards):
            if index >= limit:
                break
            try:
                # Fetch job details
                title_element = job_card.find_element(By.CLASS_NAME, 'job-title-href')
                title = title_element.text.strip()

                company_element = job_card.find_element(By.CLASS_NAME, 'company-name')
                company = company_element.text.strip()

                job_link = job_card.find_element(By.CLASS_NAME, 'job-title-href').get_attribute('href')

                job_info = {
                    "title": title,
                    "company": company,
                    "link": job_link
                }

                job_listings.append(job_info)

            except Exception as e:
                print(f"Error fetching details for job card: {str(e)}")
    except Exception as e:
        print(f"Error fetching job cards: {str(e)}")

    return job_listings

def send_internshala_job_listings(message, cookies_dict):
    limit = 5
    job_listings = fetch_internshala_jobs(cookies_dict, limit)
    
    if job_listings:
        job_message = "Here are the job listings:\n"
        for index, job in enumerate(job_listings):
            job_message += f"{index + 1}. {job['title']} at {job['company']}\n"
            job_message += f"Link: {job['link']}\n"
        job_message += "Please select a job by number to apply."
        bot.reply_to(message, job_message)
    else:
        bot.reply_to(message, "No jobs found. Please check your cookies or try again later.")

def apply_for_job(message, job_number):
    global job_listings  # Access the global job_listings list
    job_number -= 1  # Adjusting for 0-based index

    if job_number < 0 or job_number >= len(job_listings):
        bot.reply_to(message, "Invalid job selection. Please select a valid job number.")
        return

    job_link = job_listings[job_number]['link']  # Access the link from job_listings

    driver.get(job_link)  # Navigate to the job application page

    try:
        # Wait for the apply button and click it
        wait = WebDriverWait(driver, 10)
        apply_button = wait.until(EC.presence_of_element_located((By.ID, 'easy_apply_button')))
        apply_button.click()  # Click on the apply button

        # Optionally, add more code here to handle the application form if needed

        bot.reply_to(message, "Application submitted successfully.")
    except Exception as e:
        bot.reply_to(message, f"Error applying for job: {str(e)}")

try:
    bot.polling()
finally:
    # Quit the driver after polling loop
    driver.quit()
