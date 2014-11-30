from flask import Flask, render_template, session, redirect, url_for, flash
from flask.ext.script import Manager
from flask.ext.bootstrap import Bootstrap
from flask.ext.moment import Moment
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import Required, NumberRange, ValidationError
from main import tk_quote
from main import black_scholes 
import numpy as np

app = Flask(__name__)
app.config['SECRET_KEY'] = 'just a empty string'

manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/research')
def research():
    return render_template('research.html')

class NameForm(Form):
#    name   = StringField('Ticket, (e.g., AAPL, FB, YHOO)', 
#                         validators=[Required()])
    optype = SelectField('Call or Put', choices=[('call','call'),('put','put')],
                         validators=[Required(),])
    def check_is_float(form, field):
        if field.data is None:
            raise ValidationError('This field is required')
        try: 
            value = float(field.data)
        except TypeError:
            raise ValidationError('Please input a number')
        except ValueError:
            raise ValidationError('Please input a number')
        if value <= 0.0:
            raise ValidationError('Must be larger than 0')

    volatility = StringField('Volatility',
                         validators=[check_is_float]) 
    expiration = StringField('Expiration',
                         validators=[check_is_float]) 
    spot = StringField('Spot price',
                         validators=[check_is_float]) 
    strike = StringField('Strike price',
                         validators=[check_is_float]) 
    interest_rate = StringField('Interest rate',
                         validators=[check_is_float]) 
    submit = SubmitField('Submit')

@app.route('/pricer', methods=['GET', 'POST'])
def pricer():
    form = NameForm()
    if form.validate_on_submit():
        optype = form.optype.data
        volatility = float(form.volatility.data)
        expiration = float(form.expiration.data)
        spot       = float(form.spot.data)
        strike     = float(form.strike.data)
        interest_rate= float(form.interest_rate.data)
        value = black_scholes.BlackScholes(optype[0], spot, strike,
                        expiration, interest_rate, volatility)
        session['value'] = str(round(value,2))
        session['name']  = optype 
        spot_list  = np.linspace(spot/2,spot*1.5,10)
        spot_value_list = [(it_spot, black_scholes.BlackScholes(optype[0], 
               it_spot, strike, expiration, 
               interest_rate, volatility)) for it_spot in spot_list]
        session['spot_value_list']  = spot_value_list
    else:
        session['value'] = None
        session['name']  = None 
        session['spot_list']  = None
        session['value_list'] = None
    return render_template('pricer.html', form=form, 
                           ticket     = session.get('name'),
                           price      = session.get('value'),
                           spot_value_list = session.get('spot_value_list')) 


if __name__ == '__main__':
    manager.run()
