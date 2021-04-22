"""Module for serving an API."""

from flask import Flask, send_file, render_template
import pandas as pd
import csv

def serve(options):
    """Serve an API."""

    # Create a Flask application
    app = Flask(__name__,template_folder="templates")

    covid_data_frame = pd.read_csv("jhdata/COVID-19-master/csse_covid_19_data/csse_covid_19_daily_reports/04-15-2021.csv", dtype="category", sep=",")
    urban_data_frame = pd.read_csv("urban_data/share-of-population-urban.csv", dtype="category", sep=",")
    countries = covid_data_frame["Country_Region"].cat.categories
    country_links = [(item.replace(" ", "")).lower() for item in countries]

    @app.route("/")
    def index():
        """Return the index page of the website."""
        return send_file("../www/index.html")

    @app.route("/deathspercountry")
    def deathspercountry():
        """Return an page showing death data"""
        data_list = []

        for country in countries:
            country_deaths = 0
            country_data = covid_data_frame.loc[(covid_data_frame["Country_Region"] == country)]
            for value in country_data["Deaths"].values:
                country_deaths += int(value)
            data_list.append(country + " - " + str(country_deaths))
        return render_template("deathspercountry.html",data_list=data_list)

    @app.route("/choose")
    def choose():
        """Return the choice page"""
        return render_template("choose.html",countries=countries,country_links=country_links)

    @app.route("/<country>")
    def country(country):
        """Return a summarization of the choosen country"""
        country_name = countries[country_links.index(country)]
        country_data = covid_data_frame.loc[(covid_data_frame["Country_Region"] == country_name)]
        country_deaths = 0
        country_cases = 0

        try:
            urban_data = urban_data_frame.loc[(urban_data_frame["Entity"] == country_name) & ((urban_data_frame["Year"] == "2017"))]
            urban_population = float(urban_data["Urban population (% of total)"].values[0])

            return print(list(country_data.to_records(index=False))), print(list(urban_population.to_records(index=False)))
        except:
            return print(list(country_data.to_records(index=False)))

    @app.route("/newestdata")
    def newestdata():
        """Return a table of data."""

        file_path = "jhdata/COVID-19-master/csse_covid_19_data/csse_covid_19_daily_reports/04-15-2021.csv"
        with open(file_path, newline="") as f:
            data = list(csv.reader(f))

        return render_template("newestdata.html",data=data)


    @app.route("/casespercapita")
    def goodbye(name):
        """Display a list showing the cases per capita for the countries"""
        return "Goodbye, {}!".format(name)


    def arrange(contries):
        un_arranged_file = open("jhdata\COVID-19-master\csse_covid_19_data\csse_covid_19_daily_reports\04-15-2021.csv", "r")
        line_to_be_split = un_arranged_file.readline()
        current_line_list = line_to_be_split.split(',')

    app.run(host=options.address, port=options.port, debug=True)


def create_parser(subparsers):
    """Create an argument parser for the "serve" command."""
    parser = subparsers.add_parser("serve")
    parser.set_defaults(command=serve)
    # Add optional parameters to control the server configuration
    parser.add_argument("-p", "--port", default=8080, type=int, help="The port to listen on")
    parser.add_argument("--address", default="0.0.0.0", help="The address to listen on")


def daily_to_dataframe():
    """Take daily csv file and read in to list"""

    file_path = "jhdata/COVID-19-master/csse_covid_19_data/csse_covid_19_daily_reports/04-15-2021.csv"
    data = pd.read_csv(filepath)
    
    data[["Country_Region", "Deaths", "Confirmed"]]