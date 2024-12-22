from datetime import datetime

from flask import Flask, render_template, request, flash, redirect, url_for

from . import app
from .models import Cartera, ListaMovimientosDB, Consulta_coinapi, Movimiento

from .forms import MovimientoForm


@app.route('/')
def home():
    lista = ListaMovimientosDB()
    return render_template('inicio.html', movs=lista.movimientos, current_path=request.path)


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
                json_coinapi = consulta.consultar_tasa()
                cantidad_to = round(
                    consulta.calcular_cantidad_to(json_coinapi), 6)
                precio_unitario = round(consulta.calcular_precio_unitario(), 6)

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
                json_coinapi = consulta.consultar_tasa()
                consulta.obtener_fecha()
                cantidad_to = consulta.calcular_cantidad_to(json_coinapi)
                precio_unitario = consulta.calcular_precio_unitario()
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

                return redirect(url_for('home'))

    else:
        return "Error"


@app.route('/status')
def estado():
    cartera = Cartera()
    consulta = cartera.consulta_sql()
    if consulta:
        total_euros_from = round(cartera.obtener_euros_invertidos(), 2)
        total_euros_to = round(cartera.obtener_euros_venta(), 2)
        # print(total_euros)

        totales_monedas = cartera.obtener_totales_monedas()
        eur_equiv = cartera.obtener_equivalentes()
        total_eur_equiv = cartera.calcular_total_euros_equiv()

        ganancia = round(total_eur_equiv + total_euros_to -
                         total_euros_from, 2)

        return render_template('status.html', resultado=True, totales_monedas=totales_monedas, total_euros_from=total_euros_from, total_euros_to=total_euros_to, eur_equiv=eur_equiv, total_eur_equiv=total_eur_equiv, ganancia=ganancia)

    else:
        return render_template('status.html', resultado=False, total_euros_from=0, total_euros_to=0, total_eur_equiv=0, ganancia=0)
