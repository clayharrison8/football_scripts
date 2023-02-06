from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from datetime import date
import csv
import traceback

# Grabbing data from firebase and creating csv file

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin = firebase_admin.initialize_app(cred, {'databaseURL': 'https://betting-44880-default-rtdb.firebaseio.com/'})

yesterdayTimeDate = datetime.now() - timedelta(days=1)
yesterday = yesterdayTimeDate.strftime('%Y-%m-%d')

columns = [
    'league', 'fixture', 'date', 'round', 'home_odds', 'away_odds', 'under_odds', 'league_avg',
    'home_recent_for', 'home_recent_against', 'home_recent_avg', 'away_recent_for', 'away_recent_against',
    'away_recent_avg', 'league_lg_76', 'league_lg_86', 'home_76_form', 'home_76_form_l5', 'away_76_form', 'away_76_form_l5','home_86_form', 'home_86_form_l5', 'away_86_form', 'away_86_form_l5','second_half_goals',
    'red_cards','hnw','anw','gd', 'total_home_goals', 'total_away_goals', 'h_shots', 'h_shots_on_target','h_attacks', 'h_dangerous_attacks',
    'h_a_to_da_ratio', 'a_shots', 'a_shots_on_target','a_attacks', 'a_dangerous_attacks', 'a_a_to_da_ratio', 'h_2H_shots', 'h_2H_shots_on_target',
    'h_2H_attacks', 'h_2H_dangerous_attacks', 'h_2H_a_to_da_ratio', 'a_2H_shots', 'a_2H_shots_on_target', 'a_2H_attacks', 'a_2H_dangerous_attacks', 'a_2H_a_to_da_ratio',
     'won_76','won_86'
]

games = []
ref = db.reference("/data/")
fixtures = ref.get()

count = 0
for date in fixtures:
    ref2 = db.reference("/data/" + date + "/")
    games2 = ref2.get()
    # print(games2, '\n')

    if date <= yesterday:
        for key, value in games2.items():
            count += 1

            try:

                league = value['league']
                fixture = value['fixture']

                # if 'UEFA' not in league and 'CONCACAF' not in league and 'World' not in league and 'Iran' not in league and 'Iraq' not in league:

                home_odds = value['home_odds']
                away_odds = value['away_odds']
                under_odds = value['under_odds']
                league_avg = value['league_avg']
                game_round = ""
                league_lg_76 = ""
                league_lg_86 = ""


                h_shots = ""
                h_shots_on_target = ""
                h_attacks = ""
                h_dangerous_attacks = ""
                h_a_to_da_ratio = ""

                a_shots = ""
                a_shots_on_target = ""
                a_attacks = ""
                a_dangerous_attacks = ""
                a_a_to_da_ratio = ""

                h_2H_shots = ""
                h_2H_shots_on_target = ""
                h_2H_attacks = ""
                h_2H_dangerous_attacks = ""
                h_2H_a_to_da_ratio = ""

                a_2H_shots = ""
                a_2H_shots_on_target = ""
                a_2H_attacks = ""
                a_2H_dangerous_attacks = ""
                a_2H_a_to_da_ratio = ""

                ht_stats = value['stats']['HT']
                stats = value['stats']['76']

                try:
                    h_shots = int(stats['Shots'][0])
                    h_shots_on_target = int(stats['Shots On Goal'][0])
                    h_attacks = int(stats['Attack'][0])
                    h_dangerous_attacks = int(stats['Dangerous attack'][0])
                    h_a_to_da_ratio = (h_dangerous_attacks/h_attacks) * 100

                    a_shots = int(stats['Shots'][1])
                    a_shots_on_target = int(stats['Shots On Goal'][1])
                    a_attacks = int(stats['Attack'][1])
                    a_dangerous_attacks = int(stats['Dangerous attack'][1])
                    a_a_to_da_ratio = (a_dangerous_attacks/a_attacks) * 100

                    h_2H_shots = int(stats['Shots'][0]) - int(ht_stats['Shots'][0])
                    h_2H_shots_on_target = int(stats['Shots On Goal'][0]) - int(ht_stats['Shots On Goal'][0])
                    h_2H_attacks = int(stats['Attack'][0]) - int(ht_stats['Attack'][0])
                    h_2H_dangerous_attacks = int(stats['Dangerous attack'][0]) - int(ht_stats['Dangerous attack'][0])
                    h_2H_a_to_da_ratio = (h_2H_dangerous_attacks/h_2H_attacks) * 100

                    a_2H_shots = int(stats['Shots'][1]) - int(ht_stats['Shots'][1])
                    a_2H_shots_on_target = int(stats['Shots On Goal'][1]) - int(ht_stats['Shots On Goal'][1])
                    a_2H_attacks = int(stats['Attack'][1]) - int(ht_stats['Attack'][1])
                    a_2H_dangerous_attacks = int(stats['Dangerous attack'][1]) - int(ht_stats['Dangerous attack'][1])
                    a_2H_a_to_da_ratio = (a_2H_dangerous_attacks/a_2H_attacks) * 100

                except Exception as e:
                    traceback.print_exc()
                    print(e)

                try:
                    game_round = value['round']
                except Exception as e:
                    print('')

                try:
                    league_lg_76 = value['league_stats']['late_goals_76']
                    league_lg_86 = value['league_stats']['late_goals_86']

                except Exception as e:
                    print('')

                won_76 = True
                forebet_data = ""

                total_goals = 0
                second_half_goals = 0
                total_home_goals = 0
                total_away_goals = 0
                hnw = True
                anw = True
                won_86 = True

                try:

                    home_goals = value['home_goals']
                    # print(fixture)
                    for i in home_goals:
                        if i > 45 and i < 86:
                            second_half_goals += 1
                        if i > 75:
                            total_goals += 1
                        else:
                            total_home_goals += 1
                        if i > 85:
                            won_86 = False

                except Exception as e:
                    home_goals = 0
                    total_home_goals = 0

                try:
                    away_goals = value['away_goals']

                    for i in away_goals:
                        if i > 45 and i < 86:
                            second_half_goals += 1
                        if i > 75:
                            total_goals += 1
                        else:
                            total_away_goals += 1

                        if i > 85:
                            won_86 = False

                except Exception as e:
                    away_goals = 0
                    total_away_goals = 0

                try:
                    red_cards = value['red_cards']
                    for i in red_cards:
                        if i < 86:
                            total_red_cards += 1
                except Exception as e:
                    total_red_cards = 0


                if total_goals > 1:
                    won_76 = False

                if home_odds < 1.5 and total_home_goals < total_away_goals:
                    hnw = False

                if away_odds < 1.5 and total_away_goals < total_home_goals:
                    anw = False

                gd = abs(total_home_goals - total_away_goals)

                home_recent_for = value['home_recent_for']
                home_recent_against = value['home_recent_against']
                home_recent_avg = value['home_recent_avg']
                away_recent_for = value['away_recent_for']
                away_recent_against = value['away_recent_against']
                away_recent_avg = value['away_recent_avg']
                home_76_form = value['home_76_form']
                home_76_form_l5 = value['home_76_form_l5']
                away_76_form = value['away_76_form']
                away_76_form_l5 = value['away_76_form_l5']
                home_86_form = value['home_86_form']
                home_86_form_l5 = value['home_86_form_l5']
                away_86_form = value['away_86_form']
                away_86_form_l5 = value['away_86_form_l5']
                # fb_average_goals = value['forebet_data']['average_goals']
                # fb_home_pred = value['forebet_data']['home_pred']
                # fb_draw_pred = value['forebet_data']['draw_pred']
                # fb_away_pred = value['forebet_data']['away_pred']

                stats = [
                    league, fixture, date, game_round, home_odds, away_odds, under_odds, league_avg,
                    home_recent_for, home_recent_against, home_recent_avg, away_recent_for, away_recent_against,
                    away_recent_avg, league_lg_76, league_lg_86, home_76_form, home_76_form_l5, away_76_form, away_76_form_l5, home_86_form, home_86_form_l5, away_86_form, away_86_form_l5, second_half_goals,
                    total_red_cards, hnw, anw, gd, total_home_goals, total_away_goals, h_shots, h_shots_on_target, h_attacks, h_dangerous_attacks,
                    h_a_to_da_ratio, a_shots, a_shots_on_target, a_attacks, a_dangerous_attacks, a_a_to_da_ratio, h_2H_shots,h_2H_shots_on_target,
                    h_2H_attacks, h_2H_dangerous_attacks, h_2H_a_to_da_ratio, a_2H_shots, a_2H_shots_on_target, a_2H_attacks, a_2H_dangerous_attacks,
                    a_2H_a_to_da_ratio, won_76, won_86
                ]

                games.append(stats)

            except Exception as e:
                print(value['fixture'], e)

print(count)

with open('games.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        writer.writerows(games)
