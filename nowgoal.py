import requests
import time
from datetime import datetime, timedelta, date
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import firebase_admin
from firebase_admin import credentials, db
import json
from selenium.webdriver.chrome.options import Options
import re
from selenium.common.exceptions import NoSuchElementException
import traceback
from datetime import datetime
from pytz import timezone

# Scraping stats from nowgoal and adding to firebase

# Wait until statistics pop up
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--mute-audio")
chrome_options.add_argument("--disable-gpu")
chrome_driver = "/Users/clay/Documents/chromedriver"
driver = webdriver.Chrome(options=chrome_options, executable_path=chrome_driver)

notification_set = False

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin = firebase_admin.initialize_app(cred, {'databaseURL': 'https://betting-44880-default-rtdb.firebaseio.com/'})

ref = db.reference("/stats/")

def send_notification():
    TOKEN = "5722739183:AAEac_PuOS1hVkCd4JzQez8SqzA1aqSqJ5c"
    chat_id = "5403065167"

    text = "There's an error with the stats"

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={text}"
    r = requests.get(url)

def nowgoal():
    global notification_set
    today = datetime.now().strftime('%Y-%m-%d')
    driver.get('https://www.nowgoal.com/football/live')
    driver.maximize_window()

    wait = WebDriverWait(driver, 10)

    while True:
        try:
            if notification_set == False:
                driver.find_element(By.CLASS_NAME, "setting").click()
                time.sleep(3)
                # driver.find_element(By.ID, "set_notify").find_elements(By.TAG_NAME, "li")[1].click()
                driver.find_element(By.XPATH, '//div[text()="OK"]').click()
                notification_set = True

            games = driver.find_elements(By.CLASS_NAME, "item.matchdiv.live")

            for x in games:
                game = {}
                try:
                    ActionChains(driver).move_to_element(x)

                    red = x.find_element(By.CLASS_NAME, "red").text

                    minute = re.sub('[^0-9]','', red) if red != 'HT' else red

                    if minute != '' and (minute == 'HT' or (int(minute) > 74 and int(minute) < 78)):
                        home_team = x.find_element(By.CLASS_NAME, "homeTeam").find_element(By.CLASS_NAME, "name").text
                        away_team = x.find_element(By.CLASS_NAME, "guestTeam").find_element(By.CLASS_NAME, "name").text

                        fixture = (home_team + ' v ' + away_team).replace('.', ' ').replace('/', ' ')

                        game['fixture'] = fixture

                        ht_exists = db.reference("/stats/").child(fixture).child('HT').get()
                        seventy_exists = db.reference("/stats/").child(fixture).child('76').get()

                        # Stopping unnecessary scrapes
                        if (minute == 'HT' and ht_exists == None) or (int(minute) > 74 and int(minute) < 78 and ht_exists != None and seventy_exists == None):
                            try:
                                x.find_element(By.CLASS_NAME, "icon.iconfont.icon-font-open-off.close-out").click()
                                x.find_element(By.XPATH, '//li[text()="Statistics"]').click()

                                wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "indexItem")))
                                stats = x.find_elements(By.CLASS_NAME, 'indexItem')

                                stats_list = []

                                game_stats = {}

                                for i in stats:
                                    stats_list.append(i.text.split('\n'))

                                for i in stats_list:
                                    game_stats[i[1]] = [re.sub('[^0-9]','', i[0]), re.sub('[^0-9]','', i[2])]

                                game['stats'] = game_stats

                                status = 'HT' if minute == 'HT' else '76'

                                if minute == "HT":
                                    db.reference("/stats/").child(fixture).set({"date": str((datetime.now(timezone('Europe/London')) - timedelta(minutes=45)).strftime('%Y-%m-%d %H:%M'))})

                                db.reference("/stats/").child(fixture).child(status).update(game_stats)

                                x.find_element(By.CLASS_NAME, 'close').click()

                            except NoSuchElementException:
                                traceback.print_exc()
                                # print("No Element")

                except Exception as e:
                    # print(e)
                    traceback.print_exc()

            time.sleep(60)

        except Exception as e:
            driver.save_screenshot("screenshot.png")
            driver.quit()
            nowgoal()
            send_notification()
            traceback.print_exc()

nowgoal()
