import frappe
import datetime
from frappe import _

def check_valid_date_for_student(batch):
    batchdoc = frappe.get_doc("LMS Batch", batch)
    for student in batchdoc.students:
        if student.student == frappe.session.user:
            if batchdoc.start_date  == datetime.datetime.now():
                if datetime.datetime.now() < batchdoc.start_time or datetime.datetime.now() > batchdoc.end_time : 
                    raise frappe.PermissionError(_("You don't have permission to access this page."))
            else:
                raise frappe.PermissionError(_("You don't have permission to access this page."))

def check_valid_date_for_student_course(course):
    pass
    
def get_submission_details(course, member, quiz):
    
    data = {
        "enrollment_id": "",
        "enrollment_creation": "",
        "enrollment_progress": "",
        "batch_start_date": "",
        "batch_id": "",
        "batch_medium": "",
        "batch_creation":"",
        "confirmation_email_sent": False
    }
    if course:
        enrollment = frappe.db.get_value("LMS Enrollment", {"course": course, "member":member}, ["name", "creation", "progress"])
        if enrollment:
            data['enrollment_id'] = enrollment[0]
            data['enrollment_creation'] = enrollment[1]
            data['enrollment_progress'] = enrollment[2]
    batch_data = frappe.db.sql("""
        select 
            batch.name, batch.start_date, batch.medium, batch.creation,student_table.confirmation_email_sent 
        from 
            `tabLMS Batch` as batch,
            `tabLMS Assessment` as assement_table,
            `tabBatch Student` as student_table
        where
            batch.name = assement_table.parent
            and batch.name = student_table.parent
            and assement_table.assessment_type = "LMS Quiz"
            and assement_table.assessment_name = %s
            and student_table.student = %s
    """,(quiz,member), as_dict=True)
    if batch_data:
        data['batch_id'] = batch_data[0]['name']
        data['batch_start_date'] = batch_data[0]['start_date']
        data['batch_creation'] = batch_data[0]['creation']
        data['confirmation_email_sent'] = batch_data[0]['confirmation_email_sent']
        data['batch_medium'] = batch_data[0]['medium']
    
    return data