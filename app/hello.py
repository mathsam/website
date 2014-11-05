from flask import Flask, render_template, session, redirect, url_for, flash
from flask.ext.script import Manager
from flask.ext.bootstrap import Bootstrap
from flask.ext.moment import Moment
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required
from main import tk_quote

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'

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
    return render_template('index.html')

class NameForm(Form):
    name   = StringField('Ticket, (e.g., AAPL, FB, YHOO)', validators=[Required()])
    submit = SubmitField('Submit')

@app.route('/pricer', methods=['GET', 'POST'])
def pricer():
    form = NameForm()
    if form.validate_on_submit():
        name = form.name.data.upper()
        price = tk_quote.stock_query(name)
        if(price != None):
            session['price'] = price 
            session['name']  = name
            form.name.data = ''
        else:
            flash('Wrong ticket!')
            session['name'] = None
            session['price'] = None
            form.name.data = ''
        return redirect(url_for('pricer'))
    return render_template('pricer.html', form=form, ticket=session.get('name'), price=session.get('price'))

if __name__ == '__main__':
    manager.run()
