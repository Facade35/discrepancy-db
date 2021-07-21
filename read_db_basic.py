from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
db_name = 'DBTEST.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_name
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

class Model(db.Model):
    __tablename__ = 'TABLE1'
    ID = db.Column(db.Integer, primary_key=True)
    Type = db.Column(db.String)
    Desc = db.Column(db.String)
@app.route('/')
def index():
    try:
        Type = Model.query.filter_by(Type='software').order_by(Model.ID).all()
        dis_text = '<ul>'
        for disType in Type:
            dis_text += '<li>' + str(disType.ID) + ', ' + disType.Desc + '</li>'
        dis_text += '</ul>'
        return dis_text
    except Exception as e:
        error_text = "<p>The error:<br>" + str(e) + "</p>"
        hed = '<h1>Something is broken.</h1>'
        return hed + error_text
if __name__ == '__main__':
    app.run(debug=True)
