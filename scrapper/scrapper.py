import requests
from bs4 import BeautifulSoup
import json
from pathlib import Path

from dateutil import parser as date_parser
import re

from beautifulsoup_wrapper import SoupWrapper

VANGUARD_ROOT_URL="https://en.cf-vanguard.com"

def scrap_card_data(card_url: str):
    print(card_url)
    page = requests.get(card_url)
    soup = SoupWrapper(BeautifulSoup(page.content, "html.parser"))

    details = soup.find("div", class_="cardlist_detail")
    data = details.find("div", class_="data")
    card_data_keys = [
            "name",
            "type",
            "nation",
            "race",
            "grade",
            "power",
            "critical",
            "shield",
            "skill",
            "gift",
            "effect",
            "flavor",
            "regulation",
            "number",
            "rarity",
            "illstrator"
            ]

    card_data = {}
    for key in card_data_keys:
        card_data[key] = data.find("div", class_=key).text.strip()

    # image has a different dom
    image_url = details.find("div", class_="image").find("img")["src"].strip()
    card_data["image_url"] =  image_url
    card_data["original_url"] = card_url

    return card_data


def scrap_cards_from_expansion(cardlist_url: str, output_file: str):
    page = requests.get(cardlist_url)
    soup = SoupWrapper(BeautifulSoup(page.content, "html.parser"))

    expansion_url = re.match(r".+?(\?expansion=\d+)", cardlist_url).group() + "&page="

    page_number = 1
    cards_dict = []
    # Loop through pages of the cardlist (no need for headless navigation)
    while (page := requests.get(expansion_url + str(page_number))).ok:
        page_number += 1
        soup = SoupWrapper(BeautifulSoup(page.content, "html.parser"))
        card_list = soup.find("div", id="cardlist-container").find_all("li")

        for card in card_list:
            card_url = card.find('a')["href"]
            card_data = scrap_card_data(VANGUARD_ROOT_URL + card_url)
            cards_dict.append(card_data)

    with Path(output_file).open('w') as output_file:
        json.dump(cards_dict, output_file, indent=2)

def scrap_expansions(expansions_url: str):
    page = requests.get(expansions_url)
    soup = SoupWrapper(BeautifulSoup(page.content, "html.parser"))
    soup = soup.find("div", class_="cardlist_main")

    with Path("db/database.json").open('w') as db_file:
        expansions_per_year = soup.find_all("div", class_="expansion-year")
        for yearly_expansions in expansions_per_year:
            expansions = yearly_expansions.find_all("div", class_="product-item")

            for expansion in expansions:
                expansion_url = expansion.find('a')["href"]
                img_url = expansion.find("img")["src"].strip()

                category = expansion.find("div", class_="category").text.strip()
                title = expansion.find("div", class_="title").text.strip()
                release_date = expansion.find("div", class_="release").text.strip()
                clan = expansion.find("div", class_="clan").text.strip()

                # Remove punctuation except '-', '_', '[' and ']'
                expansion_file = re.sub(r'[^\w\s\-_\[\]]', '', title, re.UNICODE)
                expansion_file = re.sub(r'\s+', '_', expansion_file, re.UNICODE)
                expansion_file += ".json"

                expansion_data = {
                        "title": title,
                        "category": category,
                        "release_date": release_date,
                        "clan": clan,
                        "image_url": img_url,
                        "expansion_file": expansion_file
                        }
                json.dump(expansion_data, db_file)
                db_file.write('\n')

                scrap_cards_from_expansion(VANGUARD_ROOT_URL + expansion_url, "db/" + expansion_file)

if __name__ == "__main__": 
    #scrap_expansions(VANGUARD_ROOT_URL + "/cardlist")
    scrap_cards_from_expansion("https://en.cf-vanguard.com/cardlist/cardsearch/?expansion=162", "db/test.json")
