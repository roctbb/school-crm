from flask import Blueprint

health_blueprint = Blueprint('health', __name__)


@health_blueprint.route('/', methods=['GET'])
def status():
    return {"status": "OK"}
