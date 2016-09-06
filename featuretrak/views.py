from flask import Flask, request, session, url_for, render_template
from database import create_app, db, User

app = create_app()

@app.route("/")
def hello():
    return "Hello World!"

@app.route('/tpl')
def tpl():
    return render_template('base.html')
