from flask import session
from flask_restful import Resource


class TestReport(Resource):

    def get(self, model_id):

        ccr = session.get("ccr")
        return {"model ccr": ccr}
