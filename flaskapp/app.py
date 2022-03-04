'''
Name: Jack Kingsbury
Date: 3/3/2022
Class: CMSC447-Mo/We: 230:345
Description: This flask app uses SQLalchemy to create a database and routes to add, delete, and edit users from a table.
'''
from flask import Flask, render_template, request, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from datetime import datetime
import os
import atexit
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String


#Creates the Flask instance
app = Flask(__name__)
SECRET_KEY = os.urandom(32)

#Add a database in
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ourdata.db'
app.config['SECRET_KEY'] = SECRET_KEY

#creating database

ourdb = SQLAlchemy(app)

#creates Table
engine = create_engine('sqlite:///ourdata.db', echo = True)
meta = MetaData()
users = Table(
    'users', meta, 
    Column('id', Integer, primary_key=True),
    Column('name', String),
    Column('points', String)

)
meta.create_all(engine)







#creating model
class Users(ourdb.Model):
    name = ourdb.Column(ourdb.String(100), nullable = False, unique = True)
    id = ourdb.Column(ourdb.Integer, primary_key = True)
    points = ourdb.Column(ourdb.Integer, primary_key = False)
    #date_added = ourdb.Column(ourdb.DateTime, default = datetime.utcnow)

    def __repr__(self):
        return '<Name %r>' % self.name

#creates forms
class UserForm(FlaskForm):
    name = StringField("Name: ", validators=[DataRequired()])
    id = StringField("ID: ", validators=[DataRequired()])
    points = StringField("Points: ",  validators=[DataRequired()])
    update = SubmitField("Update")
    delete = SubmitField("Delete")
    go_back = SubmitField("Go Back")

#route for adding users
@app.route('/add', methods = ['GET', 'POST'])
def add_info():
    form = UserForm()
    name = None
    if form.validate_on_submit():
        user = Users.query.filter_by(id = form.id.data).first()
        if user is None:
            user = Users(name = form.name.data, id = form.id.data, points = form.points.data)
            ourdb.session.add(user)
            ourdb.session.commit()
        name = form.name.data
        form.name.data = ''
        form.id.data = ''
        form.points.data = ''
    our_table = Users.query
        

    return render_template("add_info.html", form = form, name = name, our_table = our_table)

#route for updating users
@app.route('/update/<int:id>', methods = ['GET', 'POST'])
def update_info(id):
    form = UserForm()
    update_user = Users.query.get_or_404(id)

    if request.method == "POST":
        update_user.name = request.form['name']
        update_user.points = request.form['points']
        try:
            ourdb.session.commit()
            return render_template("update.html", form = form, update_user = update_user)
        except:
            flash("ERROR")
            return render_template("update.html", form = form, update_user = update_user)
    else:
        return render_template("update.html", form = form, update_user = update_user)


#route for deleting users
@app.route('/delete/<int:id>', methods =['GET', 'POST'])
def delete_info(id):
    if request.method == 'GET':
        delete_user = Users.query.get_or_404(id)
        ourdb.session.delete(delete_user)
        ourdb.session.commit()
        return redirect("/add")
    else:
        return redirect("/add")

#redirect to be used with the go_back button in html
@app.route('/goback', methods = ['GET', 'POST'])
def go_back():
    return redirect("/add")



#creates the initial table 
BASE_USERS = [Users(name = 'Steve Smith', id = '211', points = '80'), Users(name = 'Jian Wong', id = '122', points = '92'),Users(name = 'Chris Peterson', id = '213', points = '91'),
Users(name = 'Sai Patel', id = '524', points = '94'),Users(name = 'Andrew Whitehead', id = '425', points = '99'),Users(name = 'Lynn Roberts', id = '626', points = '90'),
Users(name = 'Robert Sanders', id = '287', points = '75')]

for user in BASE_USERS:
    check_user = Users.query.filter_by(id = Users.id)
    ourdb.session.add(user)
    ourdb.session.commit()

#deletes the database at exit, so we get a fresh one every time
def deletedatabase():
    ourdb.drop_all()

atexit.register(deletedatabase)


if __name__ == '__main__':
    app.run(debug=True)
    