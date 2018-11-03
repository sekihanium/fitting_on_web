from wtforms import Form, FloatField, validators
from math import pi


class InputForm(Form):
    NBVL = FloatField(
        label='coefficient low', default=18,
        validators=[validators.InputRequired()])
    NBV = FloatField(
        label='coefficient', default=18,
        validators=[validators.InputRequired()])
    BV = FloatField(
        label='Brakedown voltage [V]', default=18,
        validators=[validators.InputRequired()])
    IBVL = FloatField(
        label='time interval (s)', default=18,
        validators=[validators.InputRequired()])
    IBV = FloatField(
        label='time interval (s)', default=18,
        validators=[validators.InputRequired()])
    Isr = FloatField(
        label='time interval (s)', default=18,
        validators=[validators.InputRequired()])
    Vj = FloatField(
        label='time interval (s)', default=18,
        validators=[validators.InputRequired()])
    M = FloatField(
        label='time interval (s)', default=18,
        validators=[validators.InputRequired()])
    NR = FloatField(
        label='time interval (s)', default=18,
        validators=[validators.InputRequired()])
    IKF = FloatField(
        label='time interval (s)', default=18,
        validators=[validators.InputRequired()])
    N = FloatField(
        label='time interval (s)', default=18,
        validators=[validators.InputRequired()])
    Is = FloatField(
        label='time interval (s)', default=18,
        validators=[validators.InputRequired()])