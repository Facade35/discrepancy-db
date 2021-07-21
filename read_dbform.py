from os import replace
import sqlite3
from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField
from flask_sqlalchemy import SQLAlchemy
from wtforms.fields.core import SelectField

app = Flask(__name__)
Bootstrap(app)
db_name = 'DBTEST.db'
conn = sqlite3.connect(db_name, check_same_thread=False)
app.config['SECRET_KEY'] = 'sOmebiGseCretstrIng'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_name
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)
global c
c = conn.cursor()
class issue(db.Model):
    __tablename__ = 'TABLE1'
    ID = db.Column(db.Integer, primary_key=True)
    style = db.Column(db.String)
    Desc = db.Column(db.String)
err = issue.query.with_entities(issue.style).distinct()
err_list = []
for issue in err:
    err_list.append( (issue.style) )
class typeSelect(FlaskForm):
    select = SelectField( 'Choose an error type:',
      choices=err_list
      )
    submit = SubmitField('Submit')

@app.route('/')
def index():
    form=typeSelect()
    return render_template('/read_db/nindex.html', form=form, err_list=err_list)
@app.route('/err', methods=['POST'])
def err_detail():
    selType = request.form['select']
    spec_list = []
    spec_list = c.execute('select ID, Desc from TABLE1 where style = "'+selType+'"').fetchall()
    conn.commit()
    class specSelect(FlaskForm):
        spec = SelectField('Specific Error Selection:',
            choices = spec_list
        )
        submit2 = SubmitField("Submit")
    form = specSelect()
    return render_template('/read_db/sock.html', selType = selType, form = form, zz=spec_list)
@app.route('/err/disp', methods=['POST'])
def err_display():
    selType= request.form['spec']
    info = []
    i1= c.execute('select ID from TABLE1 where ID = '+selType).fetchone()
    i2 = c.execute('select style from TABLE1 where ID="'+selType+'"').fetchone()
    i3 = c.execute('select Desc from TABLE1 where ID="'+selType+'"').fetchone()
    conn.commit
    info.append(i1)
    info.append(i2)
    info.append(i3)
    return render_template('/read_db/display.html', selType = selType, info = info)
if __name__ == '__main__':
    app.run(debug=True)
    '''
    spec_list = issue.query.with_entities(issue.style).distinct()
    c.execute('select ID from TABLE1 where style="Software"').fetchall()
    v1 = c.execute('select ID from TABLE1 where style="'+selType+'"').fetchall()
    v2 = c.execute('select style from TABLE1 where style="'+selType+'"').fetchall()
    v3 = c.execute('select Desc from TABLE1 where style="'+selType+'"').fetchall()
    v1=v1,v2=v2,v3=v3
    '''