"""Module for serving an API."""

from flask import Flask, send_file, render_template
import pandas as pd
import csv

def serve(options):
    """Serve an API."""

    # Create a Flask application
    app = Flask(__name__,template_folder="templates")

    @app.route("/")
    def index():
        """Return the index page of the website."""
        return send_file("../www/index.html")


    @app.route("/greeting/<name>")
    def greeting(name):
        """Return a greeting for the user."""
        return "Hello, {}!".format(name)


    @app.route("/deathspercountry")
    def deathspercountry():
        """Return an page showing urbanisation data"""
        
        covid_data_frame = pd.read_csv("jhdata/COVID-19-master/csse_covid_19_data/csse_covid_19_daily_reports/04-15-2021.csv", dtype="category", sep=",")
        countries = covid_data_frame["Country_Region"].cat.categories

        data_list = []

        for country in countries:
            country_deaths = 0
            country_data = covid_data_frame.loc[(covid_data_frame["Country_Region"] == country)]
            for value in country_data["Deaths"].values:
                country_deaths += int(value)
            data_list.append(country + " - " + str(country_deaths))
        return render_template("deathspercountry.html",data_list=data_list)



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
