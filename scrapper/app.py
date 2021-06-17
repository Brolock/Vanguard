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

@app.route("/scrap_url")
def scrap_url():
    if request.method == "GET":
        if "url_to_scrap" in request.values:
            url_to_scrap = request.values["url_to_scrap"] 
            try:
                return scrap_card_data(url_to_scrap)
            except:
                return "Invalid URL format provided to url_to_scrap please send a https://en.cf-vanguard.com card link"
        else:
            return "Please make a GET request at this URL with a url_to_scrap param. The form should be /scrap_url?url_to_scrap=*https://card/url* (only supports https://en.cf-vanguard.com/)"

