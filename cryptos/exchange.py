
import requests

apikey = '54CC9DB5-A9E5-4DEF-AFCA-BFAEE77C7995'
server = 'https://rest.coinapi.io'
endpoint = '/v1/exchangerate'
headers = {
    'X-CoinAPI-Key': apikey
}


class Coinapi():

    def __init__(self, moneda_from, cantidad_from, moneda_to):
        self.url = server + endpoint + '/' + moneda_from + '/' + moneda_to
        response = requests.get(url, headers=headers)

    def construir_movimiento():
        if response.status_code == 200:
            exchange = response


mov_dict = {
    'fecha':
}
