import frappe

def after_insert(doc, method):
    qs = frappe.db.get_all("LMS Quiz Submission", {"quiz": doc.quiz, "member": doc.member, })
    count = len(qs)
    print(count)
    frappe.db.set_value("LMS Quiz Submission", doc.name, "attempt", count, False)