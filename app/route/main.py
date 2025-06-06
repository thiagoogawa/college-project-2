from flask import Blueprint, render_template

main_route = Blueprint('main', __name__)

@main_route.route('/')
def index():
    return render_template('landingpage.html')

@main_route.route('/sobre_nos', methods=['GET'])
def about():
    return render_template('sobrenoslanding.html')
