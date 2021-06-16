import requests
import json
from pathlib import Path

from dateutil import parser as date_parser
import re
import argparse

from beautifulsoup_wrapper import WrappedSoup
from scrapper_logger import get_logger


# Global logger object
DB_DIR = "db"
logger = get_logger(Path(DB_DIR) / "defaultlogger.log", "default_logger")
VANGUARD_ROOT_URL="https://en.cf-vanguard.com"


def log_query(url: str, logged_dict: dict):
    keys_not_found = []
    for key, value in logged_dict.items():
        if value == "None":
            keys_not_found.append(key)

    if len(keys_not_found) > 0:
        logger.warning(f"At url: {url}\n\t{keys_not_found} Not found\n\tResulting dict: {logged_dict}")
    else:
        logger.debug(f"Parsed successfully {url}")

def clean_card_dict(card_dict: dict):
    illustrator = card_dict.pop("illstrator", None)
    card_dict["illustrator"] = illustrator
    return card_dict

def scrap_card_data(card_url: str):
    page = requests.get(card_url)
    soup = WrappedSoup(page.content, "html.parser")

    details = soup.find("div", class_="cardlist_detail")
    data = details.find("div", class_="data")
    card_dict_keys = [
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

    card_dict = {}
    for key in card_dict_keys:
        card_dict[key] = data.find("div", class_=key).text.strip()

    # image has a different dom
    image_url = details.find("div", class_="image").find("img")["src"].strip()
    card_dict["image_url"] =  image_url

    # Log and clean data
    log_query(card_url, card_dict)
    card_dict = clean_card_dict(card_dict)
    card_dict["original_url"] = card_url
    return card_dict


def scrap_cards_from_expansion(cardlist_url: str, output_file: str):
    page = requests.get(cardlist_url)
    soup = WrappedSoup(page.content, "html.parser")

    expansion_url = re.match(r".+?(\?expansion=\d+)", cardlist_url).group() + "&page="

    page_number = 1
    cards_dicts = []
    # Loop through pages of the cardlist
    while (page := requests.get(expansion_url + str(page_number))).ok:
        page_number += 1
        soup = WrappedSoup(page.content, "html.parser")
        card_list = soup.find("div", id="cardlist-container").find_all("li")

        for card in card_list:
            card_url = card.find('a')["href"]
            card_data = scrap_card_data(VANGUARD_ROOT_URL + card_url)
            cards_dicts.append(card_data)

    with Path(output_file).open('w') as output_file:
        json.dump(cards_dicts, output_file, indent=2)


def clean_expansion_dict(expansion_dict: dict):
    noisy_date = expansion_dict["release"]
    # No date was found
    if noisy_date == "None":
        return noisy_date
    date = re.findall("[\d\s\/]+|January|February|February|March|April|May|June|July|August|September|October|November|December", noisy_date)
    date = date_parser.parse(' '.join(date))
    expansion_dict["release"] = date.strftime("%m/%d/%Y")

    return expansion_dict


def scrap_expansions(expansions_url: str):
    page = requests.get(expansions_url)
    soup = WrappedSoup(page.content, "html.parser")
    soup = soup.find("div", class_="cardlist_main")

    expansion_dicts = []
    expansions_per_year = soup.find_all("div", class_="expansion-year")
    for yearly_expansions in expansions_per_year:
        expansions = yearly_expansions.find_all("div", class_="product-item")

        for expansion in expansions:
            expansion_url = expansion.find('a')["href"].strip()
            img_url = expansion.find("img")["src"].strip()

            category = expansion.find("div", class_="category").text.strip()
            title = expansion.find("div", class_="title").text.strip()
            release_date = expansion.find("div", class_="release").text.strip()
            clan = expansion.find("div", class_="clan").text.strip()

            # Remove punctuation except '-', '_', '[' and ']'
            expansion_file = re.sub(r'[^\w\s\-_\[\]]', '', title, re.UNICODE)
            expansion_file = re.sub(r'\s+', '_', expansion_file, re.UNICODE)
            expansion_file += ".json"

            if Path(DB_DIR / expansion_file).exists():
                logger.debug(f"Expansion {title} already in database, not scrapping")
                continue
            else:
                logger.info(f"Parsing expansion {title}")
            scrap_cards_from_expansion(VANGUARD_ROOT_URL + expansion_url, DB_DIR / expansion_file)

            # Log expansion in database only once the entire list of card is in
            expansion_dict = {
                    "title": title,
                    "category": category,
                    "release": release_date,
                    "clan": clan,
                    "image_url": img_url,
                    "expansion_file": expansion_file
                    }

            # Log and clean data
            log_query(expansions_url, expansion_dict)
            logger.info(f"Finished Parsing expansion {title}")
            expansion_dict = clean_expansion_dict(expansion_dict)

            expansion_dicts.append(expansion_dict)
            with Path(DB_DIR / "database.json").open('w') as db_file:
                json.dump(expansion_dicts, db_file, indent=2)


if __name__ == "__main__": 
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--db_dir", nargs='?', type=str, help="Destination directory for the scrapped json files. Path is relative to current pwd. Directory will be created if it does not exist.")
    args = parser.parse_args()

    if args.db_dir:
        DB_DIR = Path(args.db_dir)
    else:
        DB_DIR = Path(__file__).parent.absolute().joinpath(DB_DIR)

    DB_DIR.mkdir(parents=True, exist_ok=True)

    logger = scrapper_logger.get_logger(DB_DIR / "scrapper.log")
    logger.info(f"Logging to {DB_DIR / 'scrapper.log'}")
    scrap_expansions(VANGUARD_ROOT_URL + "/cardlist")
