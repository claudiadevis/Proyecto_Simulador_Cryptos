from flask_wtf import FlaskForm
from wtforms import (
    SelectField,
    DecimalField,
    HiddenField,
)
from wtforms.validators import DataRequired, NumberRange

from .models import monedas


class MovimientoForm(FlaskForm):

    moneda_from = SelectField('From:', choices=[
        ('', ''),
        ('EUR', 'Euro'),
        ('BTC', 'BTC'),
        ('ETH', 'ETH'),
        ('USDT', 'USDT'),
        ('ADA', 'ADA'),
        ('SOL', 'SOL'),
        ('XRP', 'XRP'),
        ('DOT', 'DOT'),
        ('DOGE', 'DOGE')
    ], validators=[DataRequired('Debe ingresar una moneda')]
    )

    moneda_to = SelectField('To:', choices=[
        ('', ''),
        ('EUR', 'Euro'),
        ('BTC', 'BTC'),
        ('ETH', 'ETH'),
        ('USDT', 'USDT'),
        ('ADA', 'ADA'),
        ('SOL', 'SOL'),
        ('XRP', 'XRP'),
        ('DOT', 'DOT'),
        ('DOGE', 'DOGE')
    ], validators=[DataRequired('Debe ingresar una moneda')]
    )

    cantidad = DecimalField('Q:', places=6, validators=[
        DataRequired('No puede haber una compra sin una cantidad'),
        NumberRange(
            min=0.00001, message='No se permiten cantidades inferiores a 0.00001')
    ])
