# -*- coding: utf-8 -*-

from vedis import Vedis
import config


# Пытаемся узнать из базы «состояние» пользователя
def get_current_state(user_id):
    with Vedis(config.db_file) as db:
        try:
            return db[user_id] #.decode()
        except KeyError:
            return config.States.S_START.value


def set_state(user_id, value):
    with Vedis(config.db_file) as db:
        try:
            db[user_id] = value
            return True
        except:
            return False


def add_to_end(user_id, value):
    with Vedis(config.db_file) as db:
        try:
            db[user_id] = db[user_id].decode() + value
            return True
        except:
            return False
