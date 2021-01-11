from flask import Blueprint
from flask_restful import Api
from resources.stahp_class import AHP
from resources.itenerary import GetItenerary

api_bp = Blueprint('api',__name__)
api = Api(api_bp)

#route
api.add_resource(AHP,'/recommendation')
api.add_resource(GetItenerary,'/itenerary')