from datetime import datetime

from flask import flash
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

    def agregar_movimiento(self, Movimiento):

        conexion = sqlite3.connect(self.ruta)
        cursor = conexion.cursor()

        sql = 'INSERT INTO movimientos (date, time, from_currency, from_quantity, to_currency, to_quantity) VALUES (?, ?, ?, ?, ?, ?)'

        try:
            params = (
                Movimiento.fecha,
                Movimiento.hora,
                Movimiento.moneda_from,
                Movimiento.cantidad_from,
                Movimiento.moneda_to,
                Movimiento.cantidad_to,
            )
            cursor.execute(sql, params)
            conexion.commit()
            resultado = cursor.rowcount

        except Exception as ex:
            print('Ha ocurrido un error al añadir el movimiento en la base de datos')
            print(ex)
            conexion.rollback()

        conexion.close()

        return resultado


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
            self.hora = hora[:8]
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
                self.cantidad_to = round(valor, 4)
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
                    self.cantidad_from / self.cantidad_to, 8)

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

    def agregar_movimiento(self, movimiento):
        db = DBManager(RUTA_DB)
        return db.agregar_movimiento(movimiento)


class Consulta_coinapi:

    def __init__(self, moneda_from, moneda_to, cantidad_from):
        self.moneda_from = moneda_from
        self.moneda_to = moneda_to
        self.cantidad_from = float(cantidad_from)
        self.tasa = 0
        self.cantidad_to = 0

    def consultar_tasa(self):
        server = 'https://rest.coinapi.io'
        endpoint = '/v1/exchangerate'
        headers = {
            'X-CoinAPI-Key': app.config['API_KEY']
        }
        url = server + endpoint + '/' + self.moneda_from + '/' + self.moneda_to
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            exchange = response.json()
            return exchange
        else:
            return (f'Error', response.status_code, ':', response.reason)

    def obtener_fecha(self):
        fecha_hora_actual = datetime.now()
        hora = fecha_hora_actual.time()
        self.hora = hora.strftime('%H:%M:%S')
        self.fecha = fecha_hora_actual.date().isoformat()

    def calcular_cantidad_to(self, json_coinapi):
        rate = json_coinapi.get('rate', 0)
        self.tasa = float(rate)
        if self.tasa > 0:
            self.cantidad_to = self.cantidad_from * self.tasa
            return self.cantidad_to
        else:
            return 'La tasa es menor que cero, no se puede efectuar la transacción'

    def calcular_precio_unitario(self):
        precio_unitario = self.cantidad_from / self.cantidad_to
        return precio_unitario

    def construir_diccionario(self):

        mov_dict = {
            'date': self.fecha,
            'time': self.hora,
            'from_currency': self.moneda_from,
            'from_quantity': self.cantidad_from,
            'to_currency': self.moneda_to,
            'to_quantity': self.cantidad_to,
        }
        print(f'Moneda from = {self.moneda_from}')
        print(f'Moneda to = {self.moneda_to}')
        return mov_dict


class Cartera():

    def __init__(self):
        self.diccionario_resta = {}
        self.total_euros_inv = 0
        self.nuevo_diccionario_to = {}
        self.nuevo_diccionario_from = {}
        self.total_euros_venta = 0
        self.euros_equiv = {}
        self.total_eur_equiv = 0

    def consulta_sql(self):
        """
        Este método devuelve una lista con dos diccionarios-
        El diccionario from contiene el listado de todas las monedas, estén o no la columna "From"
        y la suma de las cantidades para cada moneda. De no existir alguna de las cryptos entonces
        en cantidad devuelve 0.
        El diccionario to es similar al from, la diferencia es que toma las columnas To con sus respectivas
        cantidades en vez de from.
        """
        diccionario_to_sql = {}
        diccionario_from_sql = {}
        db = DBManager(RUTA_DB)

        consulta_to = 'SELECT to_currency, SUM(to_quantity) as suma_to FROM movimientos GROUP BY to_currency'
        lista_to = db.consultarSQL(consulta_to)

        consulta_from = 'SELECT from_currency, SUM(from_quantity) as suma_from FROM movimientos GROUP BY from_currency'
        lista_from = db.consultarSQL(consulta_from)

        # diccionario to
        if lista_to != []:
            for diccionario in lista_to:
                nueva_clave = diccionario['to_currency']
                nuevo_valor = diccionario['suma_to']
                diccionario_to_sql[nueva_clave] = nuevo_valor
            print('lista_to:', lista_to)

            for moneda in monedas:
                for clave, valor in diccionario_to_sql.items():
                    if moneda in clave:
                        self.nuevo_diccionario_to[moneda] = valor
                        break
                    else:
                        self.nuevo_diccionario_to[moneda] = 0

            # diccionario from
            for diccionario in lista_from:
                nueva_clave = diccionario['from_currency']
                nuevo_valor = diccionario['suma_from']
                diccionario_from_sql[nueva_clave] = nuevo_valor

            for moneda in monedas:
                for clave, valor in diccionario_from_sql.items():
                    if moneda in clave:
                        self.nuevo_diccionario_from[moneda] = valor
                        break
                    else:
                        self.nuevo_diccionario_from[moneda] = 0

            diccionarios = [self.nuevo_diccionario_from,
                            self.nuevo_diccionario_to]

            return diccionarios
        else:
            return None

    def obtener_euros_invertidos(self):
        """
        Este método devuelve la suma de los euros invertidos, es decir, la suma de EUR que se encuentran
        en la columna From de los movimientos.
        """
        if self.nuevo_diccionario_from['EUR']:
            self.total_euros_inv = self.nuevo_diccionario_from['EUR']
        else:
            self.total_euros_inv = 0
        return self.total_euros_inv

    def obtener_euros_venta(self):
        """
        Este método devuelve la suma de los euros retirados, es decir, la suma de EUR que se encuentran
        en la columna To de los movimientos.
        """
        if self.nuevo_diccionario_to['EUR']:
            self.total_euros_venta = self.nuevo_diccionario_to['EUR']
        else:
            self.total_euros_venta = 0
        return self.total_euros_venta

    def obtener_totales_monedas(self):
        """
        Este método devuelve otro diccionario con las diferencias entre to y from por cada una de las monedas.
        Es básicamente la tabla que se muestra en status, a excepción de que este diccionario incluye
        todas las monedas del proyecto (devuelve 0 en cantidad si estas monedas no se encuentran en "from" ni "to")
        """
        self.diccionario_resta = {
            clave: round(self.nuevo_diccionario_to[clave] -
                         self.nuevo_diccionario_from[clave], 6)
            for clave in self.nuevo_diccionario_to}

        return self.diccionario_resta

    def encontrar_monedas(self, diccionario):
        """
        Este método únicamente se utiliza para el siguiente método obtener_equivalentes. Devuelve True si en diccionario con clave
        "asset_id_quote" se encuentran las monedas del proyecto.
        """
        if diccionario['asset_id_quote'] in monedas:
            return True
        return False

    def obtener_equivalentes(self):
        """
        Este método devuelve un diccionario únicamente con las monedas que se encuentran en la tabla de movimientos
        y sus cantidades equivalentes e euros utilizando la tasa de conversión de coinapi.
        """
        consulta = Consulta_coinapi('EUR', '', 1)
        exchange = consulta.consultar_tasa()
        tasas = exchange['rates']

        dict_filtrado = filter(
            self.encontrar_monedas, tasas)

        tasas_monedas = {item['asset_id_quote']: item['rate']
                         for item in dict_filtrado}

        self.euros_equiv = {
            moneda: round(self.diccionario_resta[moneda] * 1/tasas_monedas[moneda], 2) for moneda in self.diccionario_resta if moneda in tasas_monedas
        }
        return self.euros_equiv

    def calcular_total_euros_equiv(self):
        """
        Devuelve la suma de los valores del diccionario resultante de "obtener_equivalentes"
        """
        self.total_eur_equiv = round(sum(self.euros_equiv.values()), 2)
        return self.total_eur_equiv
