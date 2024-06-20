import frappe
from frappe.website.path_resolver import resolve_path as original_resolve_path


def resolve_path(path):
    if "iclock" in path:
        # Do something here with request object.
        request = frappe.local.request
        print("--->", path, request.method, request.query_string)
    return original_resolve_path(path)