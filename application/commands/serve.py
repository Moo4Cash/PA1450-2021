"""Module for serving an API."""

from flask import Flask, send_file, render_template, redirect, url_for, Markup
import pandas as pd
import csv
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as dts
from io import BytesIO

def serve(options):
    """Serve an API."""

    # Create a Flask application
    app = Flask(__name__,template_folder="templates", static_folder="static")


    covid_data_frame = pd.read_csv("data/jhdata/COVID-19-master/csse_covid_19_data/csse_covid_19_daily_reports/04-15-2021.csv", dtype="category", sep=",")
    urban_data_frame = pd.read_csv("data/urban_data/share-of-population-urban.csv", dtype="category", sep=",")
    final_doc_frame = pd.read_csv("data/final_doc.csv", dtype="category", sep=",")

    countries = final_doc_frame["Country"]
    country_links = [(item.replace(" ", "")).lower() for item in countries]

    cases = final_doc_frame["Confirmed"]
    deaths = final_doc_frame["Deaths"]
    population = final_doc_frame["Inhabitants"]
    cases_cap = final_doc_frame["Cases per 100 000"]
    recovered = final_doc_frame["Recovered"]


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

        country_data = final_doc_frame.loc[(final_doc_frame["Country"] == country_name)].iloc[:,1:]
        html_code = Markup(country_data.to_html(index=False,border=0))

        try:
            urban_data = urban_data_frame.loc[(urban_data_frame["Entity"] == country_name) & ((urban_data_frame["Year"] == "2017"))]
            urban_population = float(urban_data["Urban population (% of total)"].values[0])

            string = f"{urban_population}% of {country_name} is urbanised."
        except:
            string = "Urbanization data is missing"

        return render_template("country.html",html_code=html_code,string=string,country_name=country_name,country=country,countries=countries,country_links=country_links)


    @app.route("/fig/<country>")
    def fig(country):
        """Return a graph for the choosen country."""
        country_index = country_links.index(country)
        country_name = countries[country_index]

        fig, ax = plt.subplots()
        ax.set_title(f"Deaths in {country_name}")
        x = []
        y = []
        country_data = final_doc_frame.loc[(final_doc_frame["Country"] == country_name)]
        country_deaths = country_data["Deaths"].values[0]
        date = dts.date2num(datetime.datetime.strptime("04-15-2021","%m-%d-%Y"))
        x.append(date)
        y.append(country_deaths)

        months = dts.MonthLocator(interval=2)
        ax.xaxis.set_major_locator(months)
        date_format = dts.DateFormatter("%Y %b")
        ax.xaxis.set_major_formatter(date_format)
        fig.autofmt_xdate()
        ax.plot(x, y)

        img = BytesIO()
        fig.savefig(img, format="png")
        img.seek(0)

        return send_file(img, mimetype='image/png')


    @app.route("/data")
    def data():
        """Return a table of data."""

        file_path = "data/final_doc.csv"
        with open(file_path, newline="") as f:
            data = list(csv.reader(f))

        return render_template("data.html",data=data,countries=countries,country_links=country_links)


    app.run(host=options.address, port=options.port, debug=True)


def create_parser(subparsers):
    """Create an argument parser for the "serve" command."""
    parser = subparsers.add_parser("serve")
    parser.set_defaults(command=serve)
    # Add optional parameters to control the server configuration
    parser.add_argument("-p", "--port", default=8080, type=int, help="The port to listen on")
    parser.add_argument("--address", default="0.0.0.0", help="The address to listen on")