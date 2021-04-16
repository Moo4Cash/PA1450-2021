"""Module for serving an API."""

from flask import Flask, send_file
import csv

def serve(options):
    """Serve an API."""

    # Create a Flask application
    app = Flask(__name__)

    @app.route("/")
    def index():
        """Return the index page of the website."""
        return send_file("../www/index.html")

    @app.route("/greeting/<name>")
    def greeting(name):
        """Return a greeting for the user."""
        return "Hello, {}!".format(name)

    @app.route("/goodbye")
    def goodbye(name):
        """Return a greeting for the user."""
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
