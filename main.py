from flask import Flask, json
from flask_cors import CORS

from flask_jwt_extended import JWTManager
from models.database import db
from routes.rr_bp import rr_bp
from routes.sap_bp import sap_bp

app = Flask(__name__)

cors = CORS(app, resources={r"/*": {"origins": "*"}})
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
jwt = JWTManager(app)

app.register_blueprint(rr_bp, url_prefix='/fa')
app.register_blueprint(sap_bp, url_prefix='/sap')

db.init_app(app)
