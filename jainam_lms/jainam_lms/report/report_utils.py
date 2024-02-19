import frappe

def get_submission_details(course, member, quiz):
    
    data = {
        "enrollment_id": "",
        "enrollment_creation": "",
        "enrollment_progress": "",
        "batch_start_date": "",
        "batch_id": "",
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
            batch.name, batch.start_date, batch.creation,student_table.confirmation_email_sent 
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
    
    return data