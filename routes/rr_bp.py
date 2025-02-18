from flask import Blueprint
from controllers.receiving_report_controller import suppliers, receiving_report, details, companies, apsupports

rr_bp = Blueprint('rr_bp', __name__)
rr_bp.route('/suppliers', methods=['GET'])(suppliers)
rr_bp.route('/receiving-report/<int:id>', methods=['GET'])(receiving_report)
rr_bp.route('/receiving-report-details/<int:id>', methods=['GET'])(details)
rr_bp.route('/companies', methods=['GET'])(companies)
rr_bp.route('/apsupports', methods=['GET'])(apsupports)