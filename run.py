from scraper import Logitravel
from request import Request

if __name__ == '__main__':
    num_adults = 2
    num_kids = 0
    location = 'Málaga'
    checkin_date = '01/08/2022'
    checkout_date = '07/08/2022'

    new_request = Request(num_adults, num_kids, location, checkin_date, checkout_date)
    hotels = Logitravel()._search(new_request)

    print('\n\nHotels found:\n')

    count = 1
    for hotel in hotels:
        print(f'Hotel number {count}º')
        print(f'\tName: {hotel.hotel}')
        print(f'\tPrice: {hotel.price}')
        print(f'\tScore: {hotel.score}\n')
        count += 1
