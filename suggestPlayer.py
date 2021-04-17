import requests
from bs4 import BeautifulSoup
import re
import json
import csv
import os

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))) + '\\'
csv_filename = __location__ + "Fantrax-Team-Roster-Major League Zookeepers (MLZ).csv"
daily_matchups_url = "https://baseballsavant.mlb.com/daily_matchups"

'''
filename: Fantrax CSV filename to read player names from
Reads batter names from a Fantrax roster CSV and returns them in a list
'''
def getBattersFromCsv(filename):
    batters = []

    with open(filename) as csvfile:
        roster_reader = csv.reader(csvfile)

        # skip first two lines of csv
        next(roster_reader)
        next(roster_reader)

        for row in roster_reader:
            # read csv up to the end of the batters
            if row[0] != 'Totals':
                batters.append(row[1])
            else:
                break

    return batters

'''
Requests daily matchups from baseball savant
NOTE: Each batter v pitcher matchup is a JSON object. 'matchups_json' consists of multiple JSON objects.
'''
def getMatchupsJSON():
    # get matchup data JSON from baseball savant
    daily_matchups_page = requests.get(daily_matchups_url)
    soup = BeautifulSoup(daily_matchups_page.content, 'html.parser')

    # parse out JSON data from javascript variable 'matchups_data'
    data = soup.find_all("script")[7].string # get script tag containing matchup data JSON - HARDCODED
    p = re.compile('var matchups_data = (.*?);')
    m = p.search(data)

    matchups_json = json.loads(m.groups()[0])
    return matchups_json

def writeMatchupsToCSV(matchups_json, batters):
    with open(__location__ + 'daily_matchup.csv', 'w', newline='') as csv_file:
        # get JSON key names and print to first row of CSV
        fieldnames_list = []
        for key in matchups_json[0]:
            fieldnames_list.append(key)
        
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames_list)
        writer.writeheader()
        for matchup in matchups_json:
            if matchup["player_name"] in batters:
                writer.writerow(matchup)

def main():
    batters = getBattersFromCsv(csv_filename)
    matchups_json = getMatchupsJSON()

    print("{0:<20}{1:<20}{2:<6}{3:<8}{4:<8}{5:<8}".format("Batter", "Pitcher", "PA", "xBA", "xwOBA", "P/PA"))
    for matchup in matchups_json:
        if matchup["player_name"] in batters:
                p_pa = int(matchup["total_pitches"]) / int(matchup["pa"])  # pitches per plate appearance
                print("{0:<20}{1:<20}{2:<6}{3:<8}{4:<8}{5:<8.3f}".format(matchup["player_name"], matchup["pitcher"], matchup["pa"], matchup["xba"], matchup["xwoba"], p_pa))

    writeMatchupsToCSV(matchups_json, batters)
    


if __name__ == '__main__':
    main()