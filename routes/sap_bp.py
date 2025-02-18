from flask import Blueprint
from controllers.sap_controller import get_payment_group
from controllers.sap_controller import get_dps

sap_bp = Blueprint('sap_bp', __name__)
sap_bp.route('/payment-groups', methods=['GET'])(get_payment_group)
sap_bp.route('/downpayments', methods=['GET'])(get_dps)
