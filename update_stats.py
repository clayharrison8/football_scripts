import time
from datetime import datetime, timedelta, date
import firebase_admin
from firebase_admin import credentials, db
from fuzzywuzzy import process, fuzz
from pytz import timezone

# Adding stats to correct node in firebase

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin = firebase_admin.initialize_app(cred, {'databaseURL': 'https://betting-44880-default-rtdb.firebaseio.com/'})

def get_stats():
    stats_ref = db.reference("/stats").get()

    for stats_key, stats_value in stats_ref.items():
        # If 76th min stats collected, add to data node and remove from stats node
        time_game_added = datetime.strptime(stats_value['date'], '%Y-%m-%d %H:%M')

        try:
            date = str(time_game_added.strftime('%Y-%m-%d'))
            exists_76 = db.reference("/stats/").child(stats_key).child('76').get()

            if exists_76 != None:
                fixtures_ref = db.reference("/data/" + date).get()

                for key, value in fixtures_ref.items():
                    game = find_game(stats_key, value['fixture'])
                    if game != None:
                        db.reference("/data/").child(date).child(key).child("stats").update(stats_value)
                    db.reference("/stats").child(stats_key).delete()

        except Exception as e:
            print(stats_key, e)

        #  Getting hours between two dates
        current_time = datetime.strptime(str(datetime.now(timezone('Europe/London')).strftime('%Y-%m-%d %H:%M')), '%Y-%m-%d %H:%M')
        time_diff = (current_time - time_game_added).total_seconds()/(60*60)

        # If been over 3 hours, remove game from database
        if time_diff > 3:
            db.reference("/stats").child(stats_key).delete()

def find_game(fixture1, fixture2):
    ratio = fuzz.ratio(fixture1.lower(), fixture2.lower())
    partial_ratio = fuzz.partial_ratio(fixture1.lower(), fixture2.lower())
    token_sort_ratio = fuzz.token_sort_ratio(fixture1, fixture2)
    token_set_ratio = fuzz.token_set_ratio(fixture1, fixture2)

    if ratio > 75 or partial_ratio > 75 or token_set_ratio > 75 or token_sort_ratio > 75:
        return fixture2

get_stats()
