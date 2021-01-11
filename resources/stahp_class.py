from flask_restful import Resource, reqparse
from flask import jsonify, request
from stahp import *
class AHP(Resource):

    def get(self):
        return {"message" : "Welcome to UG Tourence"}

    def post(self):
        layers = request.json['layers']
        result, consistent = stahp2(layers)
        return {"recommendation":result, "consistentcy":consistent}