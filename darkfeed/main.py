import http.client
import requests
from requests.auth import HTTPBasicAuth
import argparse
import json
import sys 
import configparser
import os

KEY_PATH = os.path.join(os.path.expanduser("~"), '.darkfeed.ini')

from .lib.web_service import Web
from .lib.dark import DarkFeed
from pathlib import Path

def save_key(key):
    config = configparser.ConfigParser()
    config['API'] = {'key': key}
    with open(KEY_PATH, 'w') as configfile:
        config.write(configfile)

def update_df():
    config = configparser.ConfigParser()
    try:
        config.read(KEY_PATH)
        key = config['API']['key']
    except Exception as err:
        print("Run init command first - API key was not found or is not correct")
        exit()

    conn = http.client.HTTPSConnection("darkfeed.io")
    headers = {
        "Authorization": "Basic " + key
    }

    response = requests.get("https://api.darkfeed.io/APIFULL", headers=headers)
    if(response.status_code == 200):
        data = response.json()
        with open("darkfeed.data", 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Last date: {data[0].get('Date')}")
    else:
        print("It was not possible to connect to DarkFeed")
        exit()

def get_df() -> list:
    config = configparser.ConfigParser()
    try:
        config.read(KEY_PATH)
        key = config['API']['key']
    except Exception as err:
        print("Run init command first - API key was not found or is not correct")
        exit()

    conn = http.client.HTTPSConnection("darkfeed.io")
    headers = {
        "Authorization": "Basic " + key
    }

    response = requests.get("https://api.darkfeed.io/APIFULL", headers=headers)
    if(response.status_code == 200):
        data = response.json()
        return data
    else:
        print("It was not possible to connect to DarkFeed")
        exit()

def output(data, last_data:bool=False, json_f:bool=False):
    if last_data:
        if json_f:
            print(json.dumps(data))
        else:
            print(data)

def main():
    df = DarkFeed()

    # Start with date arguments
    parser = argparse.ArgumentParser(description='Ransomware statistics - Kudos DarkFeed (darkfeed.io).')
    
    parser.add_argument('-i', '--init', action='store_true', dest='init', help="First step. Pass your API key.")

    parser.add_argument('-d', '--download_base', action='store_true', dest='download_base', help='To save/update base to a file')

    parser.add_argument('-a', '--after', type=str, dest='after', help="Date started to collecting published victims. Format: YYYY-MM-DD")
    parser.add_argument('-b', '--before', type=str, dest='before', help="Date finished to collecting published victims. Format: YYYY-MM-DD")

    parser.add_argument('-c', '--country', type= str, dest='countries', help='Country filer, write how many countries do you want split by [,].\nYou could also use: latam, south_america, central_america, north_america, europe, asia, africa or oceania')
    parser.add_argument('-lc', '--list_countries', action='store_true', dest='list_countries', help='List all possible strings for countries')

    parser.add_argument('-s', '--sectors', type= str, dest='sectors', help='Sector filter, choose the sectors of your interest. You can choose more than one split then with [,]')
    parser.add_argument('-ls', '--list_sectors', action='store_true', dest='list_sectors', help='List all possible sectors.')

    parser.add_argument('-r', '--ransomwares', type=str, dest='ransomwares', help='Ransomware filter, choose the ransomware group of your interest. You can choose more than one split then with [,]')
    parser.add_argument('-lr', '--list_ransomwares', action='store_true', dest='list_ransomwares', help='List all ransowmare groups in our base')

    parser.add_argument('-v', '--victim', type=str, dest='victim', help='Use the name or substring to search a victm.')

    parser.add_argument('-top_c', '--top_countries', type=int, dest='top_countries', help="Get the global top X countries." )
    parser.add_argument('-top_s', '--top_sectors', type=int, dest='top_sectors', help="Get the global top X sectors." )
    parser.add_argument('-top_r', '--top_ransomwares', type=int, dest='top_ransomwares', help="Get the global top X ransomwares." )

    parser.add_argument('-json', action='store_true', dest='json', help='To format your output to json')

    parser.add_argument("-count", action='store_true', dest='counter', help='To count the num of items')

    parser.add_argument("-xlsx", action='store_true', dest='xlsx', help='To convert data to spreadsheet / xlsx')

    parser.add_argument("-n", '--news', action='store_true', dest='news', help='Cyber news!')

    parser.add_argument('-g', '--start_gui', action='store_true', dest='start_gui', help='Init a web service.')
    args = parser.parse_args()

    all_flags = []
    for action in parser._option_string_actions.values():
        all_flags.extend(action.option_strings)
    all_flags = [x for x in all_flags if (x!= '--json')]
    
    last_argument = None
    if last_argument is None and len(sys.argv) > 1:
        for index in range(len(sys.argv) - 1, 0, -1):
            input_str = sys.argv[index]
            if input_str in all_flags:
                last_argument = sys.argv[index]
                break
        
    if not args:
        exit()
    else:
        if args.init:
            key = input('Enter your key:')
            save_key(key)
            print(f"Key saved")

        data = get_df()
        all_data = data

        if args.download_base:
            update_df()       
        if args.after:
            start = args.after + "T00:00:00"
            data = df.filter_after(start,data)
            output(data, last_argument in ['-a', '--after'], args.json)
        if args.before:
            end = args.before + "T23:59:59"
            data = df.filter_before(end,data)
            output(data, last_argument in ['-b', '--before'], args.json)
        if args.countries:
            select_countries = args.countries
            if ',' in select_countries:
                select_countries = [item.lstrip() for item in args.countries.split(',')]
            elif select_countries == "latam":
                select_countries = df.latam
            elif select_countries == "south_america":
                select_countries == df.south_america
            elif select_countries == "central_america":
                select_countries = df.central_america
            elif select_countries == "north_america":
                select_countries = df.north_america
            elif select_countries == "europe":
                select_countries = df.europe
            elif select_countries == "asia":
                select_countries = df.asia
            elif select_countries == "africa":
                select_countries = df.africa
            elif select_countries == "oceania":
                select_countries = df.oceania
            elif select_countries == "middle_east":
                select_countries = df.middle_east
            data = df.filter_country(select_countries, data)
            output(data, last_argument in ['-c', '--country'], args.json)
        if args.sectors:
            select_sectors = args.sectors
            if ',' in select_sectors:
                select_sectors = [item.lstrip() for item in args.sectors.split(',')]
            data = df.filter_sector(select_sectors, data)
            output(data, last_argument in ['-s', '--sectors'], args.json)
        if args.ransomwares:
            select_ransomwares = args.ransomwares
            if ',' in select_ransomwares:
                select_ransomwares = [item.lstrip() for item in args.ransomwares.split(',')]
            data = df.filter_ransomware(select_ransomwares, data)
            output(data, last_argument in ['-r', '--ransomwares'], args.json)
        if args.list_countries:
            data = df.get_country_list(data)
            output(data, last_argument in ['-lc', '--list_countries'], args.json)
        if args.list_sectors:
            data = df.get_sector_list(data)
            output(data, last_argument in ['-ls', '--list_sectors'], args.json)
        if args.list_ransomwares:
            data = df.get_ransomware_list(data)
            output(data, last_argument in ['-lr', '--list_ransomwares'], args.json)
        if args.victim:
            data = df.filter_company(args.victim, data)
            output(data, last_argument in ['-v', '--victim'], args.json)
        if args.top_countries:
            data = df.get_top_x_countries(args.top_countries, data)
            output(data, last_argument in ['-top_c', '--top_countries'], args.json)
        if args.top_sectors:
            data = df.get_top_x_sectors(args.top_sectors, data)
            output(data, last_argument in ['-top_s', '--top_sectors'], args.json)
        if args.top_ransomwares:
            data = df.get_top_x_ransomwares(args.top_ransomwares, data)
            output(data, last_argument in ['-top_r', '--top_ransomwares'], args.json)
        if args.news:
            data = df.get_cyber_news(data)
            output(data, last_argument in ["-n", '--news'], args.json)
        if args.counter:
            data = len(data)
            output(data, last_argument in ["-count"])
        if args.xlsx: 
            df.data_2_csv(data)
        if args.start_gui:
            Web(all_data)

if __name__ == "__main__":
    main()
    