import frappe
import datetime
from frappe import _
from frappe.utils import today, get_timedelta, nowtime

def check_valid_date_for_student(batch):
    batchdoc = frappe.get_doc("LMS Batch", batch)
    for student in batchdoc.students:
        if student.student == frappe.session.user:
            if str(batchdoc.start_date)  == str(today()):
                currenttimedelta = get_timedelta(nowtime())
                if  currenttimedelta < batchdoc.start_time or currenttimedelta > batchdoc.end_time : 
                    raise frappe.PermissionError(_("Please Access this page beetween "+ str(batchdoc.start_time) + " to " + str(batchdoc.end_time)))
            else:
                raise frappe.PermissionError(_("Please Access this page beetween "+ str(batchdoc.start_date) + " to " +str(batchdoc.start_time) + " " + str(batchdoc.end_time)))

def check_valid_date_for_student_course(course):
    user = frappe.session.user
    batch_data = frappe.db.sql("""
        select 
            batch.name 
        from 
            `tabLMS Batch` as batch,
            `tabBatch Course` as batch_course,
            `tabBatch Student` as student_table
        where
            batch.name = batch_course.parent
            and batch.name = student_table.parent
            and student_table.student = %s
            and batch_course.course = %s
    """,(user,course), as_dict=True)
    if batch_data:
        batch_name = batch_data[0]['name']
        check_valid_date_for_student(batch_name)

    
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