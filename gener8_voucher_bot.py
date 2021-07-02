'''
    TODO
    ----
    - Error handling:
        Error log
        Info log
        Recapcha
        Not signed in


        redeem button xpath =
        redeem button pressed route =


'''

# Load Modules
from datetime import datetime, timedelta
from decouple import config
from selenium import webdriver
from tempfile import NamedTemporaryFile
import chromedriver_binary
import csv
import os
import shutil
import time

# Environment variables
login_url          = config('GENER8_LOGIN_URL')
product_url        = config('GENER8_PRODUCT_URL')
combined_emails    = config('GENER8_EMAILS')
combined_passwords = config('GENER8_PASSWORDS')

# Create a dictionary of users emails and passwords
emails    = combined_emails.split(',')
passwords = combined_passwords.split(',')
users     = {}

for email in emails:
    index = emails.index(email)
    users[email] = passwords[index]

# Element XPaths
email_input_xpath    = '/html/body/div[2]/div[2]/section/div[3]/div[1]/form/label[1]/input'
password_input_xpath = '/html/body/div[2]/div[2]/section/div[3]/div[1]/form/label[2]/input'
login_button_xpath   = '/html/body/div[2]/div[2]/section/div[3]/div[1]/form/div/div[2]/button'
balance_xpath        = '/html/body/div[2]/div[2]/section/div[3]/div[1]/dl/dd[1]'

days_or_hrs_xpath  = '/html/body/div[4]/div[2]/section/section/article/div/div/div[2]/div[2]/div[2]/div[1]/div[2]'
hrs_or_mins_xpath  = '/html/body/div[4]/div[2]/section/section/article/div/div/div[2]/div[2]/div[2]/div[3]/div[2]'
mins_or_secs_xpath = '/html/body/div[4]/div[2]/section/section/article/div/div/div[2]/div[2]/div[2]/div[5]/div[2]'

time1_xpath = '/html/body/div[4]/div[2]/section/section/article/div/div/div[2]/div[2]/div[2]/div[1]/div[1]/div/div'
time2_xpath = '/html/body/div[4]/div[2]/section/section/article/div/div/div[2]/div[2]/div[2]/div[3]/div[1]/div/div'
time3_xpath = '/html/body/div[4]/div[2]/section/section/article/div/div/div[2]/div[2]/div[2]/div[5]/div[1]/div/div[2]'

# Configure webdriver
options = webdriver.ChromeOptions()
options.add_argument("--incognito")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--start-maximized")

# Log into Gener8 account
def login(browser, email, password):
    browser.get(login_url)
    time.sleep(2)

    email_input = browser.find_element_by_xpath(email_input_xpath)
    email_input.send_keys(email)

    password_input = browser.find_element_by_xpath(password_input_xpath)
    password_input.send_keys(password)

    # After logging in, wait for redirect to dashboard
    login_button = browser.find_element_by_xpath(login_button_xpath)
    login_button.click()
    time.sleep(2)

    if browser.current_url == product_url:
        return True
    else:
        return False

# Update CSV file
def update_csv(user, voucher_quantity, voucher_in_stock_date):
    current_time  = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    dir_path      = os.path.dirname(os.path.realpath(__file__))
    csv_file_name = 'voucher_status.csv'
    csv_file      = dir_path + '\\' + csv_file_name
    temp_file     = NamedTemporaryFile(mode='w', delete=False)
    fields        = ['last_updated', 'user', 'quantity_vouchers_redeemable', 'voucher_in_stock_date']

    try:
        with open(csv_file, 'r') as csv_file, temp_file:
            reader = csv.DictReader(csv_file, fieldnames=fields)
            writer = csv.DictWriter(temp_file, fieldnames=fields)
            for row in reader:
                if voucher_in_stock_date:
                    row['voucher_in_stock_date'] = voucher_in_stock_date
                else:
                    if row['user'] == user:
                        row['last_updated']                 = current_time
                        row['user']                         = user
                        row['quantity_vouchers_redeemable'] = voucher_quantity
                writer.writerow(row)
    except:
        return False
    else:
        shutil.move(temp_file.name, csv_file)
        return True

# Retrieve Gener8 balances
def check_balances():
    for user in users:
        email    = user
        password = users[user]

        browser = webdriver.Chrome(options=options)
        browser.implicitly_wait(10)

        success = login(browser, email, password)

        if not success:
            browser.close()
            return 'ERROR: Login Error'

        # Get Gener8 Account Balance from dashboard
        balance_element  = browser.find_element_by_xpath(balance_xpath)
        balance          = float(balance_element.text)
        voucher_quantity = int(balance // 50)

        # Close browser
        browser.close()

        # Save balance to CSV file
        success = update_csv(user=user, voucher_quantity=voucher_quantity)

        if not success:
            return 'ERROR: CSV error'
        else:
            return 'SUCCESS: Retrieved balance of', user, 'and updated CSV file'

# Find when Amazon gift cards are next available & record time
def check_voucher():
    browser = webdriver.Chrome(options=options)
    browser.implicitly_wait(10)

    # Use the first user to login
    email    = list(users.keys())[0]
    password = list(users.values())[0]

    success = login(browser, email, password)

    if not success:
        browser.close()
        return 'ERROR: Login Error'

    browser.get(product_url)

    # Assign default variable values
    days_or_hrs_element   = browser.find_element_by_xpath(days_or_hrs_xpath)
    hrs_or_mins_element   = browser.find_element_by_xpath(hrs_or_mins_xpath)
    mins_or_secs_element  = browser.find_element_by_xpath(mins_or_secs_xpath)
    voucher_in_stock_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if days_or_hrs_element.text == 'days':
        days_until_in_stock_element = browser.find_element_by_xpath(time1_xpath)
        days_until_in_stock         = int(days_until_in_stock_element.text)
        voucher_in_stock_date       += timedelta(days=days_until_in_stock)
    elif days_or_hrs_element.text == 'hrs':
        hours_until_in_stock_element = browser.find_element_by_xpath(time1_xpath)
        hours_until_in_stock         = int(hours_until_in_stock_element.text)
        voucher_in_stock_date        += timedelta(hours=hours_until_in_stock)
    if hrs_or_mins_element.text == 'hrs':
        hours_until_in_stock_element = browser.find_element_by_xpath(time2_xpath)
        hours_until_in_stock         = int(hours_until_in_stock_element.text)
        voucher_in_stock_date        += timedelta(hours=hours_until_in_stock)
    elif hrs_or_mins_element.text == 'mins':
        minutes_until_in_stock_element = browser.find_element_by_xpath(time2_xpath)
        minutes_until_in_stock         = int(minutes_until_in_stock_element.text)
        voucher_in_stock_date          += timedelta(minutes=minutes_until_in_stock)
    if mins_or_secs_element.text    == 'mins':
        minutes_until_in_stock_element = browser.find_element_by_xpath(time3_xpath)
        minutes_until_in_stock         = int(minutes_until_in_stock_element.text)
        voucher_in_stock_date          += timedelta(minutes=minutes_until_in_stock)

    browser.close()

    success = update_csv(voucher_in_stock_date=voucher_in_stock_date)

    if not success:
        return 'ERROR: CSV error'
    else:
        return 'SUCCESS: Retrieved voucher in stock date and updated CSV file'

# Redeem vouchers for users
def redeem_vouchers():
    for user in users:
        email    = user

        with open('file.csv') as csv_file:
            reader = csv.reader(csv_file)
            for row in reader:
                if row['user'] == user:
                    voucher_quantity = row['quantity_vouchers_redeemable']

        if voucher_quantity < 1:
            result = 'User' + user 'has no vouchers to redeem'
            return result
        else:
            password = users[user]

            browser = webdriver.Chrome(options=options)
            browser.implicitly_wait(10)

            success = login(browser, email, password)

            if not success:
                browser.close()
                return 'ERROR: Login Error'

            redeemable = False

            while redeemable == False:
                browser.get(product_url)


            success = update_csv(voucher_in_stock_date=voucher_in_stock_date)

            if not success:
                return 'ERROR: CSV error'
            else:
                return 'SUCCESS: Retrieved voucher in stock date and updated CSV file'

# Run program
result = check_balances()
print('Check balances result:', result)
time.sleep(1)

result = check_voucher()
print('Check voucher result:', result)
time.sleep(1)

result = redeem_vouchers()
print('Redeem voucher result:', result)
