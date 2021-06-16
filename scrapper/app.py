import flask
from flask import request

app = flask.Flask(__name__, template_folder='html_templates')

from scrapper import scrap_card_data

def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)

@app.route("/")
def index():
    links = []
    for rule in app.url_map.iter_rules():
        if "GET" in rule.methods and has_no_empty_params(rule):
            url = flask.url_for(rule.endpoint, **(rule.defaults or {}))
            links.append((url, rule.rule))
    return flask.render_template("all_links.html", links=links)

@app.route("/scrap_url", methods=["GET", "POST"])
def scrap_url():
    if request.method == "POST":
        try:
            url_to_scrap = request.form["scrapped_url"] 
            return scrap_card_data(url_to_scrap)
        except KeyError:
            return "Please add a scrapped_url form to your post request"
    else:
        return "Please make a POST request at this URL with a scrapped_url card you wish to get (only supports https://en.cf-vanguard.com/)"
