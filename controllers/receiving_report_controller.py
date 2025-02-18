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
                "company": row[0]
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
                SAPcode
            FROM
                {database}.suppliers
            WHERE
                inactive = 0"""
        cur = db.connection.cursor()
        cur.execute(query)
        rv = cur.fetchall()
        for row in rv:
            result.append({
                "supplier_id": row[0],
                "supp_name": row[1],
                "supp_ref": row[2],
                "sap_code": row[3],
            })
    except Exception as e:
        print(str(e))
    return make_response(jsonify(result), 200)


def index():
    result = []
    try:
        query = f"""
            SELECT 
                a.id AS trans_id,
                c.supp_name AS supplier_name,
                c.supplier_id,
                a.purch_order_no,
                a.reference,
                a.delivery_date,
                a.suppl_ref_no,
                a.suppl_ref_date,
                a.suppl_served_by,
                a.grn_remarks,
                a.category_id,
                ifnull(a.apinvoice_no_and_poack_no, '') as ap_no,
                CASE
                    WHEN SUM(b.qty_recd) > SUM(IFNULL(d.qty_invoiced, 0)) THEN 'Open'
                    ELSE 'Closed'
                END AS status
            FROM
                {database}.grn_batch a
                    INNER JOIN
                {database}.grn_items b ON b.grn_batch_id = a.id
                    LEFT JOIN
                {database}.suppliers c ON c.supplier_id = a.supplier_id
                    LEFT JOIN
                {database}.purch_order_details d ON d.po_detail_item = b.po_detail_item
            GROUP BY a.id"""
        cur = db.connection.cursor()
        cur.execute(query)
        rv = cur.fetchall()
        for row in rv:
            result.append({
                "trans_id": row[0],
                "supp_name": row[1],
                "supplier_id": row[2],
                "purch_order_no": row[3],
                "reference": row[4],
                "delivery_date": row[5],
                "suppl_ref_no": row[6],
                "suppl_ref_date": row[7],
                "suppl_served_by": row[8],
                "grn_remarks": row[9],
                "category_id": row[10],
                "ap_no": row[11],
                "status": row[12]
            })

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
                c.supp_name AS supplier_name,
                c.supplier_id,
                (SELECT 
                    t1.reference
                FROM
                    {database}.purch_orders t1
                WHERE
                    t1.order_no = a.purch_order_no),
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
                    LIMIT 1),
                a.apinvoice_no_and_poack_no,
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
        rv = cur.fetchall()
        for row in rv:
            result.append({
                "trans_id": row[0],
                "supp_name": row[1],
                "supplier_id": row[2],
                "purch_order_ref": row[3],
                "reference": row[4],
                "delivery_date": row[5],
                "suppl_ref_no": row[6],
                "suppl_ref_date": row[7],
                "suppl_served_by": row[8],
                "grn_remarks": row[9],
                "category": row[10],
                "ap_no": row[11],
                "status": row[12],
                "loc_code": row[13]
            })

    except Exception as e:
        print(str(e))
    return make_response(jsonify(result), 200)


def details(id):
    result = []
    try:
        query = """
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
                    t1.serialised
                FROM
                    stock_master t1
                WHERE
                    t1.stock_id = a.item_code) AS serialized,
            a.po_detail_item
        FROM
            grn_items a
                LEFT JOIN
            purch_order_details b ON b.po_detail_item = a.po_detail_item
                INNER JOIN
            grn_batch c ON c.id = a.grn_batch_id
        WHERE
            a.grn_batch_id = 78
                AND (a.qty_recd - b.qty_invoiced) > 0"""
    except Exception as e:
        print(str(e))
    return make_response(jsonify(result), 200)
