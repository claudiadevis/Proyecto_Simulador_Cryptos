from datetime import datetime

from flask import Flask, render_template, request

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

        boton = request.form['boton']

        if boton == 'calcular':

            if formulario.validate():
                moneda_from = formulario.moneda_from.data
                moneda_to = formulario.moneda_to.data
                cantidad_from = formulario.cantidad.data

                consulta = Consulta_coinapi(
                    moneda_from, moneda_to, cantidad_from)
                cantidad_to = consulta.calcular_cantidad_to()
                precio_unitario = consulta.calcular_precio_unitario()

                # mov_dict = {
                #     'fecha': fecha_tasa_coinapi[1],
                #     'hora': fecha_tasa_coinapi[2],
                #     'moneda_from': moneda_from,
                #     'cantidad_from': cantidad_from,
                #     'moneda_to': moneda_to,
                #     'cantidad_to': cantidad_to,
                # }

                # movimiento = Movimiento(mov_dict)

                return render_template('compra.html', form=formulario, cantidad_to=cantidad_to, precio_unitario=precio_unitario)

            else:
                return render_template('compra.html', form=formulario)

        elif boton == 'enviar':
            if formulario.validate():
                moneda_from = formulario.moneda_from.data
                moneda_to = formulario.moneda_to.data
                cantidad_from = formulario.cantidad.data

                consulta = Consulta_coinapi(
                    moneda_from, moneda_to, cantidad_from)
                consulta.calcular_cantidad_to()
                consulta.calcular_precio_unitario()
                movimiento = consulta.construir_movimiento()

            return render_template('compra.html', form=formulario)

    else:
        return "Error"
