from flask import Flask
from flask import request, make_response

def create_app():
    app = Flask(__name__)

    @app.route("/", methods=['GET', 'POST'])
    def post_message():
        if request.method == 'POST':
            response = make_response('', 200)
            return response
        elif request.method == 'GET':
            response = make_response('', 200)
            return response

    return app