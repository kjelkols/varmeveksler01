from flask import Blueprint, render_template

main = Blueprint('main', __name__)

@main.route('/')
def index():
    # Legg til logikk for å hente data og sende til template
    return render_template('index.html')
