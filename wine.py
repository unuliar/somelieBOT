class wine:
    def __init__(self, name='', img='', stat_str='0', year_str='0', price_str='0', volume_ml='0', seo_name='', id=''):
        self.name = name
        self.image_link = img
        self.stat = float(stat_str)
        self.year = year_str
        self.price = int(price_str)
        self.volume = float(volume_ml) / 1000.0
        self.seo_name = seo_name
        self.id = id


class wine_request:
    type_id = 0

    def __init__(self, type_id='', min_price='', max_price='', min_rating=''):
        self.type_id = type_id
        self.min_price = min_price
        self.max_price = max_price
        self.min_rating = min_rating

    def serialize(self):
        params_static = "?country_code=RU&currency_code=RUB&grape_filter=varietal"
        params_str = "&min_rating={}&order_by=&order=desc&price_range_min={}&price_range_max={}&wine_type_ids[]={}"
        params_static += params_str
        params_str.format(self.min_rating, self.min_price, self.max_price, self.type_id)
        return params_str


def as_wine(dict):
    if 'vintage' in dict:
        vintage = dict['vintage']
        return wine(vintage['name'], vintage['image']['variations']['large'],
                    vintage['statistics']['ratings_average'], vintage['year'], dict['price']['amount'],
                    dict['price']['bottle_type']['volume_ml'], vintage['seo_name'], vintage['wine']['id'])
    return dict

