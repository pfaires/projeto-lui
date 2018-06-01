# -*- coding: utf-8 -*-
"""
Created on Wed May 30 13:16:18 2018

@author: Paulo
"""

from bs4 import BeautifulSoup
from browser import Browser
from urllib.error import HTTPError
from datetime import datetime
import pandas as pd

# Retorna o texto de uma tag removendo os espaços antes e depois
def strip_text(field):
    return field.text.strip()

# Verifica se a classe de um elemento é a que o sportingbet usa para
# mostrar os odds dos jogos
def is_class_odds(css_class):
    return  css_class is not None and \
            css_class.startswith("mb-option-button__option-name mb-option-button__option-name--odds-")
# Recupera os dados da pagina HTML para um evento (jogo)
def data_for_event(event, date):
    time =  event.find("div", \
                       "marketboard-event-without-header__market-time")
    teams = event.find_all("div", \
                           class_ = is_class_odds)
    odds = event.find_all("div", \
                           "mb-option-button__option-odds ")
    match_id = event.find("a", target="statistics") \
                    .attrs["href"] \
                    .split("/")[-1].strip()
    return [ date + " " + strip_text(time), match_id ] + \
           [strip_text(item) for item in [teams[0], odds[0], odds[1], teams[2], odds[2]] ]

# Recupera os dados da pagina HTML para um subgrupo: uma data e diversos eventos
def data_for_subgroup(subgroup):
    events = subgroup.find_all("div","marketboard-event-group__item--event")
    date = subgroup.h2.text.split(" - ")[1].strip()
    return [data_for_event(e, date) for e in events]

# Recupera os dados da página para um Grupo da copa
def data_for_group(group):
    subgroups = group.find_all("div","marketboard-event-group__item--sub-group")
    return map(data_for_subgroup, subgroups[1:])

# Recupera os dados da pagina e retorna um dataframe
def scrape():
    browser = Browser()
    data = {"sportId": "4",
            "leagueIds": "63154,63156,63158,63160,63162,63164,63166,63168",
            "page": "0"}
    try:
        # Post na pagina de odds
        # contents = browser.get("https://sports.sportingbet.com/pt-br/sports#eventId=&leagueIds=63154,63156,63158,63160,63162,63164,63166,63168&marketGroupId=&page=0&sportId=4")
        contents = browser.post("https://sports.sportingbet.com/en/sports/indexmultileague", data)
        page = contents.read()
        # pega os grupos e processa
        doc = BeautifulSoup(page, "html.parser")
        groups = doc.find_all("div", class_="marketboard-event-group")
        data = [data_for_group(g) for g in groups]
        # desfaz a estrutura grupos->subgrupos->eventos, já que so estamos interessados
        # nos eventos (jogos)
        flattened_data = [e for g in data for sg in g for e in sg]
        # Transforma em dataframe e converte colunas numericas
        df = pd.DataFrame(flattened_data, columns = ["datetime", "match_id", "team_a", "odds_a", "odds_tie", "team_b", "odds_b"])
        df[["odds_a","odds_tie", "odds_b"]] = df[["odds_a","odds_tie", "odds_b"]].astype(float)
        df["match_id"] = df["match_id"].astype(int)
        return df
    except HTTPError as e:
        print(e.msg, e.code, e.hdrs)

# se o script for executado da linha de comando, captura dados e exporta para csv
if __name__ == "__main__":
    df = scrape()
    filename = "sportingbet_%s.csv" % datetime.now().strftime("%d%m%Y%H%M%S") 
    df.to_csv(filename, index = False)
