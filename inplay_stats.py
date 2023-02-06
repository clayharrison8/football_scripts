import requests
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import json
from Naked.toolshed.shell import execute_js


# Getting inplay stats from either scorebing or skybet
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin = firebase_admin.initialize_app(cred, {'databaseURL': 'https://betting-44880-default-rtdb.firebaseio.com/'})

ref = db.reference("/stats/")

def send_notification():
    TOKEN = "5722739183:AAEac_PuOS1hVkCd4JzQez8SqzA1aqSqJ5c"
    chat_id = "5403065167"

    text = "There's an error with the stats"

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={text}"
    r = requests.get(url)


def add_stats_to_database(fixture, home_a, away_a, home_s_on, away_s_on, home_da, away_da, home_s_off, away_s_off, home_a_ratio, away_a_ratio, home_corners, away_corners, time, date):
    stats = {
        'home_a': int(home_a),
        'away_a': int(away_a),
        'home_s_on': int(home_s_on),
        'away_s_on': int(away_s_on),
        'home_da': int(home_da),
        'away_da': int(away_da),
        'home_s_off': int(home_s_off),
        'away_s_off': int(away_s_off),
        'home_a_ratio': int(home_a_ratio),
        'away_a_ratio': int(away_a_ratio),
        'home_corners': int(home_corners),
        'away_corners': int(away_corners),
    }

    if time == "HT":
        ref.child(fixture).set({"date": date})

    game_exists = ref.child(fixture).get()

    if game_exists != None:
        ref.child(fixture).child(time).update(stats)

def get_inplay_stats():
    today = datetime.now().strftime('%Y-%m-%d')

    # Grabbing stats from js file
    response = execute_js('test.js')
    f = open("stats.txt","r")
    lines = f.readlines()
    here = json.loads(lines[0])

    for i in here:
        try:
            home_a_ratio = int(i['homeDa']/i['homeA'] * 100)
            away_a_ratio = int(i['awayDa']/i['awayA'] * 100)

            status = i['status']

            time = ""

            if status == 'HT':
                time = status
            elif int(status) > 73 and int(status) < 77:
                time = "76"
            elif int(status) > 83 and int(status) < 86:
                time = "86"

            if time != "":
                add_stats_to_database(i['fixture'], i['homeA'], i['awayA'], i['homeSot'], i['awaySot'], i['homeDa'], i['awayDa'], i['homeSf'], i['awaySf'], home_a_ratio, away_a_ratio, i['homeC'], i['awayC'], time, today)

        except Exception as e:
            print(e)

def skybet():
    today = datetime.now().strftime('%Y-%m-%d')

    driver = webdriver.Firefox()

    try:
        games_list = []

        driver.get('https://m.skybet.com/in-play')
        driver.maximize_window()

        wait = WebDriverWait(driver, 30)

        # wait.until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Accept & Close')]"))).click()

        element = driver.find_element_by_class_name("js-page__cookies-accept").click()
        games = driver.find_elements_by_class_name("_xz2x8v")

        for x in range(len(games)):
            try:
                odds_list = []

                home_team = games[x].find_element_by_class_name("_1szonrm.homeName").text
                away_team = games[x].find_element_by_class_name("_1szonrm.awayName").text

                odds = games[x].find_elements_by_class_name("_1ou2dx2")

                games[x].find_element_by_class_name("_1ucbs6b").click()

                fixture = home_team + ' v ' + away_team

                stats = games[x].find_elements_by_class_name("_1d4ut32")

                home_a = int(stats[0].text)
                away_a = int(stats[1].text)
                home_s_on = int(stats[2].text)
                away_s_on = int(stats[3].text)
                home_da = int(stats[4].text)
                away_da = int(stats[5].text)
                home_s_off = int(stats[6].text)
                away_s_off = int(stats[7].text)
                home_a_ratio = int(home_da/home_a * 100)
                away_a_ratio = int(away_da/away_a * 100)

                corners = games[x].find_elements_by_class_name("_ae4rrb3")

                home_corners = int(corners[0].text)
                away_corners = int(corners[1].text)

                status = games[x].find_element_by_class_name("_zzy6qz").text.split(':')[0]

                time = ""

                if status == 'HT':
                    time = status
                elif int(status) > 73 and int(status) < 77:
                    time = "76"
                elif int(status) > 83 and int(status) < 86:
                    time = "86"

                if time != "":
                    add_stats_to_database(fixture, home_a, away_a, home_s_on, away_s_on, home_da, away_da, home_s_off, away_s_off, home_a_ratio, away_a_ratio, home_corners, away_corners, time, today)

            except Exception as e:
                    print(e)

        driver.quit()

    except Exception as e:
        print(e)

while True:
    try:
        get_inplay_stats()
    except Exception as e:
        skybet()
        send_notification()

    time.sleep(180)
