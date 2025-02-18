from flask import jsonify, make_response
from flask import request
from models.database import db

database = "fadata"


def companies():
    result = []
    try:
        query = f"""SHOW databases LIKE 'desdeveloper%'"""
        cur = db.connection.cursor()
        cur.execute(query)
        rv = cur.fetchall()
        for row in rv:
            result.append({
                "company": row["Database (desdeveloper%)"]
            })
    except Exception as e:
        print(str(e))
    return make_response(jsonify(result), 200)


def suppliers():
    result = []
    try:
        company = request.args.get("company", None)
        database = company
        query = f"""
            SELECT 
                supplier_id,
                supp_name, 
                supp_ref, 
                SAPcode as sap_code
            FROM
                {database}.suppliers
            WHERE
                inactive = 0"""
        cur = db.connection.cursor()
        cur.execute(query)
        result = cur.fetchall()
        
    except Exception as e:
        print(str(e))
    return make_response(jsonify(result), 200)


def receiving_report(id):
    result = []
    try:
        company = request.args.get("company", None)
        filter = request.args.get("filter", False)
        database = company
        query = f"""
            SELECT 
                a.id AS trans_id,
                c.supp_name AS supp_name,
                c.supplier_id,
                (SELECT 
                    t1.reference
                FROM
                    {database}.purch_orders t1
                WHERE
                    t1.order_no = a.purch_order_no) as purch_order_ref,
                a.reference,
                a.delivery_date,
                a.suppl_ref_no,
                a.suppl_ref_date,
                a.suppl_served_by,
                a.grn_remarks,
                (SELECT 
                        t1.description
                    FROM
                        {database}.stock_category t1
                    WHERE
                        t1.category_id = a.category_id
                    AND
                        t1.inactive = 0
                    LIMIT 1) as category,
                a.apinvoice_no_and_poack_no as ap_no,
                CASE
                    WHEN SUM(b.qty_recd) > SUM(d.qty_invoiced) THEN 'Open'
                    ELSE 'Closed'
                END AS status,
                a.loc_code
            FROM
                {database}.grn_batch a
                    INNER JOIN
                {database}.grn_items b ON b.grn_batch_id = a.id
                    LEFT JOIN
                {database}.suppliers c ON c.supplier_id = a.supplier_id
                    LEFT JOIN
                {database}.purch_order_details d ON d.po_detail_item = b.po_detail_item
            WHERE
                a.supplier_id = {id}"""
        if filter:
            query += f""" AND (a.reference LIKE '%{filter}%') """
        query += " GROUP BY a.id "
        cur = db.connection.cursor()
        cur.execute(query)
        result = cur.fetchall()

    except Exception as e:
        print(str(e))
    return make_response(jsonify(result), 200)


def details(id):
    result = []
    try:
        company = request.args.get("company", None)
        database = company
        query = f"""
        SELECT 
            a.id,
            a.grn_batch_id,
            a.item_code,
            a.description,
            a.color_code,
            (a.qty_recd - b.qty_invoiced) AS quantity,
            b.std_cost_unit,
            c.category_id,
            (SELECT 
                t1.description
            FROM
                {database}.stock_category t1
            WHERE
                t1.category_id = c.category_id
            AND
                t1.inactive = 0
            LIMIT 1) as category,
            (SELECT 
                    t1.serialised
                FROM
                    {database}.stock_master t1
                WHERE
                    t1.stock_id = a.item_code) AS serialized,
            a.po_detail_item
        FROM
            {database}.grn_items a
                LEFT JOIN
            {database}.purch_order_details b ON b.po_detail_item = a.po_detail_item
                INNER JOIN
            {database}.grn_batch c ON c.id = a.grn_batch_id
        WHERE
            a.grn_batch_id = {id}
                AND (a.qty_recd - b.qty_invoiced) > 0"""
        cur = db.connection.cursor()
        cur.execute(query)
        rv = cur.fetchall()
        for row in rv:
            serials = []

            query = f"""
                SELECT
                    serialise_id,
                    serialise_lot_no,
                    serialise_chasis_no
                FROM
                    {database}.item_serialise
                WHERE
                    serialise_grn_items_id = {row["id"]}
                AND
                    invoice = 0"""
            cur = db.connection.cursor()
            cur.execute(query)
            serials = cur.fetchall()
            result.append({
                "id": row["id"],
                "grn_batch_id": row["grn_batch_id"],
                "item_code": row["item_code"],
                "description": row["description"],
                "color_code": row["color_code"],
                "quantity": row["quantity"],
                "selected_quantity": row["quantity"],
                "std_cost_unit": row["std_cost_unit"],
                "corrected_price": row["std_cost_unit"],
                "category_id": row["category_id"],
                "category": row["category"],
                "serialized": row["serialized"],
                "po_detail_item": row["po_detail_item"],
                "serials": serials
            })
    except Exception as e:
        print(str(e))
    return make_response(jsonify(result), 200)


def apsupports():
    result = []
    try:
        company = request.args.get("company", None)
        supplier = request.args.get("supplier_id", 0)
        category = request.args.get("category", '')
        database = company
        query = f"""
            SELECT DISTINCT
                a.ap_support_type,
                a.distribution,
                'APSUPPORT' AS item_code,
                ifnull(b.price, 0) as price
            FROM
                {database}.item_apsupport_type a
                    LEFT JOIN
                {database}.item_apsupport_price b ON a.id = b.apsupport_type_id
                    LEFT JOIN
                {database}.stock_category c ON c.category_id = b.category_id
            WHERE
                a.inactive = '0'
            ORDER BY 2"""
        cur = db.connection.cursor()
        cur.execute(query)
        result = cur.fetchall()
    except Exception as e:
        print(str(e))
    return make_response(jsonify(result), 200)
