from flask_wtf import FlaskForm
from wtforms import (
    SelectField,
    DecimalField,
    ValidationError
)
from wtforms.validators import DataRequired, NumberRange

from .models import monedas, Cartera


def validate_moneda(form, field):
    if field.data not in monedas:
        raise ValidationError(
            f'La moneda seleccionada "{field.data}" no se encuentra dentro del listado de monedas permitidas en la transacción')
    if field.data == '':
        raise ValidationError(f'Selecciona una moneda del desplegable')


def validate_monedas(form, field):
    if form.moneda_from.data == field.data:
        raise ValidationError(
            'No se permite una transacción con moneda origen y destino iguales')


def validate_Q_disponible(form, field):
    cartera = Cartera()
    cartera.consulta_sql()
    monedas_disponibles = cartera.obtener_totales_monedas()
    moneda_from = form.moneda_from.data
    if moneda_from == '':
        raise ValidationError(f'Selecciona una moneda del desplegable')

    if moneda_from != 'EUR':
        if monedas_disponibles[moneda_from] == 0:
            raise ValidationError(
                f'La moneda "{moneda_from}" no existe en tu cartera')
        moneda_disponible = monedas_disponibles[moneda_from]
        if field.data > moneda_disponible:
            raise ValidationError(f'No tienes suficientes "{
                moneda_from}" en tu cartera para efectuar esta operación')


class MovimientoForm(FlaskForm):

    lista_monedas = [
        ('', ''),
        ('EUR', 'Euro'),
        ('BTC', 'Bitcoin'),
        ('ETH', 'Ethereum'),
        ('USDT', 'Tether'),
        ('ADA', 'Cardano'),
        ('SOL', 'Solana'),
        ('XRP', 'Ripple'),
        ('DOT', 'Polkadot'),
        ('DOGE', 'Dogecoin'),
        ('SHIB', 'Shiba Inu'),
    ]

    moneda_from = SelectField('From:', choices=lista_monedas,
                              validators=[DataRequired(
                                  'Debe ingresar una moneda origen'), validate_moneda],
                              render_kw={'disabled': False}
                              )

    moneda_to = SelectField('To:', choices=lista_monedas,
                            validators=[DataRequired('Debe ingresar una moneda destino'),
                                        validate_moneda, validate_monedas],
                            render_kw={'disabled': False}
                            )

    cantidad = DecimalField('Q:', places=6, validators=[
        DataRequired(
            'No puede haber una compra sin una cantidad'), validate_Q_disponible,
        NumberRange(
            min=0.00001, message='No se permiten cantidades inferiores a 0.00001')
    ])
