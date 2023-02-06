from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import re
import time
from datetime import datetime
from datetime import date

driver = webdriver.Firefox()

today = datetime.today().strftime('%Y-%m-%d')

data = []

def add_to_database(league, fixture, home_pred, draw_pred, away_pred, average_goals):
    ref = db.reference("/forebet/" + date + "/")
    ref.push({
        'league': "" if league is not None else league,
        'fixture': "" if fixture is not None else fixture,
        'home_pred': "" if home_pred is not None else home_pred,
        'draw_pred': "" if draw_pred is not None else draw_pred,
        'away_pred': "" if fixture is not None else away_pred,
        'average_goals': "" if average_goals is not None else average_goals,
    })

def get_games(date):
	driver.get("https://www.forebet.com/en/football-predictions/predictions-1x2/" + date)
	driver.maximize_window()

	wait = WebDriverWait(driver, 10)

	try:
		driver.find_element_by_xpath('//span[text()="More [+]"]').click()
		time.sleep(1)
	except Exception as e:
		print("")

	games = driver.find_elements_by_xpath('//div[contains(@class, "rcnt")]')

	for x in games:
		temperature = '-'
		weather = '-'

		try:
			ActionChains(driver).move_to_element(x)

			predictions = re.findall('..',x.find_element_by_class_name("fprc").text)

			home_pred = predictions[0]
			draw_pred = predictions[1]
			away_pred = predictions[2]

			first = date.split(' ')[0]

			predicted = x.find_element_by_class_name("forepr").text
			fixture = x.find_element_by_class_name("homeTeam").text + " v " + x.find_element_by_class_name("awayTeam").text
			average_goals = float(x.find_element_by_class_name("avg_sc.tabonly").text)

			# print(x.find_element_by_class_name("tnmscn"))

			# League Name
			location = x.find_element_by_class_name("flsc").get_attribute("onclick").split("(",1)[1][:-1].split(",")
			country = location[2].replace("'", "")
			league = country + ": " + location[3].replace("'", "")

			try:
				score = x.find_element_by_class_name('l_scr').text
				prediction = x.find_element_by_class_name('forepr').text

				short_tag = x.find_element_by_class_name('shortTag').text

				print(fixture)

			except Exception as e:
				print(e)

			if len(short_tag) == 3 and (short_tag == "EPL" or "JO" or short_tag[2].isdigit()):
				game = [league, fixture, home_pred, draw_pred, away_pred, average_goals]
				add_to_database(league, fixture, home_pred, draw_pred, away_pred, average_goals )
				data.append(game)

		except Exception as e:
			print(e)


get_games(today)

driver.quit()
