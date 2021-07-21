""" write to a SQLite database with forms, templates
    add new record, delete a record, edit/update a record
    """

from flask import Flask, render_template, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap

from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, RadioField, HiddenField, StringField, IntegerField, FloatField
from wtforms.validators import InputRequired, Length, Regexp, NumberRange
from datetime import date

app = Flask(__name__)
app.config['SECRET_KEY'] = 'MLXH243GssUWwKdTWS7FDhdwYF56wPj8'
Bootstrap(app)
db_name ='DBTEST.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_name
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

class Issue(db.Model):
    __tablename__ = 'TABLE1'
    ID = db.Column(db.Integer, primary_key=True)
    Title = db.Column(db.String)
    style = db.Column(db.String)
    Desc = db.Column(db.String)
    updated = db.Column(db.String)

    def __init__(self, Title, style, Desc, updated):
        self.Title = Title
        self.style = style
        self.Desc = Desc
        self.updated = updated

class AddRecord(FlaskForm):
    # ID used only by update/edit
    id_field = HiddenField()
    Title = StringField('Title:', [ InputRequired(),
        Length(min=3, message="Invalidlength")
        ])
    style = SelectField('Which area does the discrepancy impact', [ InputRequired()],
        choices=[ ('', ''), ('PLC', 'PLC'),
        ('Software', 'Software'),('HMI', 'HMI')])
    Desc = StringField('Describe the error', [ InputRequired(),
        Length(min=3, message="Invalidlength")
        ])
    # updated - date - handled in the route
    updated = HiddenField()
    submit = SubmitField('Add/Update Record')

# small form
class DeleteForm(FlaskForm):
    id_field = HiddenField()
    purpose = HiddenField()
    submit = SubmitField('Delete This discrepancy')

# +++++++++++++++++++++++
# get local date - does not account for time zone
# note: date was imported at top of script
def stringdate():
    today = date.today()
    date_list = str(today).split('-')
    # build string in format 01-01-2000
    date_string = date_list[1] + "-" + date_list[2] + "-" + date_list[0]
    return date_string

# +++++++++++++++++++++++
# routes

@app.route('/')
def index():
    # get a list of unique values in the style column
    styles = Issue.query.with_entities(Issue.style).distinct()
    return render_template('index.html', styles=styles)

@app.route('/inventory/<style>')
def inventory(style):
    errs = Issue.query.filter_by(style=style).order_by(Issue.ID).all()
    return render_template('list.html', socks=errs, style=style)

@app.route('/add_record', methods=['GET', 'POST'])
def add_record():
    form1 = AddRecord()
    if form1.validate_on_submit():
        Title = request.form['Title']
        style = request.form['style']
        Desc = request.form['Desc']
        # get today's date from function, above all the routes
        updated = stringdate()
        # the data to be inserted into Issue model - the table, socks
        record = Issue(Title, style, Desc, updated)
        # Flask-SQLAlchemy magic adds record to database
        db.session.add(record)
        db.session.commit()
        # create a message to send to the template
        message = f"The data for {Title} has been submitted."
        return render_template('add_record.html', message=message)
    else:
        # show validaton errors
        # see https://pythonprogramming.net/flash-flask-tutorial/
        for field, errors in form1.errors.items():
            for error in errors:
                flash("Error in {}: {}".format(
                    getattr(form1, field).label.text,
                    error
                ), 'error')
        return render_template('add_record.html', form1=form1)

# select a record to edit or delete
@app.route('/select_record/<letters>')
def select_record(letters):
    a, b = list(letters)
    errs = Issue.query.filter(Issue.Title.between(a, b)).order_by(Issue.Title).all()
    return render_template('select_record.html', socks=errs)

# edit or delete - come here from form in /select_record
@app.route('/edit_or_delete', methods=['POST'])
def edit_or_delete():
    ID = request.form['ID']
    choice = request.form['choice']
    err = Issue.query.filter(Issue.ID == ID).first()
    # two forms in this template
    form1 = AddRecord()
    form2 = DeleteForm()
    return render_template('edit_or_delete.html', sock=err, form1=form1, form2=form2, choice=choice)

# result of delete - this function deletes the record
@app.route('/delete_result', methods=['POST'])
def delete_result():
    ID = request.form['id_field']
    purpose = request.form['purpose']
    err = Issue.query.filter(Issue.ID == ID).first()
    if purpose == 'delete':
        db.session.delete(err)
        db.session.commit()
        message = f"The discrepancy {Issue.Title} has been deleted from the database."
        return render_template('result.html', message=message)

# result of edit - this function updates the record
@app.route('/edit_result', methods=['POST'])
def edit_result():
    ID = request.form['id_field']
    # call up the record from the database
    err = Issue.query.filter(Issue.ID == ID).first()
    # update all values
    err.Title = request.form['Title']
    err.style = request.form['style']
    err.Desc = request.form['Desc']
    # get today's date from function, above all the routes
    err.updated = stringdate()

    form1 = AddRecord()
    if form1.validate_on_submit():
        # update database record
        db.session.commit()
        # create a message to send to the template
        message = f"The data for discrepancy {err.Title} has been updated."
        return render_template('result.html', message=message)
    else:
        err.ID = ID
        for field, errors in form1.errors.items():
            for error in errors:
                flash("Error in {}: {}".format(
                    getattr(form1, field).label.text,
                    error
                ), 'error')
        return render_template('edit_or_delete.html', form1=form1, sock=err, choice='edit')


# +++++++++++++++++++++++
# error routes
@app.errorhandler(404)
def page_not_found(e):
    return render_template('/error.html', pagetitle="404 Error - Page Not Found", pageheading="Page not found (Error 404)", error=e), 404

@app.errorhandler(405)
def form_not_posted(e):
    return render_template('/error.html', pagetitle="405 Error - Form Not Submitted", pageheading="The form was not submitted (Error 405)", error=e), 405

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('/error.html', pagetitle="500 Error - Internal Server Error", pageheading="Internal server error (500)", error=e), 500

# +++++++++++++++++++++++

if __name__ == '__main__':
    app.run(debug=True)
