from flask_restful import Resource, reqparse
from flask import jsonify, request
from PulpConnector import *
class GetItenerary(Resource):

    def get(self):
        return {"message" : "Welcome to UG Tourence"}

    def post(self):
        city_id = request.json['city_id']
        result = generateItenerary(city_id)
        return {"itenarary":result}