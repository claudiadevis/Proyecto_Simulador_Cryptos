from datetime import datetime

from flask import Flask, render_template, request, flash

from . import app
from .models import Cartera, ListaMovimientosDB, Consulta_coinapi, Movimiento

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

                return render_template('compra.html', form=formulario, cantidad_to=cantidad_to, precio_unitario=precio_unitario, blockControl=True)

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
                mov_dict = consulta.construir_diccionario()

                lista = ListaMovimientosDB()
                movimiento = Movimiento(mov_dict)
                resultado = lista.agregar_movimiento(movimiento)

                if resultado == 1:
                    flash('El movimiento se ha añadido correctamente')
                elif resultado == -1:
                    flash('El movimiento no se ha guardado. Inténtalo de nuevo.')
                else:
                    flash('Houston, tenemos un problema')

            return render_template('compra.html', form=formulario)

    else:
        return "Error"


@app.route('/status')
def estado():
    cartera = Cartera()
    totales = cartera.consulta_totales_SQL()
    print(totales)
    return render_template('status.html', totales_monedas=totales)
