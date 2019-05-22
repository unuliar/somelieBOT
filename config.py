# -*- coding: utf-8 -*-

from enum import Enum

token = '891676728:AAEl_6OWG86_g2o39tLZMoHP3V36OJDlyGo'
db_file = "db.vdb"
static_params='?country_code=RU&currency_code=RUB&grape_filter=varietal&order=desc'

class States(Enum):
    S_START = "0"
    S_ENTER_WINE_TYPE = "1"
    S_ENTER_WINE_PRICE = "2"
    S_ENTER_WINE_RATING = "3"
