"""Module for serving an API."""


import matplotlib

from flask import Flask, send_file, render_template, redirect, url_for, Markup, send_from_directory

import pandas as pd
import pathlib as ph
import csv

def serve(options):
    """Serve an API."""

    # Create a Flask application

    app = Flask(__name__,template_folder="templates", static_folder="static")

    covid_data_frame = pd.read_csv("data/jhdata/COVID-19-master/csse_covid_19_data/csse_covid_19_daily_reports/04-15-2021.csv", dtype="category", sep=",")
    urban_data_frame = pd.read_csv("data/urban_data/share-of-population-urban.csv", dtype="category", sep=",")
    countries = covid_data_frame["Country_Region"].cat.categories

    country_links = [(item.replace(" ", "")).lower() for item in countries]

    final_doc_frame = pd.read_csv("data\final_doc.csv", dtype="category", sep=",")
    cases = final_doc_frame["Confirmed"]
    deaths = final_doc_frame["Deaths"]
    population = final_doc_frame["Inhabitants"]
    cases_cap = final_doc_frame["Cases per 100 000"]
    recovered = final_doc_frame["Recovered"]


    def plot(country_name, stat_name, *data_frames):
        """Returns a graph"""
        plt.style.use("seaborn")
        fig, ax = plt.subplots()
        ax.set_title(f"{stat_name} in {country_name}", color="#484b6a", family="sans-serif", name="Helvetica", size="12", weight="bold")
        for data_frame in data_frames:
            x = []
            y = []
            country_data = data_frame.loc[(data_frame["Country/Region"] == country_name)].iloc[:,4:]
            for column in country_data.columns:
                date = dts.date2num(datetime.datetime.strptime(column,"%m/%d/%y"))
                if date not in x:
                    x.append(date)
                total = 0
                for value in country_data[column].values:
                    total += int(value)
                y.append(total)
            plt.setp(ax.get_xticklabels(), color="#484b6a", family="sans-serif", name="Helvetica", size="10")
            plt.setp(ax.get_yticklabels(), color="#484b6a", family="sans-serif", name="Helvetica", size="10")
            months = dts.MonthLocator(interval=2)
            ax.xaxis.set_major_locator(months)
            date_format = dts.DateFormatter("%d-%m-%Y")
            ax.xaxis.set_major_formatter(date_format)
            ax.plot(x,y)
            fig.autofmt_xdate()
        return fig

    
    def map_coords(map_image, country_name, data_frame):
        """Returns the map coordinates for the choosen country"""
        map_width, map_height = map_image.size
        country_data = data_frame.loc[(data_frame["Country/Region"] == country_name)]       
        country_lon = 0.0
        country_lat = 0.0
        for lon in country_data["Long"].values:
            country_lon = float(lon)
        for lat in country_data["Lat"].values:
            country_lat = float(lat)
        
        x = round((map_width / 360) * (180 + country_lon))
        y = round((map_height / 180) * (90 - country_lat))
        return x,y



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

            string = f"{country_name} has {country_cases} confirmed cases and {country_deaths} deaths. {urban_population}% of {country_name} is urbanised.\n The country has {country_cases_per_cap} cases per 100 000 inhabitants and {country_inhabitants} currently live there."
        except:
            string = f"{country_name} has {country_cases} confirmed cases and {country_deaths} deaths. Urbanization data is missing"


        return render_template("country.html",html_table=html_table,country_name=country_name,country=country,countries=countries,country_links=country_links)


    @app.route("/fig/<country>_<stat>.jpg")
    def fig(country, stat):
        """Uploads a graph to the page"""
        country_index = country_links.index(country)
        country_name = countries[country_index]
        stat_name = stat.replace("%", " ")

        if stat_name == "Confirmed and Recovered":
            fig = plot(country_name, stat_name, confirmed_data_frame, recovered_data_frame)
        elif stat_name == "Deaths":
            fig = plot(country_name, stat_name, deaths_data_frame)


            return f"{country_name} has {country_cases} confirmed cases and {country_deaths} deaths. {urban_population}% of {country_name} is urbanised. \n The country has {country_cases_per_cap} cases per 100 000 inhabitants and {country_inhabitants} currently live there"
        except:
            return print(list(country_data.to_records(index=False)))

    @app.route("/newestdata")
    def newestdata():
        """Return a table of data."""


        return render_template("country.html",country=country_name,string=string)


    @app.route("/download/<country>.csv")
    def download_data(country):
        """Uploads a csv document with data from the specified country to the page"""
        country_index_start = -1
        country_index_stop = 0
        countries = confirmed_data_frame["Country/Region"]
        for x in range(0, len(countries)):
            if country == countries[x].lower() and country_index_start == -1:
                country_index_start = x
                country_index_stop = x
            elif country == countries[x].lower():
                country_index_stop = country_index_stop + 1
        filename = country + ".csv"

        with open(filename, "w") as write_to_file:
            write_to_file.write("Confirmed")
            formated_dataframe_confirmed = confirmed_data_frame.iloc[country_index_start:country_index_stop + 1, 0:]
            write_to_file.write(formated_dataframe_confirmed.to_csv())
            write_to_file.write("\n\n\n" + "Deaths")
            formated_dataframe_deaths = deaths_data_frame.iloc[country_index_start:country_index_stop + 1, 0:]
            write_to_file.write(formated_dataframe_deaths.to_csv())
            write_to_file.write("\n\n\n" + "Recovered")
            formated_dataframe_recovered = recovered_data_frame.iloc[country_index_start:country_index_stop + 1, 0:]
            write_to_file.write(formated_dataframe_recovered.to_csv())

        path_of_file = ph.Path(__file__).parent.parent.parent.absolute()

        return send_from_directory(path_of_file, filename)



    @app.route("/data")
    def data():
        """Return a table of data."""

        file_path = "data/jhdata/COVID-19-master/csse_covid_19_data/csse_covid_19_daily_reports/04-15-2021.csv"
        with open(file_path, newline="") as f:
            data = list(csv.reader(f))

        return render_template("data.html",data=data)

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