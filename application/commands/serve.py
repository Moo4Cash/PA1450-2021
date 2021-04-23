"""Module for serving an API."""

from flask import Flask, send_file, render_template, redirect
import pandas as pd
import csv

def serve(options):
    """Serve an API."""

    # Create a Flask application
    app = Flask(__name__,template_folder="templates",static_folder="static")

    covid_data_frame = pd.read_csv("data/jhdata/COVID-19-master/csse_covid_19_data/csse_covid_19_daily_reports/04-15-2021.csv", dtype="category", sep=",")
    urban_data_frame = pd.read_csv("data/urban_data/share-of-population-urban.csv", dtype="category", sep=",")
    countries = covid_data_frame["Country_Region"].cat.categories
    country_links = [(item.replace(" ", "")).lower() for item in countries]

    @app.route("/")
    def index():
        """Return the index page of the website."""
        return render_template("index.html",countries=countries,country_links=country_links)

    @app.route("/<country>")
    def country(country):
        """Return a summarization of the choosen country"""
        if country == "Choose country":
            return redirect("/data")

        country_index = country_links.index(country)
        country_name = countries[country_index]
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
            string = f"{country_name} has {country_cases} confirmed cases and {country_deaths} deaths. {urban_population}% of {country_name} is urbanised.\n The country has {country_cases_per_cap} cases per 100 000 inhabitants and {country_inhabitants} currently live there."
        except:
            string = f"{country_name} has {country_cases} confirmed cases and {country_deaths} deaths. Urbanization data is missing"

        return render_template("country.html",country=country_name,string=string)

    @app.route("/data")
    def data():
        """Return a table of data."""

        file_path = "data/jhdata/COVID-19-master/csse_covid_19_data/csse_covid_19_daily_reports/04-15-2021.csv"
        with open(file_path, newline="") as f:
            data = list(csv.reader(f))

        return render_template("data.html",data=data)

    app.run(host=options.address, port=options.port, debug=True)


def create_parser(subparsers):
    """Create an argument parser for the "serve" command."""
    parser = subparsers.add_parser("serve")
    parser.set_defaults(command=serve)
    # Add optional parameters to control the server configuration
    parser.add_argument("-p", "--port", default=8080, type=int, help="The port to listen on")
    parser.add_argument("--address", default="0.0.0.0", help="The address to listen on")
