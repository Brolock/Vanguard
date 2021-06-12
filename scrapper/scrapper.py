import requests
from bs4 import BeautifulSoup

import json

cardlist_test_url="https://en.cf-vanguard.com/cardlist/cardsearch/?expansion=167&view=image&view=text&sort=no"

def scrap_card_data(card_url: str):
    print(card_url)
    page = requests.get(card_url)
    soup = BeautifulSoup(page.content, "html.parser")

    extension = soup.find("h3", class_="style-h3").text.strip()
    
    details = soup.find("div", class_="cardlist_detail")
    image_url = details.find("div", class_="image").find("img")["src"].strip()

    data = details.find("div", class_="data")

    name =   data.find("div", class_="name").text.strip()
    Type =   data.find("div", class_="type").text.strip()
    nation = data.find("div", class_="nation").text.strip()
    race =   data.find("div", class_="race").text.strip()

    grade =  data.find("div", class_="grade").text.strip()
    power =  data.find("div", class_="power").text.strip()
    crit =   data.find("div", class_="critical").text.strip()
    shield = data.find("div", class_="shield").text.strip()
    skill =  data.find("div", class_="skill").text.strip()
    gift =   data.find("div", class_="gift").text.strip()
    effect = data.find("div", class_="effect").text.strip()

    
    flavor =      data.find("div", class_="flavor").text.strip()
    regulation =  data.find("div", class_="regulation").text.strip()
    number =      data.find("div", class_="number").text.strip()
    rarity =      data.find("div", class_="rarity").text.strip()

    # illustrator has a typo
    illustrator = data.find("div", class_="illstrator").text.strip()

    card_data = {
            "Name": name,
            "Type": Type,
            "Nation": nation,
            "Race": race,
            "Grade": grade,
            "Power": power,
            "Critical": crit,
            "Shield": shield,
            "Skill": skill,
            "Gift": gift,
            "Effect": effect,
            "Flavor": flavor,
            "Regulation": regulation,
            "CardNumber": number,
            "Rarity": rarity
            }

    with open("{}.json".format(number.replace('/', '-')), 'w') as card_file:
        json.dump(card_data, card_file)

def scrap_cards_from_url(root_url: str, cardlist_url: str):
    page = requests.get(cardlist_url)
    soup = BeautifulSoup(page.content, "html.parser")

    card_list = soup.find("div", class_="cardlist_imagelist").find_all('li')

    for card in card_list:
        card_url = card.find('a')['href']
        scrap_card_data(root_url + card_url)

scrap_cards_from_url("https://en.cf-vanguard.com/", cardlist_test_url)
