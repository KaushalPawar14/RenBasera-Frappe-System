import frappe


"""This API performs the following tasks

-> Move Dispatch Challan From Pending Security Veify  to Dispatched
-> Create Entry in Vehicle Log 
-> Enter Data in Bothe Vehicle Log and Security Check
"""
@frappe.whitelist()
def get_greeting(challanRef:str):
    return challanRef
