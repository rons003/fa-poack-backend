import datetime
from flask import json, jsonify, make_response, request

import pymssql


def get_payment_group():
    conn = sap_connection_db()
    query = f"""SELECT PymntGroup [PaymentTerm], LEFT(PymntGroup, 3) [CountTerm] FROM OCTG"""
    cursor = conn.cursor()
    cursor.execute(query)
    payment_groups = []
    for row in cursor:
        payment_groups.append({
            "PaymentTerm": row["PaymentTerm"],
            "CountTerm": row["CountTerm"]
        })
    conn.close()
    return payment_groups


def get_dps():
    conn = sap_connection_db()
    card_code = request.args.get('code', '')
    query = f"""
        SELECT
            A.ReceiptNum,
            A.DocEntry, 
            A.CardCode, 
            A.CardName, 
            A.DocDate,
            A.DpmAmnt,  
            A.DpmAppl, 
            (A.DpmAmnt - A.DpmAppl) [DPBalance] 
        FROM 
            ODPO A 
        WHERE 
            A.CardCode = '{card_code}'
        AND 
            ISNULL(A.ReceiptNum,'') <> ''
        AND 
            (A.DpmAmnt - A.DpmAppl) > 0
        ORDER BY 1"""
    cursor = conn.cursor()
    cursor.execute(query)
    dps = []
    for row in cursor:
        dps.append({
            "ReceiptNum": row["ReceiptNum"],
            "DocEntry": row["DocEntry"],
            "CardCode": row["CardCode"],
            "CardName": row["CardName"],
            "DocDate": row["DocDate"],
            "DpmAmnt": row["DpmAmnt"],
            "DpmAppl": row["DpmAppl"],
            "DPBalance": row["DPBalance"]
            
        })
    conn.close()
    return dps


def sap_connection_db():
    conn = pymssql.connect(
        server='SCCSVRSAP',
        user='sa',
        password='Sb1@SCC',
        database='DESIHOFC_TEST',
        as_dict=True,
        tds_version='7.0'
    )
    return conn
