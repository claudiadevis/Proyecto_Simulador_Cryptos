from flask_wtf import FlaskForm
from wtforms import (
    SelectField,
    DecimalField,
    ValidationError
)
from wtforms.validators import DataRequired, NumberRange

from .models import monedas


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
        ('DOGE', 'Dogecoin')
    ]

    moneda_from = SelectField('From:', choices=lista_monedas, validators=[DataRequired('Debe ingresar una moneda'), validate_moneda]
                              )

    moneda_to = SelectField('To:', choices=lista_monedas, validators=[DataRequired('Debe ingresar una moneda'), validate_moneda, validate_monedas]
                            )

    cantidad = DecimalField('Q:', places=6, validators=[
        DataRequired('No puede haber una compra sin una cantidad'),
        NumberRange(
            min=0.00001, message='No se permiten cantidades inferiores a 0.00001')
    ])
