from flask import Flask, render_template, session, redirect, url_for, flash
from flask.ext.script import Manager
from flask.ext.bootstrap import Bootstrap
from flask.ext.moment import Moment
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import Required, NumberRange, ValidationError
from main import tk_quote
from main import black_scholes 
from main.american_put_pricer import american_put
from main.plot_tools import plot_line
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
    call_or_put = SelectField('Call or Put', choices=[('call','call'),('put','put')],
                         validators=[Required(),])
    optype = SelectField('European or American', 
                     choices=[('European','European'),('American','American')],
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

    volatility = StringField('Volatility (annualized)',
                         validators=[check_is_float]) 
    expiration = StringField('Expiration (in year)',
                         validators=[check_is_float]) 
    spot = StringField('Spot price',
                         validators=[check_is_float]) 
    strike = StringField('Strike price',
                         validators=[check_is_float]) 
    interest_rate = StringField('Interest rate % (in percentage)',
                         validators=[check_is_float], default='0.25') 
    submit = SubmitField('Submit')

@app.route('/pricer', methods=['GET', 'POST'])
def pricer():
    form = NameForm()
    if form.validate_on_submit():
        call_or_put = form.call_or_put.data
        optype      = form.optype.data
        volatility = float(form.volatility.data)
        expiration = float(form.expiration.data)
        spot       = float(form.spot.data)
        strike     = float(form.strike.data)
        interest_rate= float(form.interest_rate.data)/100.0
        session['name']  = call_or_put 
        spot_list  = np.linspace(spot/2,spot*1.5,10)
        if call_or_put[0] == 'p' and optype[0] == 'E':
            value = american_put(volatility, interest_rate,
                   0, expiration, strike, spot, 5000)
            spot_value_list = [(it_spot, american_put(volatility, interest_rate,
                   0, expiration, strike, it_spot, 1000)) for it_spot in spot_list]
        else:
            value = black_scholes.BlackScholes(call_or_put[0], spot, strike,
                        expiration, interest_rate, volatility)
            spot_value_list = [(it_spot, black_scholes.BlackScholes(call_or_put[0], 
                   it_spot, strike, expiration, 
                   interest_rate, volatility)) for it_spot in spot_list]
        session['value'] = str(round(value,2))
        session['spot_value_list']  = spot_value_list
        spot_price_chart_html = plot_line(spot_list,
                            [y for (tmp, y) in spot_value_list],
                            'Spot vs. price for' + optype + call_or_put,
                            'Spot',
                            'Price')
        session['chart_html'] = spot_price_chart_html
    else:
        session['value'] = None
        session['name']  = None 
        session['spot_list']  = None
        session['value_list'] = None
    return render_template('pricer.html', form=form, 
                           ticket     = session.get('name'),
                           price      = session.get('value'),
                           spot_value_list = session.get('spot_value_list'),
                           spot_vs_price_plot = session.get('chart_html')) 


if __name__ == '__main__':
    manager.run()
