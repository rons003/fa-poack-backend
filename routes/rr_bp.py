from flask import Blueprint
from controllers.receiving_report_controller import index, suppliers, receiving_report, companies

rr_bp = Blueprint('rr_bp', __name__)
rr_bp.route('/', methods=['GET'])(index)
rr_bp.route('/suppliers', methods=['GET'])(suppliers)
rr_bp.route('/receiving-report/<int:id>', methods=['GET'])(receiving_report)
rr_bp.route('/companies', methods=['GET'])(companies)