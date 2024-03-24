from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
import requests
from bs4 import BeautifulSoup
import getindianname as name
import string
import random

def info(x):
  if print_info:
    print(f"[INFO] {x}")

def error(x):
  if print_error :
    print(f"[ERROR] {x}")

def debug(x):
  if print_debug:
    print(f"[DEBUG] {x}")

def saveAccount(account):
  file = open(account_file, "a+")
  file.write(account+"\n")
  file.close()

def createMail():
  rawEmail = requests.post("https://api.internal.temp-mail.io/api/v3/email/new", data={"min_name_length":10,"max_name_length":10}).json()
  return rawEmail["email"]

def getVerificationLink(email):
  emails = requests.get(f"https://api.internal.temp-mail.io/api/v3/email/{email}/messages")
  try:
    html = emails.json()[0]["body_html"]
  except:
    time.sleep(10)
    html = emails.json()[0]["body_html"]
  soup = BeautifulSoup(html, 'html.parser').find('a', id='bottom-button')
  return soup.get('href')

def generate():
  start_time = time.time()
  url = "https://mega.nz/register"
  accountUrl = "https://mega.nz/account"

  info("Generating User details")
  full_name = name.randname()
  fullname = full_name.split()
  first_name = fullname[0]
  last_name = fullname[1]
  passwd = ''.join(random.choice(string.ascii_letters + string.digits + "@#&()[]") for _ in range(12))

  email = createMail()
  info("Generated "+email)

  info("Initiating Account Creation...")
  options = webdriver.ChromeOptions()
  options.add_argument('--headless')
  options.add_argument('--no-sandbox')
  options.add_argument('--disable-dev-shm-usage')

  driver = webdriver.Chrome(options=options)

  driver.get(url)

  WebDriverWait(driver, 300).until(EC.visibility_of_element_located((By.ID, 'register-firstname-registerpage2')))

  info("Filling user details...")

  driver.find_element(By.ID, "register-firstname-registerpage2").send_keys(first_name)
  driver.find_element(By.ID, "register-lastname-registerpage2").send_keys(last_name)
  driver.find_element(By.ID, "register-email-registerpage2").send_keys(email)
  driver.find_element(By.ID, "register-password-registerpage2").send_keys(passwd)
  driver.find_element(By.ID, "register-password-registerpage3").send_keys(passwd)
  driver.find_elements(By.XPATH, "/html/body/div[6]/div[1]/div[2]/div[2]/div[2]/div[1]/form/div[8]/div[1]/input")[0].click()
  driver.find_element(By.ID, "register-check-registerpage2").click()

  try :
    driver.find_element(By.XPATH, "/html/body/div[6]/div[1]/div[2]/div[2]/div[2]/div[1]/form/button")[0].click()
  except:
    driver.find_element(By.XPATH, "/html/body/div[6]/div[1]/div[2]/div[2]/div[2]/div[1]/form/button").click()

  try :
    WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.XPATH, "/html/body/section[5]/div[14]/section/div/div[2]/div[1]")))
    msgtxt = driver.find_element(By.XPATH, "/html/body/section[5]").text
    if (driver.find_element(By.XPATH, "/html/body/section[5]").text).startswith("Please check your email and click the link to confirm your "):
      info("Email Sent")
      info("Waiting for 2 second to recieve mail...")
      time.sleep(2)
    else :
      error("Unable to sent mail")
  except Exception as e:
    error(f"Timeout \n {e}")

  info("Getting verification link")
  verifyLink = getVerificationLink(email)

  info(verifyLink)

  driver.get(verifyLink)

  try :
    info("Verifying account")
    WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.ID, "login-password2")))
    driver.find_element(By.ID, "login-password2").send_keys(passwd)
    driver.find_element(By.XPATH, "/html/body/div[6]/div[1]/div[2]/div[2]/div[2]/div[1]/form/button").click()

  except Exception as e :
    error("Timeout\n"+str(e))

  account = f"{full_name}:{email}:{passwd}"
  print(f"[INFO] Account Created : {account}")
  saveAccount(account)
  info("Account Saved")

  info("Waiting for plan page to appears")

  WebDriverWait(driver, 120).until(EC.visibility_of_element_located((By.ID, "freeStart")))

  info("Selecting the free plann")
  driver.find_element(By.ID, "freeStart").click()

  driver.get(accountUrl)
  driver.save_screenshot("/content/freeplan.png")

  debug("Waiting for account page to open")

  driver.quit()
  info(f"Time taken : {time.time()-start_time} second")

  if print_debug or print_info or print_error :
    print("\n\n")

how_many_accounts = int(input("Enter number of account to generate : "))
account_file = "accounts.txt"
print_info = True
print_debug = True
print_error = True

print(f"Initiating Account Creation...\n\nUsers to generate : {how_many_accounts}\n\n")
for i in range(how_many_accounts):
  generate()
