from mapping import LOCATION_CONFIG
from hotel_item import HotelLocationSearchItem
import requests
import urllib.parse

class Logitravel():

    @property
    def site(self):
        return 'logitravel'

    @property
    def market(self):
        return 'com'

    @property
    def base_url(self):
        return 'https://www.logitravel.com'

    def _search(self, Request):
        self.hotels_found = []

        location = Request.location.upper()
        self.config = LOCATION_CONFIG.get(location, {})
        if not self.config:
            print('Not Config!!')

        self.check_in = Request.checkin_date
        self.check_out = Request.checkout_date

        # GET method to obtain full list hotels
        headers = {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'es-ES,es;q=0.9',
            'referer': f'{self.base_url}/hotels/results/?code={self.config}&type=CIU&check_in={self.check_in}&check_out={self.check_out}&rooms=30,30',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
        }
        params = {
            'code': self.config,
            'type': 'CIU',
            'new_search': 'false',
            'check_in': self.check_in,
            'check_out': self.check_out,
            'line': 'hotels',
            'language': 'es',
            'is_list': 'true',
            'is_summary': 'false',
            'market': 'es',
            'currency': 'EUR',
        }

        url = f'{self.base_url}/hotels/api/hotel/top/?{urllib.parse.urlencode(params)}'
        res = requests.get(url, headers=headers)
        print(f'GET RESPONSE: {res}')

        all_hotels = res.json()

        # 2º POST method for know hotels availables
        params = {
            'check_in': self.check_in,
            'check_out': self.check_out,
            'rooms': '30,30',
            'hotels': all_hotels.get('hotel_list'),
            'line': 'hotels',
            'is_list': 'true',
            'business_line': 8,
            'country': 'ES',
            'lang': 'es',
            'market': 'es',
            'currency': 'EUR',
            'resident': 'false',
            'senior': 'false'
        }
        url = f'{self.base_url}/hotels/api/results/avail/'

        res_avail = requests.post(url, json=params)
        print(f'POST RESPONSE: {res_avail}')

        # 3º GET method to obtain hotel info
        avail_hotels = res_avail.json().get('hotels')
        str_ids = ''

        for hotel in avail_hotels:
            str_ids = str_ids + hotel.get('hotel') + ','
        str_ids = str_ids[:-1]

        headers = {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'es-ES,es;q=0.9',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
        }
        params = {
            'hotels': str_ids,
            'language': 'es',
            'is_list': 'true'
        }

        url = f'{self.base_url}/hotels/api/hotel/search/?{urllib.parse.urlencode(params)}'

        res = requests.get(url, headers=headers)
        print(f'GET RESPONSE: {res}')

        # Parser
        hotels_info = res.json()
        results = self._parse(hotels_info, avail_hotels)
        if not results:
            raise TypeError('NOT RESULTS')

        return results

    def _parse(self, hotels_info, avail_hotels, page=1):

        hotels_list = hotels_info.get('hotels')
        if not hotels_list:
            raise TypeError("Not Hotel list in parse")

        results = []
        for hotel in hotels_list:
            hotel_info = hotels_list.get(hotel).get('hotel_info')
            price = ''
            board = ''

            for i in avail_hotels:
                if i.get('hotel') == hotel:
                    price = i.get('options')[0].get('price')
                    board = i.get('options')[0].get('board')

            item = HotelLocationSearchItem()
            item.id_hotel = hotel_info.get('hotel_code')
            item.hotel = hotel_info.get('name')
            item.latitude = hotel_info.get('geocoding').get('latitude')
            item.longitude = hotel_info.get('geocoding').get('longitude')
            item.base_score = 10.0
            item.score = hotel_info.get('average')
            item.stars = hotel_info.get('hotel_category')
            item.city = hotel_info.get('city_name')
            item.price = str(price) + ' €'
            item.board = board

            results.append(item)

        return results
