from flask import render_template

from cryptos.models import ListaMovimientosDB, Movimiento

from . import app


@app.route('/')
def home():
    lista = ListaMovimientosDB()
    return render_template('inicio.html', movs=lista.movimientos)


@app.route('/compra')
def comprar():
    return render_template('compra.html')
