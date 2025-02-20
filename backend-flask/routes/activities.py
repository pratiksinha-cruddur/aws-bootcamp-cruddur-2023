
#flask
from flask import request, g

#Decorators
from aws_xray_sdk.core import xray_recorder
from flask import current_app as app
from flask_cors import CORS, cross_origin
from lib.cognito_jwt_token import jwt_required
from lib.cors import init_cors

# Services
from services.home_activities import *
from services.notifications_activities import *
from services.create_activity import *
from services.search_activities import *
from services.show_activity import *
from services.create_reply import *

## Helpers
from lib.helpers import model_json

def load(app):
    def default_home_feed(e):
        # unauthenicatied request
        app.logger.debug(e)
        app.logger.debug("unauthenicated")
        data = HomeActivities.run()
        return data, 200

    @app.route("/api/activities/home", methods=['GET'])
    @xray_recorder.capture('activities-for-home')
    @jwt_required(on_error=default_home_feed)
    def data_home():
        data = HomeActivities.run(cognito_user_id=g.cognito_user_id)
        return data, 200

    @app.route("/api/activities/notifications", methods=['GET'])
    def data_notifications():
        data = NotificationsActivities.run()
        return data, 200

    @app.route("/api/activities/search", methods=['GET'])
    def data_search():
        term = request.args.get('term')
        model = SearchActivities.run(term)
        return model_json(model)

    @app.route("/api/activities", methods=['POST', 'OPTIONS'])
    @cross_origin()
    @jwt_required()
    def data_activities():
        message = request.json['message']
        ttl = request.json['ttl']
        model = CreateActivity.run(message, g.cognito_user_id, ttl)
        return model_json(model)

    

    @app.route("/api/activities/<string:activity_uuid>/reply", methods=['POST', 'OPTIONS'])
    @cross_origin()
    @jwt_required()
    def data_activities_reply(activity_uuid):
        message = request.json['message']
        model = CreateReply.run(message, g.cognito_user_id, activity_uuid)
        return model_json(model)
