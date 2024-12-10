from datetime import datetime

from flask import render_template, request

from . import app
from .models import ListaMovimientosDB, Consulta_coinapi, Movimiento

from .forms import MovimientoForm


@app.route('/')
def home():
    lista = ListaMovimientosDB()
    return render_template('inicio.html', movs=lista.movimientos)


@app.route('/compra', methods=['GET', 'POST'])
def compra():
    formulario = MovimientoForm(data=request.form)

    if request.method == 'GET':
        return render_template('compra.html', form=formulario)

    if request.method == 'POST':

        if formulario.validate():
            moneda_from = formulario.moneda_from.data
            moneda_to = formulario.moneda_to.data
            cantidad_from = formulario.cantidad.data
            if moneda_from == moneda_to:
                return "La moneda origen no puede ser igual a la moneda destino"

            consulta = Consulta_coinapi()
            fecha_tasa_coinapi = consulta.consultar_tasa(
                moneda_from, moneda_to)
            tasa_coinapi = float(fecha_tasa_coinapi[0])
            cantidad_to = cantidad_from * tasa_coinapi

            mov_dict = {
                'fecha': fecha_tasa_coinapi[1],
                'hora': fecha_tasa_coinapi[2],
                'moneda_from': moneda_from,
                'cantidad_from': cantidad_from,
                'moneda_to': moneda_to,
                'cantidad_to': cantidad_to,
            }

            movimiento = Movimiento(mov_dict)

            return render_template('compra.html', form=formulario, mov=movimiento, cantidad_to=cantidad_to)

        else:
            return "Error"
