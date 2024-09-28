import telebot
import requests
from bs4 import BeautifulSoup

TOKEN = '7574930334:AAFwl7p2VRwXy0B0Sb3vCElQ8v3X4cm6slo'.strip()

bot = telebot.TeleBot(TOKEN)

# Store cookies in a global dictionary
cookies_dict = {}

# Function to parse cookies from user input
def parse_cookies(cookies_input):
    cookies = {}
    cookie_list = cookies_input.split(";")
    for cookie in cookie_list:
        if "=" in cookie:
            key, value = cookie.strip().split("=", 1)
            cookies[key] = value
        else:
            raise ValueError("Each cookie must contain an '=' character.")
    return cookies

# Step 1: Start command to ask for cookies
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Welcome! Please provide your cookies in this format: `PHPSESSID=value; sessionToken=value;`")

# Step 2: Receive cookies input from the user
@bot.message_handler(func=lambda message: True)
def set_cookies(message):
    global cookies_dict
    try:
        cookies_dict = parse_cookies(message.text)
        bot.reply_to(message, "Cookies set successfully! Now fetching job listings.")
        send_internshala_job_listings(message)
    except ValueError as e:
        bot.reply_to(message, f"Error: {str(e)}")

# Step 3: Fetch job listings from Internshala with debugging
def fetch_internshala_jobs(cookies):
    url = "https://internshala.com/internships"
    
    # Send the request with cookies
    response = requests.get(url, cookies=cookies)

    # Check if response is valid
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # Log the HTML for debugging
        print("Response HTML:", soup.prettify())  # This will print the raw HTML to the terminal
        
        job_listings = []

        # Example of how to find job title elements - adjust based on actual HTML structure
        for job_card in soup.find_all('div', class_='internship_meta'):
            title_element = job_card.find('a', class_='job-title-href')
            company_element = job_card.find('p', class_='company-name')
            location_element = job_card.find('span', class_='location_names')
            
            if title_element and company_element and location_element:
                title = title_element.text.strip()
                company = company_element.text.strip()
                location = location_element.text.strip()
                job_listings.append(f"{title} at {company}, {location}")
        
        return job_listings
    else:
        print(f"Failed to fetch jobs. Status code: {response.status_code}")
        return []

# Step 4: Send job listings to the user
def send_internshala_job_listings(message):
    job_listings = fetch_internshala_jobs(cookies_dict)
    
    if job_listings:
        for job in job_listings:
            bot.reply_to(message, job)
    else:
        bot.reply_to(message, "No jobs found. Please check your cookies or try again later.")

# Start the bot polling to receive messages
bot.polling()
