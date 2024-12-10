from datetime import datetime
from cryptos import app

import sqlite3
import requests

RUTA_DB = 'cryptos/data/cryptos.db'


monedas = [
    'EUR',
    'BTC',
    'ETH',
    'USDT',
    'ADA',
    'SOL',
    'XRP',
    'DOT',
    'DOGE',
    'SHIB',
]


class DBManager:
    """
    Clase para interactuar con la base de datos
    """

    def __init__(self, ruta):
        self.ruta = ruta

    def consultarSQL(self, consulta):

        conexion = sqlite3.connect(self.ruta)
        cursor = conexion.cursor()
        cursor.execute(consulta)
        datos = cursor.fetchall()

        self.registros = []
        nombres_columna = []

        for columna in cursor.description:
            nombres_columna.append(columna[0])

        for dato in datos:
            movimiento = {}
            indice = 0
            for nombre in nombres_columna:
                movimiento[nombre] = dato[indice]
                indice += 1
            self.registros.append(movimiento)

        conexion.close()
        return self.registros


class Movimiento:

    def __init__(self, dict_mov):
        self.errores = []

        fecha = dict_mov.get('date', '')
        hora = dict_mov.get('time', '')
        moneda_from = dict_mov.get('from_currency', '')
        cantidad_from = dict_mov.get('from_quantity', 0)
        moneda_to = dict_mov.get('to_currency', '')
        cantidad_to = dict_mov.get('to_quantity', 0)

        self.id = dict_mov.get('id')

        # Validación fecha y hora
        try:
            fecha_hora = fecha + 'T' + hora + 'Z'
            self.fecha_hora = datetime.fromisoformat(fecha_hora)
            self.fecha = fecha
            self.hora = hora
        except ValueError:
            self.fecha_hora = None
            mensaje = f'La fecha u hora no están en el formato ISO 8601'
            self.errores.append(mensaje)
        except TypeError:
            self.fecha_hora = None
            mensaje = f'La fecha u hora no son una cadena'
            self.errores.append(mensaje)
        except:
            self.fecha_hora = None
            mensaje = f'Error desconocido con la fecha u hora'
            self.errores.append(mensaje)

        # Validación from (moneda)
        if moneda_from in monedas:
            self.moneda_from = moneda_from
        else:
            raise ValueError(
                f'La moneda {moneda_from} no es una moneda válida')

        # Validación to (moneda)
        if moneda_to in monedas:
            self.moneda_to = moneda_to
        else:
            raise ValueError(f'La moneda {moneda_to} no es una moneda válida')

        # Validación cantidad_from
        try:
            valor = float(cantidad_from)
            if valor > 0:
                self.cantidad_from = valor
            else:
                self.cantidad_from = 0
                mensaje = f'El importe de la cantidad debe ser un número mayor que cero'
                self.errores.append(mensaje)

        except ValueError:
            self.cantidad_from = 0
            mensaje = f'El valor no es convertible a número'
            self.errores.append(mensaje)

        # Validación cantidad_to
        try:
            valor = float(cantidad_to)
            if valor > 0:
                self.cantidad_to = valor
            else:
                self.cantidad_to = 0
                mensaje = f'El importe de la cantidad debe ser un número mayor que cero'
                self.errores.append(mensaje)

        except ValueError:
            self.cantidad_to = 0
            mensaje = f'El valor no es convertible a número'
            self.errores.append(mensaje)

        if self.cantidad_to:
            if self.cantidad_from:
                self.precio_unitario = round(
                    self.cantidad_from / self.cantidad_to, 4)

    @property
    def has_errors(self):
        return len(self.errores) > 0

    def __str__(self):
        return f'{self.fecha} | {self.hora} | {self.moneda_from} | {self.cantidad_from} | {self.moneda_to} | {self.cantidad_to}'

    def __repr__(self):
        return self.__str__()


class ListaMovimientosDB:

    def __init__(self):
        try:
            self.cargar_movimientos()
        except:
            self.movimientos = []

    def cargar_movimientos(self):
        db = DBManager(RUTA_DB)
        sql = 'SELECT id, date, time, from_currency, from_quantity, to_currency, to_quantity FROM movimientos'
        datos = db.consultarSQL(sql)

        self.movimientos = []
        for dato in datos:
            mov = Movimiento(dato)
            # ☺print(mov)
            self.movimientos.append(mov)


class Consulta_coinapi:

    def consultar_tasa(self,  origen, destino):
        server = 'https://rest.coinapi.io'
        endpoint = '/v1/exchangerate'
        headers = {
            'X-CoinAPI-Key': app.config['API_KEY']
        }
        url = server + endpoint + '/' + origen + '/' + destino
        response = requests.get(url, headers=headers)
        lista = []

        if response.status_code == 200:
            exchange = response.json()
            tasa = exchange.get('rate', 0)
            lista.append(tasa)
            fecha_hora = exchange.get('time', '')
            fecha, hora = fecha_hora.split('T')
            lista.append(fecha)
            hora = hora[:-1]
            lista.append(hora)

        return lista
