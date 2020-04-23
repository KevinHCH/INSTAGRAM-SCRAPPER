#!/usr/bin/env python3

# SELENIUM
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException

from pprint import pprint
from pathlib import Path
from dotenv import load_dotenv

import sys, os, time, json
import numpy as np

# PYMONGO
from pymongo import MongoClient
dbh = MongoClient("localhost", 27017)

# Database
ig_database = dbh["ig_users"]

# Table
ig_users = ig_database["ig_users"]

## CONFIG
load_dotenv()
USERNAME = os.getenv('USERNAME_IG')
PASSWORD = os.getenv('PASSWORD_IG')

TARGET = input("Type the Instagram user name: ").strip()

while len(TARGET) == 0:
  print("You must to insert a valid name \n")
  TARGET = input("Insert the Instagram name: ").strip()

print(f"Target user: {TARGET}")

URL = "https://www.instagram.com/"

DRIVER_PATH = "/usr/bin/chromedriver"
BRAVE_BROWSER_PATH = "/usr/bin/brave-browser"

driver_options = webdriver.ChromeOptions()
driver_options.binary_location = BRAVE_BROWSER_PATH
driver_options.add_argument("--incognito")
# driver_options.add_argument("--headless") #Lo ejecuta sin entorno gráfico

## MAIN
browser = webdriver.Chrome(executable_path=DRIVER_PATH, options=driver_options)

browser.implicitly_wait(10)
browser.get(URL)
browser.maximize_window()
# LOGIN
username_input = browser.find_element_by_name("username")
username_input.send_keys(USERNAME)

password_input = browser.find_element_by_name('password')
password_input.send_keys(PASSWORD)

submit = browser.find_element_by_css_selector('button[type="submit"]')
submit.click()

try:
  wait = WebDriverWait(browser, 10)
  # Para que busque el elemento se deben pasar los valores como tuplas
  selector = (By.CSS_SELECTOR, "div>button:last-of-type[tabindex='0']")
  not_now_btn = wait.until(EC.element_to_be_clickable(selector)).click()
  
except TimeoutException:
  print("Time to load took to mutch time")

new_url = f"{URL}{TARGET}"
browser.get(new_url)

imgs_list = []

total_pubs = browser.find_element_by_css_selector("main header section ul li:first-child > span:first-of-type > span").text.replace(".","")
total_pubs = int(total_pubs)

print(f"TOTAL PUBLICATIONS: {total_pubs}")
print("Searching imgs...\n")

scroll_bottom = """window.scrollTo({top:document.body.scrollHeight, behavior:'smooth'});
                   var totalHeight=document.body.scrollHeight; return totalHeight;"""
current_height = browser.execute_script(scroll_bottom)
match = False

while match == False:
  last_count = current_height
  time.sleep(3)
  current_height = browser.execute_script(scroll_bottom)

  imgs_script = """const imgObj = [...document.querySelectorAll('section article a')]
                                    .map(img => JSON.stringify({
                                                                \"img\": img.href, 
                                                                \"srcset\": [...img.children[0].querySelectorAll('img')][0].srcset
                                                              })); 
                                    return imgObj;"""
  
  imgs_dict = browser.execute_script(imgs_script)
  imgs_list.append([json.loads(item) for item in imgs_dict])
  # print(f"last_count: {last_count} -- current_height: {current_height}\n")
  
  if last_count == current_height:
    match = True

flatten = list(np.concatenate(imgs_list, axis=0))
uniques = list({value["img"]: value for value in flatten}.values())

final_dict = {"user_name": TARGET, "data": uniques}

# Write all the content in a JSON file #OPTIONAL
if len(sys.argv) == 2 and sys.argv[1] == "write":

  subdir = "data"
  current_dir = Path().cwd()
  result_dir = f"{current_dir}/{subdir}"

  if not Path(result_dir).is_dir():
    os.mkdir(result_dir)

  with open(f"{result_dir}/{TARGET}.json", "w+") as file:
    file.write(json.dumps(final_dict, indent=2))

#INSERT IN THE DATABASE
inserted_docs = ig_users.insert_one(final_dict)
total_rows = len(uniques)
if total_rows > 0:
  print(f"Have been inserted {total_rows} documents\n")
  print("Bye")

time.sleep(3)

browser.close()
