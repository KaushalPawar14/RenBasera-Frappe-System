

import frappe
from frappe.auth import LoginManager
from frappe.utils.password import get_decrypted_password

@frappe.whitelist(allow_guest=True)
def login(usr, pwd):
    # 1. Explicitly check if the user exists
    if not frappe.db.exists("User", usr):
        frappe.throw("Invalid User or Password", frappe.exc.AuthenticationError)

    try:
        # 2. Authenticate using Frappe's built-in manager
        login_manager = LoginManager()
        login_manager.authenticate(user=usr, pwd=pwd)
        user = login_manager.user
        
    except Exception:
        frappe.throw("Invalid User or Password", frappe.exc.AuthenticationError)

    # 3. Get the user document
    user_doc = frappe.get_doc("User", user)

    # 4. Generate API Key and Secret if they do not exist
    if not user_doc.api_key or not user_doc.api_secret:
        api_secret = frappe.generate_hash(length=15)
        user_doc.api_key = frappe.generate_hash(length=15)
        user_doc.api_secret = api_secret
        user_doc.save(ignore_permissions=True)
        frappe.db.commit()
    else:
        # 5. Decrypt the existing secret
        api_secret = get_decrypted_password("User", user, "api_secret")

    # 6. Extract the user's roles into a simple array of strings
    user_roles = [role.role for role in user_doc.roles]

    # 7. Return the extended payload
    return {
        "LoggedIn": True,
        "api_key": user_doc.api_key,
        "api_secret": api_secret,
        "full_name": user_doc.full_name,
        "email": user_doc.email,
        "username": user_doc.username,
        "roles": user_roles,
        "user_image": user_doc.user_image # Helpful if you want an avatar in your Vue Navbar
    }