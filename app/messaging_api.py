# app/messaging_api.py

from flask import Flask
from flask import request, make_response
from multiprocessing import Value

def create_app():
    #Creating a variable shared across Flask processes
    message_id = Value('i', 0)
    app = Flask(__name__)

    @app.route("/", methods=['GET', 'POST'])
    def post_message():
        response = None
        if request.method == 'POST':
            if request.is_json:
                with message_id.get_lock():
                    response = make_response({'status': 200, 'message_id': message_id.value}, 200)
                    message_id.value +=1
            else:
                response = make_response({'status': 400}, 400)
        elif request.method == 'GET':
            response = make_response('', 200)
        
        return response

    return app
