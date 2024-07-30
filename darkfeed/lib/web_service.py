from flask import Flask, render_template
from datetime import datetime as dt
from dateutil import relativedelta as rd
from collections import defaultdict
import logging 
import webbrowser
from threading import Timer

from .keywords import keywords
from .dark import DarkFeed

app = Flask(__name__)
app.logger.setLevel(logging.ERROR)
logging.getLogger('werkzeug').setLevel(logging.ERROR)

class Web():
    def __init__(self, data:list) -> None:
        darkfeed_database = data

        if not data:
            print("There are not data to be analyzed. Check your API")
            exit()

        df = DarkFeed()

        db_ransomwares = df.get_ransomware_news(data)
        db_cti = df.get_cyber_news(data)

        ##########
        ## HOME ##
        ##########
        database_len = len(darkfeed_database)
        date_last_data = darkfeed_database[0].get('Date')
        groups_by_victims = df.count_group_name(db_ransomwares)
        sorted_dict_sorted = dict(sorted(groups_by_victims.items(), key=lambda item: item[1], reverse=True))
        total_groups = len(groups_by_victims)
        last_3_victims = db_ransomwares[-3:]

        dashboard_items = [database_len, date_last_data, total_groups]
        
        keywords['dashboard_items'] = dashboard_items
        keywords['ransomware_groups'] = sorted_dict_sorted
        keywords['last_3_victims'] = last_3_victims
        keywords['last_3_cti_news'] = db_cti[:3]
        
        ##############
        ## DASHBOARD #
        ##############
        # Global - Year #
        currentYear = dt.now().year
        currentMonth = dt.now().month
        date_y = str(currentYear) + '-01-01' + "T00:00:00"
        date_m = str(currentYear) + '-' + str(currentMonth) + '-01' + "T00:00:00"
        last_month_first_day = dt.strftime((dt.strptime(date_m, "%Y-%m-%dT%H:%M:%S") - rd.relativedelta(months=1)) - rd.relativedelta(day=1, hour=0, minute=0, second=0), "%Y-%m-%dT%H:%M:%S")
        last_month_last_day = dt.strftime((dt.strptime(last_month_first_day, "%Y-%m-%dT%H:%M:%S") + rd.relativedelta(months=1)) - rd.relativedelta(days=1, hour=23, minute=59, second=59), "%Y-%m-%dT%H:%M:%S")
        
        victims_current_year = df.filter_after(date_y, db_ransomwares)

        victims_by_month = df.count_data_per_month(victims_current_year)
        total_victms_current_year = len(victims_current_year)
        top10_global_countries = df.get_top_x_countries(10, victims_current_year)
        top10_global_ransomwares = df.get_top_x_ransomwares(10, victims_current_year)
        top10_global_sectors = df.get_top_x_sectors(10, victims_current_year)

        keywords['dash_current_year'] = currentYear
        keywords['dash_top10_global_countries_labels'] = list(top10_global_countries.keys())
        keywords['dash_top10_global_countries_values'] = list(top10_global_countries.values())
        keywords['dash_top10_global_ransomwares_labels'] = list(top10_global_ransomwares.keys())
        keywords['dash_top10_global_ransomwares_values'] = list(top10_global_ransomwares.values())
        keywords['dash_top10_global_sectors_labels'] = list(top10_global_sectors.keys())
        keywords['dash_top10_global_sectors_values'] = list(top10_global_sectors.values())
        keywords['dash_total_victms_current_year'] = total_victms_current_year

        # Global - Victims per Month
        last_year_first_day = dt.strftime((dt.strptime(date_y, "%Y-%m-%dT%H:%M:%S") - rd.relativedelta(years=1)), "%Y-%m-%dT%H:%M:%S")
        last_year_last_day = dt.strftime((dt.strptime(date_y, "%Y-%m-%dT%H:%M:%S") - rd.relativedelta(days=1)) - rd.relativedelta(hour=23, minute=59, second=59), "%Y-%m-%dT%H:%M:%S")
        victims_last_year_a = df.filter_after(last_year_first_day, db_ransomwares)
        victims_last_year = df.filter_before(last_year_last_day, victims_last_year_a)
        victims_by_month_last_year = df.count_data_per_month(victims_last_year)

        victims_by_month_this_year = {}
        victims_by_month_l_year = {}
        victims_by_month_this_year, victims_by_month_l_year = self.compare_dict_dates(victims_by_month, victims_by_month_last_year)

        keywords['dash_victims_by_month_labels'] = list(victims_by_month_this_year.keys())
        keywords['dash_victims_by_month_values'] = list(victims_by_month_this_year.values())

        keywords['dash_last_year'] = currentYear - 1
        keywords['dash_victims_by_month_last_year_labels'] = list(victims_by_month_l_year.keys())
        keywords['dash_victims_by_month_last_year_values'] = list(victims_by_month_l_year.values())

        # Global - This Month #
        victims_this_month = df.filter_after(date_m, victims_current_year)

        total_victims_this_month = len(victims_this_month)
        top10_global_this_month_countries = df.get_top_x_countries(10, victims_this_month)
        top10_global_this_month_ransomwares = df.get_top_x_ransomwares(10, victims_this_month)
        top10_global_this_month_sectors = df.get_top_x_sectors(10, victims_this_month)

        keywords['dash_total_victims_this_month'] = total_victims_this_month
        keywords['dash_top10_global_this_month_countries_labels'] = list(top10_global_this_month_countries.keys())
        keywords['dash_top10_global_this_month_countries_values'] = list(top10_global_this_month_countries.values())
        keywords['dash_top10_global_this_month_ransomwares_labels'] = list(top10_global_this_month_ransomwares.keys())
        keywords['dash_top10_global_this_month_ransomwares_values'] = list(top10_global_this_month_ransomwares.values())
        keywords['dash_top10_global_this_month_sectors_labels'] = list(top10_global_this_month_sectors.keys())
        keywords['dash_top10_global_this_month_sectors_values'] = list(top10_global_this_month_sectors.values())

        # Global - Last Month #
        victims_last_month_db = df.filter_after(last_month_first_day, victims_current_year)
        victims_last_month = df.filter_before(last_month_last_day, victims_last_month_db)

        total_victims_last_month = len(victims_last_month)
        top10_global_last_month_countries = df.get_top_x_countries(10, victims_last_month)
        top10_global_last_month_ransomwares = df.get_top_x_ransomwares(10, victims_last_month)
        top10_global_last_month_sectors = df.get_top_x_sectors(10, victims_last_month)

        keywords['dash_total_victims_last_month'] = total_victims_last_month
        keywords['dash_top10_global_last_month_countries_labels'] = list(top10_global_last_month_countries.keys())
        keywords['dash_top10_global_last_month_countries_values'] = list(top10_global_last_month_countries.values())
        keywords['dash_top10_global_last_month_ransomwares_labels'] = list(top10_global_last_month_ransomwares.keys())
        keywords['dash_top10_global_last_month_ransomwares_values'] = list(top10_global_last_month_ransomwares.values())
        keywords['dash_top10_global_last_month_sectors_labels'] = list(top10_global_last_month_sectors.keys())
        keywords['dash_top10_global_last_month_sectors_values'] = list(top10_global_last_month_sectors.values())

        global_growth = self.calculate_growth_percentage(total_victims_this_month, total_victims_last_month)
        keywords['dash_global_cards_values'] = [total_victms_current_year, total_victims_this_month, total_victims_last_month, global_growth]

        # Latam - Year #

        victims_latam_year = df.filter_country(df.latam, victims_current_year)
        total_latam_victims_this_year = len(victims_latam_year)
        top10_latam_countries_year = df.get_top_x_countries(10, victims_latam_year)
        top10_latam_ransomwares_year = df.get_top_x_ransomwares(10, victims_latam_year)
        top10_latam_sectors_year = df.get_top_x_sectors(10, victims_latam_year)

        keywords['dash_total_victims_latam_this_year'] = total_latam_victims_this_year
        keywords['dash_top10_latam_countries_year_labels'] = list(top10_latam_countries_year.keys())
        keywords['dash_top10_latam_countries_year_values'] = list(top10_latam_countries_year.values())
        keywords['dash_top10_latam_ransomwares_year_labels'] = list(top10_latam_ransomwares_year.keys())
        keywords['dash_top10_latam_ransomwares_year_values'] = list(top10_latam_ransomwares_year.values())
        keywords['dash_top10_latam_sectors_year_labels'] = list(top10_latam_sectors_year.keys())
        keywords['dash_top10_latam_sectors_year_values'] = list(top10_latam_sectors_year.values())

        # Latam - Victims By Month
        victims_by_month_latam_year = df.count_data_per_month(victims_latam_year)

        keywords['dash_victims_by_month_latam_year_labels'] = list(victims_by_month_latam_year.keys())[::-1]
        keywords['dash_victims_by_month_latam_year_values'] = list(victims_by_month_latam_year.values())[::-1]

        # Latam - This Month #

        victims_latam_this_month = df.filter_country(df.latam, victims_this_month)
        victims_latam_last_month = df.filter_country(df.latam, victims_last_month)
        total_latam_victims_last_month = len(victims_latam_last_month)
        total_latam_victims_this_month = len(victims_latam_this_month)
        top10_latam_this_month_countries = df.get_top_x_countries(10, victims_latam_this_month)
        top10_latam_this_month_ransomwares = df.get_top_x_ransomwares(10, victims_latam_this_month)
        top10_latam_this_month_sectors = df.get_top_x_sectors(10, victims_latam_this_month)
        
        dash_latam_monthly_growth = self.calculate_growth_percentage(total_latam_victims_last_month, total_latam_victims_last_month)

        keywords['dash_total_latam_victims_last_month'] = total_latam_victims_last_month
        keywords['dash_total_latam_victims_this_month'] = total_latam_victims_this_month
        keywords['dash_latam_monthly_growth'] = dash_latam_monthly_growth
        keywords['dash_top10_latam_this_month_countries_labels'] = list(top10_latam_this_month_countries.keys())
        keywords['dash_top10_latam_this_month_countries_values'] = list(top10_latam_this_month_countries.values())
        keywords['dash_top10_latam_this_month_ransomwares_labels'] = list(top10_latam_this_month_ransomwares.keys())
        keywords['dash_top10_latam_this_month_ransomwares_values'] = list(top10_latam_this_month_ransomwares.values())
        keywords['dash_top10_latam_this_month_sectors_labels'] = list(top10_latam_this_month_sectors.keys())
        keywords['dash_top10_latam_this_month_sectors_values'] = list(top10_latam_this_month_sectors.values())

        # South America - Year
        victims_south_america_year = df.filter_country(df.south_america, victims_current_year)

        total_south_america_victims_this_year= len(victims_south_america_year)
        top10_south_america_countries_year = df.get_top_x_countries(10, victims_south_america_year)
        top10_south_america_ransomwares_year = df.get_top_x_ransomwares(10, victims_south_america_year)
        top10_south_america_sectors_year = df.get_top_x_sectors(10, victims_south_america_year)

        keywords['dash_total_victims_south_america_this_year'] = total_south_america_victims_this_year
        keywords['dash_top10_south_america_countries_year_labels'] = list(top10_south_america_countries_year.keys())
        keywords['dash_top10_south_america_countries_year_values'] = list(top10_south_america_countries_year.values())
        keywords['dash_top10_south_america_ransomwares_year_labels'] = list(top10_south_america_ransomwares_year.keys())
        keywords['dash_top10_south_america_ransomwares_year_values'] = list(top10_south_america_ransomwares_year.values())
        keywords['dash_top10_south_america_sectors_year_labels'] = list(top10_south_america_sectors_year.keys())
        keywords['dash_top10_south_america_sectors_year_values'] = list(top10_south_america_sectors_year.values())

        # South America - Victims By Month
        victims_by_month_south_america_year = df.count_data_per_month(victims_south_america_year)

        keywords['dash_victims_by_month_south_america_year_labels'] = list(victims_by_month_south_america_year.keys())[::-1]
        keywords['dash_victims_by_month_south_america_year_values'] = list(victims_by_month_south_america_year.values())[::-1]

        # South America - Month
        victims_south_america_this_month = df.filter_country(df.south_america, victims_this_month)
        victims_south_america_last_month = df.filter_country(df.south_america, victims_last_month)

        total_south_america_victims_last_month = len(victims_south_america_last_month)
        total_south_america_victims_this_month = len(victims_south_america_this_month)
        top10_south_america_this_month_countries = df.get_top_x_countries(10, victims_south_america_this_month)
        top10_south_america_this_month_ransomwares = df.get_top_x_ransomwares(10, victims_south_america_this_month)
        top10_south_america_this_month_sectors = df.get_top_x_sectors(10, victims_south_america_this_month)

        south_america_victims_montly_growth = self.calculate_growth_percentage(total_south_america_victims_this_month, total_south_america_victims_last_month)

        keywords['dash_total_south_america_victims_this_month'] = total_south_america_victims_this_month
        keywords['dash_total_south_america_victims_last_month'] = total_south_america_victims_last_month
        keywords['dash_south_america_victims_montly_growth'] = south_america_victims_montly_growth
        keywords['dash_top10_south_america_this_month_countries_labels'] = list(top10_south_america_this_month_countries.keys())
        keywords['dash_top10_south_america_this_month_countries_values'] = list(top10_south_america_this_month_countries.values())
        keywords['dash_top10_south_america_this_month_ransomwares_labels'] = list(top10_south_america_this_month_ransomwares.keys())
        keywords['dash_top10_south_america_this_month_ransomwares_values'] = list(top10_south_america_this_month_ransomwares.values())
        keywords['dash_top10_south_america_this_month_sectors_labels'] = list(top10_south_america_this_month_sectors.keys())
        keywords['dash_top10_south_america_this_month_sectors_values'] = list(top10_south_america_this_month_sectors.values())


        # Africa - Year
        victims_africa_year = df.filter_country(df.africa, victims_current_year)

        total_africa_victims_this_year = len(victims_africa_year)
        top10_africa_countries_year = df.get_top_x_countries(10, victims_africa_year)
        top10_africa_ransomwares_year = df.get_top_x_ransomwares(10, victims_africa_year)
        top10_africa_sectors_year = df.get_top_x_sectors(10, victims_africa_year)

        keywords['dash_total_victims_africa_this_year'] = total_africa_victims_this_year
        keywords['dash_top10_africa_countries_year_labels'] = list(top10_africa_countries_year.keys())
        keywords['dash_top10_africa_countries_year_values'] = list(top10_africa_countries_year.values())
        keywords['dash_top10_africa_ransomwares_year_labels'] = list(top10_africa_ransomwares_year.keys())
        keywords['dash_top10_africa_ransomwares_year_values'] = list(top10_africa_ransomwares_year.values())
        keywords['dash_top10_africa_sectors_year_labels'] = list(top10_africa_sectors_year.keys())
        keywords['dash_top10_africa_sectors_year_values'] = list(top10_africa_sectors_year.values())

        # Africa - Victims By Month
        victims_by_africa_latam_year = df.count_data_per_month(victims_africa_year)

        keywords['dash_victims_by_month_africa_year_labels'] = list(victims_by_africa_latam_year.keys())[::-1]
        keywords['dash_victims_by_month_africa_year_values'] = list(victims_by_africa_latam_year.values())[::-1]

        # Africa - Month
        victims_africa_this_month = df.filter_country(df.africa, victims_this_month)
        victims_africa_last_month = df.filter_country(df.africa, victims_last_month)

        total_africa_victims_this_month = len(victims_africa_this_month)
        total_africa_victims_last_month = len(victims_africa_last_month)
        top10_africa_this_month_countries = df.get_top_x_countries(10, victims_africa_this_month)
        top10_africa_this_month_ransomwares = df.get_top_x_ransomwares(10, victims_africa_this_month)
        top10_africa_this_month_sectors = df.get_top_x_sectors(10, victims_africa_this_month)

        africa_victims_monthly_growth = self.calculate_growth_percentage(total_africa_victims_this_month, total_africa_victims_last_month)

        keywords['dash_total_africa_victims_this_month'] = total_africa_victims_this_month
        keywords['dash_total_africa_victims_last_month'] = total_africa_victims_last_month
        keywords['dash_africa_victims_monthly_growth'] = africa_victims_monthly_growth
        keywords['dash_top10_africa_this_month_countries_labels'] = list(top10_africa_this_month_countries.keys())
        keywords['dash_top10_africa_this_month_countries_values'] = list(top10_africa_this_month_countries.values())
        keywords['dash_top10_africa_this_month_ransomwares_labels'] = list(top10_africa_this_month_ransomwares.keys())
        keywords['dash_top10_africa_this_month_ransomwares_values'] = list(top10_africa_this_month_ransomwares.values())
        keywords['dash_top10_africa_this_month_sectors_labels'] = list(top10_africa_this_month_sectors.keys())
        keywords['dash_top10_africa_this_month_sectors_values'] = list(top10_africa_this_month_sectors.values())

        # Asia - Year
        victims_asia_year = df.filter_country(df.asia, victims_current_year)

        total_asia_victims_this_year = len(victims_asia_year)
        top10_asia_countries_year = df.get_top_x_countries(10, victims_asia_year)
        top10_asia_ransomwares_year = df.get_top_x_ransomwares(10, victims_asia_year)
        top10_asia_sectors_year = df.get_top_x_sectors(10, victims_asia_year)

        keywords['dash_total_victims_asia_this_year'] = total_asia_victims_this_year
        keywords['dash_top10_asia_countries_year_labels'] = list(top10_asia_countries_year.keys())
        keywords['dash_top10_asia_countries_year_values'] = list(top10_asia_countries_year.values())
        keywords['dash_top10_asia_ransomwares_year_labels'] = list(top10_asia_ransomwares_year.keys())
        keywords['dash_top10_asia_ransomwares_year_values'] = list(top10_asia_ransomwares_year.values())
        keywords['dash_top10_asia_sectors_year_labels'] = list(top10_asia_sectors_year.keys())
        keywords['dash_top10_asia_sectors_year_values'] = list(top10_asia_sectors_year.values())

        # Asia - Victims By Month
        victims_by_asia_year = df.count_data_per_month(victims_asia_year)

        keywords['dash_victims_by_month_asia_year_labels'] = list(victims_by_asia_year.keys())[::-1]
        keywords['dash_victims_by_month_asia_year_values'] = list(victims_by_asia_year.values())[::-1]

        # Asia - Month
        victims_asia_this_month = df.filter_country(df.asia, victims_this_month)
        victims_asia_last_month = df.filter_country(df.asia, victims_last_month)

        total_asia_victims_this_month = len(victims_asia_this_month)
        total_asia_victims_last_month = len(victims_asia_last_month)
        top10_asia_this_month_countries = df.get_top_x_countries(10, victims_asia_this_month)
        top10_asia_this_month_ransomwares = df.get_top_x_ransomwares(10, victims_asia_this_month)
        top10_asia_this_month_sectors = df.get_top_x_sectors(10, victims_asia_this_month)

        asia_victims_monthly_growth = self.calculate_growth_percentage(total_asia_victims_this_month, total_asia_victims_last_month)

        keywords['dash_total_asia_victims_this_month'] = total_asia_victims_this_month
        keywords['dash_total_asia_victims_last_month'] = total_asia_victims_last_month
        keywords['dash_asia_victims_monthly_growth'] = asia_victims_monthly_growth
        keywords['dash_top10_asia_this_month_countries_labels'] = list(top10_asia_this_month_countries.keys())
        keywords['dash_top10_asia_this_month_countries_values'] = list(top10_asia_this_month_countries.values())
        keywords['dash_top10_asia_this_month_ransomwares_labels'] = list(top10_asia_this_month_ransomwares.keys())
        keywords['dash_top10_asia_this_month_ransomwares_values'] = list(top10_asia_this_month_ransomwares.values())
        keywords['dash_top10_asia_this_month_sectors_labels'] = list(top10_asia_this_month_sectors.keys())
        keywords['dash_top10_asia_this_month_sectors_values'] = list(top10_asia_this_month_sectors.values())

        # Central America - Year
        victims_central_america_year = df.filter_country(df.central_america, victims_current_year)

        total_central_america_victims_this_year = len(victims_central_america_year)
        top10_central_america_countries_year = df.get_top_x_countries(10, victims_central_america_year)
        top10_central_america_ransomwares_year = df.get_top_x_ransomwares(10, victims_central_america_year)
        top10_central_america_sectors_year = df.get_top_x_sectors(10, victims_central_america_year)

        keywords['dash_total_victims_central_america_this_year'] = total_central_america_victims_this_year
        keywords['dash_top10_central_america_countries_year_labels'] = list(top10_central_america_countries_year.keys())
        keywords['dash_top10_central_america_countries_year_values'] = list(top10_central_america_countries_year.values())
        keywords['dash_top10_central_america_ransomwares_year_labels'] = list(top10_central_america_ransomwares_year.keys())
        keywords['dash_top10_central_america_ransomwares_year_values'] = list(top10_central_america_ransomwares_year.values())
        keywords['dash_top10_central_america_sectors_year_labels'] = list(top10_central_america_sectors_year.keys())
        keywords['dash_top10_central_america_sectors_year_values'] = list(top10_central_america_sectors_year.values())

        # Central America - Victims By Month
        victims_by_central_america_year = df.count_data_per_month(victims_central_america_year)

        keywords['dash_victims_by_month_central_america_year_labels'] = list(victims_by_central_america_year.keys())[::-1]
        keywords['dash_victims_by_month_central_america_year_values'] = list(victims_by_central_america_year.values())[::-1]


        # Central America - Month
        victims_central_america_this_month = df.filter_country(df.central_america, victims_this_month)
        victims_central_america_last_month = df.filter_country(df.central_america, victims_last_month)

        total_central_america_victims_this_month = len(victims_central_america_this_month)
        total_central_america_victims_last_month = len(victims_central_america_last_month)
        top10_central_america_this_month_countries = df.get_top_x_countries(10, victims_central_america_this_month)
        top10_central_america_this_month_ransomwares = df.get_top_x_ransomwares(10, victims_central_america_this_month)
        top10_central_america_this_month_sectors = df.get_top_x_sectors(10, victims_central_america_this_month)

        central_america_victims_monthly_growth = self.calculate_growth_percentage(total_central_america_victims_this_month, total_central_america_victims_last_month)

        keywords['dash_total_central_america_victims_this_month'] = total_central_america_victims_this_month
        keywords['dash_total_central_america_victims_last_month'] = total_central_america_victims_last_month
        keywords['dash_central_america_victims_monthly_growth'] = central_america_victims_monthly_growth
        keywords['dash_top10_central_america_this_month_countries_labels'] = list(top10_central_america_this_month_countries.keys())
        keywords['dash_top10_central_america_this_month_countries_values'] = list(top10_central_america_this_month_countries.values())
        keywords['dash_top10_central_america_this_month_ransomwares_labels'] = list(top10_central_america_this_month_ransomwares.keys())
        keywords['dash_top10_central_america_this_month_ransomwares_values'] = list(top10_central_america_this_month_ransomwares.values())
        keywords['dash_top10_central_america_this_month_sectors_labels'] = list(top10_central_america_this_month_sectors.keys())
        keywords['dash_top10_central_america_this_month_sectors_values'] = list(top10_central_america_this_month_sectors.values())


        # Europe - Year
        victims_europe_year = df.filter_country(df.europe, victims_current_year)

        total_europe_victims_this_year = len(victims_europe_year)
        top10_europe_countries_year = df.get_top_x_countries(10, victims_europe_year)
        top10_europe_ransomwares_year = df.get_top_x_ransomwares(10, victims_europe_year)
        top10_europe_sectors_year = df.get_top_x_sectors(10, victims_europe_year)

        keywords['dash_total_victims_europe_this_year'] = total_europe_victims_this_year
        keywords['dash_top10_europe_countries_year_labels'] = list(top10_europe_countries_year.keys())
        keywords['dash_top10_europe_countries_year_values'] = list(top10_europe_countries_year.values())
        keywords['dash_top10_europe_ransomwares_year_labels'] = list(top10_europe_ransomwares_year.keys())
        keywords['dash_top10_europe_ransomwares_year_values'] = list(top10_europe_ransomwares_year.values())
        keywords['dash_top10_europe_sectors_year_labels'] = list(top10_europe_sectors_year.keys())
        keywords['dash_top10_europe_sectors_year_values'] = list(top10_europe_sectors_year.values())

        # Europe - Victims By Month
        victims_by_europe_year = df.count_data_per_month(victims_europe_year)

        keywords['dash_victims_by_month_europe_year_labels'] = list(victims_by_europe_year.keys())[::-1]
        keywords['dash_victims_by_month_europe_year_values'] = list(victims_by_europe_year.values())[::-1]


        # Europe - Month
        victims_europe_this_month = df.filter_country(df.europe, victims_this_month)
        victims_europe_last_month = df.filter_country(df.europe, victims_last_month)

        total_europe_victims_this_month = len(victims_europe_this_month)
        total_europe_victims_last_month = len(victims_europe_last_month)
        top10_europe_this_month_countries = df.get_top_x_countries(10, victims_europe_this_month)
        top10_europe_this_month_ransomwares = df.get_top_x_ransomwares(10, victims_europe_this_month)
        top10_europe_this_month_sectors = df.get_top_x_sectors(10, victims_europe_this_month)

        europe_victims_monthly_growth = self.calculate_growth_percentage(total_europe_victims_this_month, total_europe_victims_last_month)

        keywords['dash_total_europe_victims_this_month'] = total_europe_victims_this_month
        keywords['dash_total_europe_victims_last_month'] = total_europe_victims_last_month
        keywords['dash_europe_victims_monthly_growth'] = europe_victims_monthly_growth
        keywords['dash_top10_europe_this_month_countries_labels'] = list(top10_europe_this_month_countries.keys())
        keywords['dash_top10_europe_this_month_countries_values'] = list(top10_europe_this_month_countries.values())
        keywords['dash_top10_europe_this_month_ransomwares_labels'] = list(top10_europe_this_month_ransomwares.keys())
        keywords['dash_top10_europe_this_month_ransomwares_values'] = list(top10_europe_this_month_ransomwares.values())
        keywords['dash_top10_europe_this_month_sectors_labels'] = list(top10_europe_this_month_sectors.keys())
        keywords['dash_top10_europe_this_month_sectors_values'] = list(top10_europe_this_month_sectors.values())

        # North America - Year
        victims_north_america_year = df.filter_country(df.north_america, victims_current_year)

        total_north_america_victims_this_year = len(victims_north_america_year)
        top10_north_america_countries_year = df.get_top_x_countries(10, victims_north_america_year)
        top10_north_america_ransomwares_year = df.get_top_x_ransomwares(10, victims_north_america_year)
        top10_north_america_sectors_year = df.get_top_x_sectors(10, victims_north_america_year)

        keywords['dash_total_victims_north_america_this_year'] = total_north_america_victims_this_year
        keywords['dash_top10_north_america_countries_year_labels'] = list(top10_north_america_countries_year.keys())
        keywords['dash_top10_north_america_countries_year_values'] = list(top10_north_america_countries_year.values())
        keywords['dash_top10_north_america_ransomwares_year_labels'] = list(top10_north_america_ransomwares_year.keys())
        keywords['dash_top10_north_america_ransomwares_year_values'] = list(top10_north_america_ransomwares_year.values())
        keywords['dash_top10_north_america_sectors_year_labels'] = list(top10_north_america_sectors_year.keys())
        keywords['dash_top10_north_america_sectors_year_values'] = list(top10_north_america_sectors_year.values())

        # North America - Victims By Month
        victims_by_north_america_year = df.count_data_per_month(victims_north_america_year)

        keywords['dash_victims_by_month_north_america_year_labels'] = list(victims_by_north_america_year.keys())[::-1]
        keywords['dash_victims_by_month_north_america_year_values'] = list(victims_by_north_america_year.values())[::-1]


        # North America - Month
        victims_north_america_this_month = df.filter_country(df.north_america, victims_this_month)
        victims_north_america_last_month = df.filter_country(df.north_america, victims_last_month)

        total_north_america_victims_this_month = len(victims_north_america_this_month)
        total_north_america_victims_last_month = len(victims_north_america_last_month)
        top10_north_america_this_month_countries = df.get_top_x_countries(10, victims_north_america_this_month)
        top10_north_america_this_month_ransomwares = df.get_top_x_ransomwares(10, victims_north_america_this_month)
        top10_north_america_this_month_sectors = df.get_top_x_sectors(10, victims_north_america_this_month)

        north_america_victims_monthly_growth = self.calculate_growth_percentage(total_north_america_victims_this_month, total_north_america_victims_last_month)

        keywords['dash_total_north_america_victims_this_month'] = total_north_america_victims_this_month
        keywords['dash_total_north_america_victims_last_month'] = total_north_america_victims_last_month
        keywords['dash_north_america_victims_monthly_growth'] = north_america_victims_monthly_growth
        keywords['dash_top10_north_america_this_month_countries_labels'] = list(top10_north_america_this_month_countries.keys())
        keywords['dash_top10_north_america_this_month_countries_values'] = list(top10_north_america_this_month_countries.values())
        keywords['dash_top10_north_america_this_month_ransomwares_labels'] = list(top10_north_america_this_month_ransomwares.keys())
        keywords['dash_top10_north_america_this_month_ransomwares_values'] = list(top10_north_america_this_month_ransomwares.values())
        keywords['dash_top10_north_america_this_month_sectors_labels'] = list(top10_north_america_this_month_sectors.keys())
        keywords['dash_top10_north_america_this_month_sectors_values'] = list(top10_north_america_this_month_sectors.values())


        # Oceania - Year
        victims_oceania_year = df.filter_country(df.oceania, victims_current_year)

        total_oceania_victims_this_year = len(victims_oceania_year)
        top10_oceania_countries_year = df.get_top_x_countries(10, victims_oceania_year)
        top10_oceania_ransomwares_year = df.get_top_x_ransomwares(10, victims_oceania_year)
        top10_oceania_sectors_year = df.get_top_x_sectors(10, victims_oceania_year)

        keywords['dash_total_victims_oceania_this_year'] = total_oceania_victims_this_year
        keywords['dash_top10_oceania_countries_year_labels'] = list(top10_oceania_countries_year.keys())
        keywords['dash_top10_oceania_countries_year_values'] = list(top10_oceania_countries_year.values())
        keywords['dash_top10_oceania_ransomwares_year_labels'] = list(top10_oceania_ransomwares_year.keys())
        keywords['dash_top10_oceania_ransomwares_year_values'] = list(top10_oceania_ransomwares_year.values())
        keywords['dash_top10_oceania_sectors_year_labels'] = list(top10_oceania_sectors_year.keys())
        keywords['dash_top10_oceania_sectors_year_values'] = list(top10_oceania_sectors_year.values())

        # Oceania - Victims By Month
        victims_by_oceania_year = df.count_data_per_month(victims_oceania_year)

        keywords['dash_victims_by_month_oceania_year_labels'] = list(victims_by_oceania_year.keys())[::-1]
        keywords['dash_victims_by_month_oceania_year_values'] = list(victims_by_oceania_year.values())[::-1]

        
        # Oceania - Month
        victims_oceania_this_month = df.filter_country(df.oceania, victims_this_month)
        victims_oceania_last_month = df.filter_country(df.oceania, victims_last_month)

        total_oceania_victims_this_month = len(victims_oceania_this_month)
        total_oceania_victims_last_month = len(victims_oceania_last_month)
        top10_oceania_this_month_countries = df.get_top_x_countries(10, victims_oceania_this_month)
        top10_oceania_this_month_ransomwares = df.get_top_x_ransomwares(10, victims_oceania_this_month)
        top10_oceania_this_month_sectors = df.get_top_x_sectors(10, victims_oceania_this_month)

        oceania_victims_monthly_growth = self.calculate_growth_percentage(total_oceania_victims_this_month, total_oceania_victims_last_month)

        keywords['dash_total_oceania_victims_this_month'] = total_oceania_victims_this_month
        keywords['dash_total_oceania_victims_last_month'] = total_oceania_victims_last_month
        keywords['dash_oceania_victims_monthly_growth'] = oceania_victims_monthly_growth
        keywords['dash_top10_oceania_this_month_countries_labels'] = list(top10_oceania_this_month_countries.keys())
        keywords['dash_top10_oceania_this_month_countries_values'] = list(top10_oceania_this_month_countries.values())
        keywords['dash_top10_oceania_this_month_ransomwares_labels'] = list(top10_oceania_this_month_ransomwares.keys())
        keywords['dash_top10_oceania_this_month_ransomwares_values'] = list(top10_oceania_this_month_ransomwares.values())
        keywords['dash_top10_oceania_this_month_sectors_labels'] = list(top10_oceania_this_month_sectors.keys())
        keywords['dash_top10_oceania_this_month_sectors_values'] = list(top10_oceania_this_month_sectors.values())

        ############
        ## Sector ##
        ############

        # Manufacturing - Year
        victims_manufacturing_year = df.filter_sector(df.sector_manufacturing, victims_current_year)

        total_manufacturing_victims_this_year = len(victims_manufacturing_year)
        top10_manufacturing_countries_year = df.get_top_x_countries(10, victims_manufacturing_year)
        top10_manufacturing_ransomwares_year = df.get_top_x_ransomwares(10, victims_manufacturing_year)

        keywords['dash_total_victims_manufacturing_this_year'] = total_manufacturing_victims_this_year
        keywords['dash_top10_manufacturing_countries_year_labels'] = list(top10_manufacturing_countries_year.keys())
        keywords['dash_top10_manufacturing_countries_year_values'] = list(top10_manufacturing_countries_year.values())
        keywords['dash_top10_manufacturing_ransomwares_year_labels'] = list(top10_manufacturing_ransomwares_year.keys())
        keywords['dash_top10_manufacturing_ransomwares_year_values'] = list(top10_manufacturing_ransomwares_year.values())

        # Manufacturing - Victims By Month
        victims_by_manufacturing_year = df.count_data_per_month(victims_manufacturing_year)

        keywords['dash_victims_by_month_manufacturing_year_labels'] = list(victims_by_manufacturing_year.keys())[::-1]
        keywords['dash_victims_by_month_manufacturing_year_values'] = list(victims_by_manufacturing_year.values())[::-1]

        # Manufacturing - Month
        victims_manufacturing_this_month = df.filter_sector(df.sector_manufacturing, victims_this_month)
        victims_manufacturing_last_month = df.filter_sector(df.sector_manufacturing, victims_last_month)

        total_manufacturing_victims_this_month = len(victims_manufacturing_this_month)
        total_manufacturing_victims_last_month = len(victims_manufacturing_last_month)
        top10_manufacturing_last_month_countries = df.get_top_x_countries(10, victims_manufacturing_last_month)
        top10_manufacturing_last_month_ransomwares = df.get_top_x_ransomwares(10, victims_manufacturing_last_month)

        manufacturing_victims_monthly_growth = self.calculate_growth_percentage(total_manufacturing_victims_this_month, total_manufacturing_victims_last_month)

        keywords['dash_total_manufacturing_victims_this_month'] = total_manufacturing_victims_this_month
        keywords['dash_total_manufacturing_victims_last_month'] = total_manufacturing_victims_last_month
        keywords['dash_manufacturing_victims_monthly_growth'] = manufacturing_victims_monthly_growth
        keywords['dash_top10_manufacturing_last_month_countries_labels'] = list(top10_manufacturing_last_month_countries.keys())
        keywords['dash_top10_manufacturing_last_month_countries_values'] = list(top10_manufacturing_last_month_countries.values())
        keywords['dash_top10_manufacturing_last_month_ransomwares_labels'] = list(top10_manufacturing_last_month_ransomwares.keys())
        keywords['dash_top10_manufacturing_last_month_ransomwares_values'] = list(top10_manufacturing_last_month_ransomwares.values())

        # Finance - Year
        victims_finance_year = df.filter_sector(df.sector_finance, victims_current_year)

        total_finance_victims_this_year = len(victims_finance_year)
        top10_finance_countries_year = df.get_top_x_countries(10, victims_finance_year)
        top10_finance_ransomwares_year = df.get_top_x_ransomwares(10, victims_finance_year)

        keywords['dash_total_victims_finance_this_year'] = total_finance_victims_this_year
        keywords['dash_top10_finance_countries_year_labels'] = list(top10_finance_countries_year.keys())
        keywords['dash_top10_finance_countries_year_values'] = list(top10_finance_countries_year.values())
        keywords['dash_top10_finance_ransomwares_year_labels'] = list(top10_finance_ransomwares_year.keys())
        keywords['dash_top10_finance_ransomwares_year_values'] = list(top10_finance_ransomwares_year.values())

        # Finance - Victims By Month
        victims_by_finance_year = df.count_data_per_month(victims_finance_year)

        keywords['dash_victims_by_month_finance_year_labels'] = list(victims_by_finance_year.keys())[::-1]
        keywords['dash_victims_by_month_finance_year_values'] = list(victims_by_finance_year.values())[::-1]

        # Finance - Month
        victims_finance_this_month = df.filter_sector(df.sector_finance, victims_this_month)
        victims_finance_last_month = df.filter_sector(df.sector_finance, victims_last_month)

        total_finance_victims_this_month = len(victims_finance_this_month)
        total_finance_victims_last_month = len(victims_finance_last_month)
        top10_finance_last_month_countries = df.get_top_x_countries(10, victims_finance_last_month)
        top10_finance_last_month_ransomwares = df.get_top_x_ransomwares(10, victims_finance_last_month)

        finance_victims_monthly_growth = self.calculate_growth_percentage(total_finance_victims_last_month, total_finance_victims_last_month)

        keywords['dash_total_finance_victims_this_month'] = total_finance_victims_this_month
        keywords['dash_total_finance_victims_last_month'] = total_finance_victims_last_month
        keywords['dash_finance_victims_monthly_growth'] = finance_victims_monthly_growth
        keywords['dash_top10_finance_last_month_countries_labels'] = list(top10_finance_last_month_countries.keys())
        keywords['dash_top10_finance_last_month_countries_values'] = list(top10_finance_last_month_countries.values())
        keywords['dash_top10_finance_last_month_ransomwares_labels'] = list(top10_finance_last_month_ransomwares.keys())
        keywords['dash_top10_finance_last_month_ransomwares_values'] = list(top10_finance_last_month_ransomwares.values())

        
        # Energy - Year
        victims_energy_year = df.filter_sector(df.sector_energy, victims_current_year)

        total_energy_victims_this_year = len(victims_energy_year)
        top10_energy_countries_year = df.get_top_x_countries(10, victims_energy_year)
        top10_energy_ransomwares_year = df.get_top_x_ransomwares(10, victims_energy_year)

        keywords['dash_total_victims_energy_this_year'] = total_energy_victims_this_year
        keywords['dash_top10_energy_countries_year_labels'] = list(top10_energy_countries_year.keys())
        keywords['dash_top10_energy_countries_year_values'] = list(top10_energy_countries_year.values())
        keywords['dash_top10_energy_ransomwares_year_labels'] = list(top10_energy_ransomwares_year.keys())
        keywords['dash_top10_energy_ransomwares_year_values'] = list(top10_energy_ransomwares_year.values())

        # Energy - Victims By Month
        victims_by_energy_year = df.count_data_per_month(victims_energy_year)

        keywords['dash_victims_by_month_energy_year_labels'] = list(victims_by_energy_year.keys())[::-1]
        keywords['dash_victims_by_month_energy_year_values'] = list(victims_by_energy_year.values())[::-1]

        # Energy - Month
        victims_energy_this_month = df.filter_sector(df.sector_energy, victims_this_month)
        victims_energy_last_month = df.filter_sector(df.sector_energy, victims_last_month)

        total_energy_victims_this_month = len(victims_energy_this_month)
        total_energy_victims_last_month = len(victims_energy_last_month)
        top10_energy_last_month_countries = df.get_top_x_countries(10, victims_energy_last_month)
        top10_energy_last_month_ransomwares = df.get_top_x_ransomwares(10, victims_energy_last_month)

        energy_victims_monthly_growth = self.calculate_growth_percentage(total_energy_victims_this_month, total_energy_victims_last_month)

        keywords['dash_total_energy_victims_this_month'] = total_energy_victims_this_month
        keywords['dash_total_energy_victims_last_month'] = total_energy_victims_last_month
        keywords['dash_energy_victims_monthly_growth'] = energy_victims_monthly_growth
        keywords['dash_top10_energy_last_month_countries_labels'] = list(top10_energy_last_month_countries.keys())
        keywords['dash_top10_energy_last_month_countries_values'] = list(top10_energy_last_month_countries.values())
        keywords['dash_top10_energy_last_month_ransomwares_labels'] = list(top10_energy_last_month_ransomwares.keys())
        keywords['dash_top10_energy_last_month_ransomwares_values'] = list(top10_energy_last_month_ransomwares.values())


        # Health - Year
        victims_health_year = df.filter_sector(df.sector_health, victims_current_year)

        total_health_victims_this_year = len(victims_health_year)
        top10_health_countries_year = df.get_top_x_countries(10, victims_health_year)
        top10_health_ransomwares_year = df.get_top_x_ransomwares(10, victims_health_year)

        keywords['dash_total_victims_health_this_year'] = total_health_victims_this_year
        keywords['dash_top10_health_countries_year_labels'] = list(top10_health_countries_year.keys())
        keywords['dash_top10_health_countries_year_values'] = list(top10_health_countries_year.values())
        keywords['dash_top10_health_ransomwares_year_labels'] = list(top10_health_ransomwares_year.keys())
        keywords['dash_top10_health_ransomwares_year_values'] = list(top10_health_ransomwares_year.values())

        # Health - Victims By Month
        victims_by_health_year = df.count_data_per_month(victims_health_year)

        keywords['dash_victims_by_month_health_year_labels'] = list(victims_by_health_year.keys())[::-1]
        keywords['dash_victims_by_month_health_year_values'] = list(victims_by_health_year.values())[::-1]


        # Health - Last Month
        victims_health_this_month = df.filter_sector(df.sector_health, victims_this_month)
        victims_health_last_month = df.filter_sector(df.sector_health, victims_last_month)

        total_health_victims_last_month = len(victims_health_last_month)
        total_health_victims_this_month = len(victims_health_this_month)
        top10_health_last_month_countries = df.get_top_x_countries(10, victims_health_last_month)
        top10_health_last_month_ransomwares = df.get_top_x_ransomwares(10, victims_health_last_month)

        health_victims_monthly_growth = self.calculate_growth_percentage(total_health_victims_this_month, total_health_victims_last_month)

        keywords['dash_total_health_victims_this_month'] = total_health_victims_this_month
        keywords['dash_total_health_victims_last_month'] = total_health_victims_last_month
        keywords['dash_health_victims_monthly_growth'] = health_victims_monthly_growth
        keywords['dash_top10_health_last_month_countries_labels'] = list(top10_health_last_month_countries.keys())
        keywords['dash_top10_health_last_month_countries_values'] = list(top10_health_last_month_countries.values())
        keywords['dash_top10_health_last_month_ransomwares_labels'] = list(top10_health_last_month_ransomwares.keys())
        keywords['dash_top10_health_last_month_ransomwares_values'] = list(top10_health_last_month_ransomwares.values())


        #################
        ## RANSOMWARES ##
        #################
        keywords['db_ransomwares'] = db_ransomwares

        ##############
        ## CTI NEWS ##
        ##############
        keywords['db_cti'] = db_cti
        
        Timer(1, webbrowser.open('http://127.0.0.1:5000/')).start()
        app.run(debug=False, port=5000, host="0.0.0.0")

        print("Service running at: http://127.0.0.1:5000/")

    def compare_dict_dates(self, a:dict,b:dict):
        all_keys = set(a.keys()).union(set(b.keys()))

        a_compare = defaultdict(int)
        b_compare = defaultdict(int)

        for key in all_keys:
            a_compare[key] = a.get(key, 0)
            b_compare[key] = b.get(key, 0)

        a_ord_dictionary = self.order_dictionary_by_month_keys(a_compare)
        b_ord_dictionary = self.order_dictionary_by_month_keys(b_compare)
        
        return dict(a_ord_dictionary), dict(b_ord_dictionary)
    
    def order_dictionary_by_month_keys(self, dictionary:dict) -> dict:
        sorted_keys = sorted(dictionary.keys(), key=lambda x: int(x))
        ordered_dict = {key: dictionary[key] for key in sorted_keys}
        return ordered_dict
    
    def calculate_growth_percentage(self, new_value:int, old_value:int) -> float:
        try:
            percentage = ((new_value - old_value) / abs(old_value)) * 100
            return "{:.2f}".format(percentage)
        except ZeroDivisionError:
            if old_value == 0 and new_value == 0:
                return 0.0  
            else:
                return float('inf')

    @app.route("/",)
    def home():        
        return render_template('index.html', content = keywords )

    @app.route("/dashboard")
    def dashboard():
        return render_template('dashboard.html', content = keywords)

    @app.route("/ransomwares")
    def ransomwares(): # Table
        return render_template('ransomwares.html', content = keywords)

    @app.route('/cti-news')
    def cti_news(): # Table
        return render_template('cti_news.html', content = keywords)