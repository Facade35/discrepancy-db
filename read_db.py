import pymysql
from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField
from flask_sqlalchemy import SQLAlchemy
from wtforms.fields.core import SelectField

app = Flask(__name__)
Bootstrap(app)
db_name = 'DBTEST.db'
app.config['SECRET_KEY'] = 'sOmebiGseCretstrIng'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_name
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)
class issue(db.Model):
    __tablename__ = 'TABLE1'
    ID = db.Column(db.Integer, primary_key=True)
    style = db.Column(db.String)
    Desc = db.Column(db.String)




@app.route('/')
def index():
    styles = issue.query.with_entities(issue.style).distinct()
    return render_template('/read_db/index.html', style=styles)

@app.route('/list/<style>')
def list(style):
    try:
        issues = issue.query.filter_by(style=style).order_by(issue.ID).all()
        return render_template('read_db/list.html', issues=issues, styles=style)
    except Exception as e:
        error_text = "<p>The error:<br>" + str(e) + "</p>"
        hed = '<h1>Something is broken.</h1>'
        return hed + error_text

if __name__ == '__main__':
    app.run(debug=True)
