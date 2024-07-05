import http.client
import requests
from requests.auth import HTTPBasicAuth
import argparse
import json
import sys 
import configparser

from pprint import pprint

#from lib.web_service import Web
from lib.dark import DarkFeed
from pathlib import Path

def save_key(key):
    config = configparser.ConfigParser()
    config['API'] = {'key': key}
    with open('.ini', 'w') as configfile:
        config.write(configfile)

def update_df():
    config = configparser.ConfigParser()
    config.read('.ini')
    try:
        key = config['API']['key']
    except Exception as err:
        print("Run init command first - API key was not found")
        #print(err)

    conn = http.client.HTTPSConnection("darkfeed.io")
    headers = {
        "Authorization": "Basic " + key
    }

    response = requests.get("https://api.darkfeed.io/APIFULL", headers=headers)
    if(response.status_code == 200):
        data = response.json()
        with open("data", 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Last date: {data[0].get('Date')}")
    else:
        print("It was not possible to connect to DarkFeed")


if __name__ == "__main__":
    data = []
    with open('data', 'r') as file:
        data = json.load(file)
    all_data = data

    df = DarkFeed()

    # Start with date arguments
    parser = argparse.ArgumentParser(description='Ransomware statistics - Kudos DarkFeed (darkfeed.io).')
    
    parser.add_argument('-i', '--init', type=str, dest='init', help='First step. Pass your API key')

    parser.add_argument('-u', '--update_base', action='store_true', dest='update_base', help='Update your base of data')

    parser.add_argument('-a', '--after', type=str, dest='after', help="Date started to collecting published victims. Format: YYYY-MM-DD")
    parser.add_argument('-b', '--before', type=str, dest='before', help="Date finished to collecting published victims. Format: YYYY-MM-DD")

    parser.add_argument('-c', '--country', type= str, dest='countries', help='Country filer, write how many countries do you want split by [,].\nYou could also use: latam, south_america, central_america, middle_east, north_america, europe, asia, africa or oceania')
    parser.add_argument('-lc', '--list_countries', action='store_true', dest='list_countries', help='List all possible strings for countries')

    parser.add_argument('-s', '--sectors', type= str, dest='sectors', help='Sector filter, choose the sectors of your interest. You can choose more than one split then with [,]')
    parser.add_argument('-ls', '--list_sectors', action='store_true', dest='list_sectors', help='List all possible sectors.')

    parser.add_argument('-r', '--ransomwares', type=str, dest='ransomwares', help='Ransomware filter, choose the ransomware group of your interest. You can choose more than one split then with [,]')
    parser.add_argument('-lr', '--list_ransomwares', action='store_true', dest='list_ransomwares', help='List all ransowmare groups in our base')

    parser.add_argument('-v', '--victim', type=str, dest='victim', help='Use the name or substring to search a victm.')

    parser.add_argument('-top_c', '--top_countries', type=int, dest='top_countries', help="Get the global top X countries." )
    parser.add_argument('-top_s', '--top_sectors', type=int, dest='top_sectors', help="Get the global top X sectors." )
    parser.add_argument('-top_r', '--top_ransomwares', type=int, dest='top_ransomwares', help="Get the global top X ransomwares." )

    parser.add_argument("-n", '--news', action='store_true', dest='news', help='Cyber news!')

    parser.add_argument('-g', '--start_gui', action='store_true', dest='start_gui', help='Init a web service.')
    args = parser.parse_args()

    all_flags = []
    for action in parser._option_string_actions.values():
        all_flags.extend(action.option_strings)
    
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
            save_key(args.init)
        if args.after:
            start = args.after + "T00:00:00"
            data = df.filter_after(start,data)
            if last_argument in ['-a', '--after']:
                print(data)
        if args.before:
            end = args.before + "T23:59:59"
            data = df.filter_before(end,data)
            if last_argument in ['-b', '--before']:
                print(data)
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
            if last_argument in ['-c', '--country']:
                print(data)
        if args.sectors:
            select_sectors = args.sectors
            if ',' in select_sectors:
                select_sectors = [item.lstrip() for item in args.sectors.split(',')]
            data = df.filter_sector(select_sectors, data)
            if last_argument in ['-s', '--sectors']:
                print(data)
        if args.ransomwares:
            select_ransomwares = args.ransomwares
            if ',' in select_ransomwares:
                select_ransomwares = [item.lstrip() for item in args.ransomwares.split(',')]
            data = df.filter_ransomware(select_ransomwares, data)
            if last_argument in ['-r', '--ransomwares']:
                print(data)
        if args.list_countries:
            if last_argument in ['-lc', '--list_countries']:
                print(df.get_country_list())
        if args.list_sectors:
            if last_argument in ['-ls', '--list_sectors']:
                print(df.get_sector_list())
        if args.list_ransomwares:
            if last_argument in ['-lr', '--list_ransomwares']:
                print(df.get_ransomware_list())
        if args.victim:
            if last_argument in ['-v', '--victim']:
                print(df.filter_company(args.victim, data))
        if args.top_countries:
            if last_argument in ['-top_c', '--top_countries']:
                print(df.get_top_x_countries(args.top_countries, data))
        if args.top_sectors:
            if last_argument in ['-top_s', '--top_sectors']:
                print(df.get_top_x_sectors(args.top_sectors, data))
        if args.top_ransomwares:
            if last_argument in ['-top_r', '--top_ransomwares']:
                print(df.get_top_x_ransomwares(args.top_ransomwares, data))
        if args.news:
            if last_argument in ["-n", '--news']:
                print(df.get_cyber_news(data))
        if args.start_gui:
            print('In development . . .')
            exit()
            Web(all_data)
        if args.update_base:
            update_df()