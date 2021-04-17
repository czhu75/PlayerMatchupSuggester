import requests
from bs4 import BeautifulSoup
import re
import json
import csv

csv_filename = "C:\Tools\PlayerMatchupSuggester\Fantrax-Team-Roster-Major League Zookeepers (MLZ).csv"
daily_matchups_url = "https://baseballsavant.mlb.com/daily_matchups"

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

def main():
    batters = getBattersFromCsv(csv_filename)
    matchups_json = getMatchupsJSON()

    for matchup in matchups_json:
        if matchup["player_name"] in batters:
            print(matchup)
    

if __name__ == '__main__':
    main()