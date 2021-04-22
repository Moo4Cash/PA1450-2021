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
    country_links = [item.replace(" ", "") for item in countries]
    final_doc_frame = pd.read_csv("/home/pa1450/PA1450-2021/final_doc.csv", dtype="category", sep=",")
    final_doc_countries = final_doc_frame["Country"]
    final_doc_cases_cap = final_doc_frame["CasesPer100 000"]
    final_doc_population = final_doc_frame["Inhabitants"].astype(int)

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

    @app.route("/data/<country>")
    def country(country):
        """Return a summarization of the choosen country"""
        country_index = country_links.index(country)
        country_name = countries[country_index]
        country_cases_per_cap = final_doc_cases_cap[country_index]
        country_inhabitants = final_doc_population[country_index]
        country_deaths = 0
        country_cases = 0
        country_data = covid_data_frame.loc[(covid_data_frame["Country_Region"] == country_name)]

        for value in country_data["Deaths"].values:
            country_deaths += int(value)
        for value in country_data["Confirmed"].values:
            country_cases += int(value)

        try:
            urban_data = urban_data_frame.loc[(urban_data_frame["Entity"] == country_name) & ((urban_data_frame["Year"] == "2017"))]
            urban_population = float(urban_data["Urban population (% of total)"].values[0])
            return f"{country_name} has {country_cases} confirmed cases and {country_deaths} deaths. {urban_population}% of {country_name} is urbanised. \n The country has {country_cases_per_cap} cases per 100 000 inhabitants and {country_inhabitants} currently live there"
        except:
            return f"{country_name} has {country_cases} confirmed cases and {country_deaths} deaths. Urbanization data is missing"

    @app.route("/newestdata")
    def newestdata():
        """Return a table of data."""

        file_path = "jhdata/COVID-19-master/csse_covid_19_data/csse_covid_19_daily_reports/04-15-2021.csv"
        with open(file_path, newline="") as f:
            data = list(csv.reader(f))

        return render_template("newestdata.html",data=data)

    @app.route("/newestdataus")
    def newestdataus():
        """Return a table of data."""

        file_path = "jhdata/COVID-19-master/csse_covid_19_data/csse_covid_19_daily_reports_us/04-15-2021.csv"
        with open(file_path, newline="") as f:
            data = list(csv.reader(f))

        return render_template("newestdata.html",data=data)

    @app.route("/casespercapita")
    def display_cases_per_capita():
        
        capita_data_list = []
        for x in range(0, len(final_doc_countries)):
            capita_data_list.append(str(final_doc_countries[x]) + " " + str(final_doc_cases_cap[x]))

        return render_template("casespercapita.html",capita_data_list=capita_data_list)


    app.run(host=options.address, port=options.port, debug=True)


def create_parser(subparsers):
    """Create an argument parser for the "serve" command."""
    parser = subparsers.add_parser("serve")
    parser.set_defaults(command=serve)
    # Add optional parameters to control the server configuration
    parser.add_argument("-p", "--port", default=8080, type=int, help="The port to listen on")
    parser.add_argument("--address", default="0.0.0.0", help="The address to listen on")
