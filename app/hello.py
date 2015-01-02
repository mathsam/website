from flask import Flask, render_template, session, redirect, url_for, flash, request
from flask.ext.script import Manager
from flask.ext.bootstrap import Bootstrap
from flask.ext.moment import Moment
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import Required, NumberRange, ValidationError
from main import tk_quote
from main import black_scholes 
from main.american_put_pricer import american_put
from main.plot_tools import plot_line, plot_time_multilines
import numpy as np
import json
#import redis
#from simplekv.memory.redisstore import RedisStore
from flask_kvsession import KVSessionExtension
from simplekv.memory import DictStore
import simplekv

import sys
sys.path.append('/media/junyic/Work/Courses/4th_year/SoftwareEngineering/Project/UltraFinance/')
from data_analysis.volatility import get_hist_vol

#store = RedisStore(redis.StrictRedis())
store = DictStore()
simplekv.TimeToLiveMixin = (20) # session expires after 60 sec

app = Flask(__name__)
app.config['SECRET_KEY'] = 'just a empty string'
KVSessionExtension(store, app)

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


class PricerForm(Form):
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

    def check_pd(form, field):
        """
        check if positive definite (>0)
        """
        value = float(field.data)
        if value <= 0.0:
            raise ValidationError('Must be larger than 0')

    def check_psd(form, field):
        """
        check if positive semi definite (>=0)
        """
        value = float(field.data)
        if value < 0.0:
            raise ValidationError('Must be no less than 0')


    volatility = StringField('Volatility (annualized)',
                         validators=[check_is_float, check_pd]) 
    expiration = StringField('Expiration (in year)',
                         validators=[check_is_float, check_pd]) 
    spot = StringField('Spot price',
                         validators=[check_is_float, check_pd]) 
    strike = StringField('Strike price',
                         validators=[check_is_float, check_pd]) 
    interest_rate = StringField('Interest rate % (in percentage)',
                         validators=[check_is_float, check_psd], default='0.25') 
    submit = SubmitField('Submit')

@app.route('/pricer', methods=['GET', 'POST'])
def pricer():
    form = PricerForm()
    print session.get('name')
    if form.validate_on_submit():
        call_or_put = form.call_or_put.data
        optype      = form.optype.data
        volatility = float(form.volatility.data)
        expiration = float(form.expiration.data)
        spot       = float(form.spot.data)
        strike     = float(form.strike.data)
        interest_rate= float(form.interest_rate.data)/100.0
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
        session['name']  = call_or_put 
        session['spot_value_list']  = spot_value_list
        spot_price_chart_html = plot_line(spot_list,
                            [y for (tmp, y) in spot_value_list],
                            'chart_spot_vs_price',
                            'Spot vs. price for ' + optype + ' ' + call_or_put,
                            'Spot',
                            'Price')
        session['chart_html'] = spot_price_chart_html
#        return redirect(url_for('pricer'))
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


class HisVolForm(Form):
    def check_if_ticket_exist(form, field):
        if field.data is None:
            raise ValidationError('This field is required')

        if session.get('ylabels'):
            ticket_set = json.loads(session.get('ylabels'))
            if field.data.upper() in ticket_set:
                raise ValidationError('Ticket already exists')
            elif len(ticket_set) >= 5:
                raise ValidationError('Total number of tickets must <= 5. Please \
                                       Clear chart first!')

        try:
            ticket = str(field.data.upper())
            vol, vol_date, adj_close = get_hist_vol(ticket)
            form.vol = [100*vol_it for vol_it in vol]
            form.vol_date  = vol_date
            form.adj_close = adj_close
        except ValueError:
            raise ValidationError('Sorry, ticket does not exist in database')

    ticket = StringField('Ticket (e.g., AAPL, FB, YHOO in S&P 500)',
                         validators=[check_if_ticket_exist])
    submit = SubmitField('Add to chart')


@app.route('/volatility', methods=['GET', 'POST'])
def volatility():
    session.permanent = False
    form = HisVolForm()
    try:
        if request.form['clear_chart'] == 'Clear chart':
            session['tickets'] = None
            session['ylabels'] = None
            session['vol']     = None
            session['adj_close'] = None
            return render_template('volatility.html', form=form, 
                           ticket = session.get('tickets'),
                           vol_chart = session.get('vol_chart'),
                           adj_chart = session.get('adj_chart'))
    except KeyError:
        pass

    if form.validate_on_submit():
        if session.get('tickets') is None:
            session['tickets'] = form.ticket.data.upper()
        else:
            session['tickets'] += ' ' + form.ticket.data.upper()

        if session.get('ylabels') is None:
            vol       = []
            adj_close = []
            ylabels   = []
        else:
            vol       = json.loads(session.get('vol'))
            adj_close = json.loads(session.get('adj_close'))
            ylabels   = json.loads(session.get('ylabels'))

        vol.append(list(form.vol))
        adj_close.append(list(form.adj_close))
        ylabels.append(form.ticket.data.upper())
        session['vol']       = json.dumps(vol)
        session['adj_close'] = json.dumps(adj_close)
        session['ylabels']   = json.dumps(ylabels)

        session['vol_chart'] = plot_time_multilines(form.vol_date,
                                vol, 'vol_chart', 'Date', ylabels)
        session['adj_chart'] = plot_time_multilines(form.vol_date,
                          adj_close, 'adj_chart', 'Date', ylabels)

    print session.get('tickets'), session.get('ylabels')
    return render_template('volatility.html', form=form, 
                           ticket = session.get('tickets'),
                           vol_chart = session.get('vol_chart'),
                           adj_chart = session.get('adj_chart')) 

@app.route('/doc_fin')
def doc_fin():
    return render_template('financial_doc.html')

if __name__ == '__main__':
    manager.run()
