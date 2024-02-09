import frappe
import datetime


def all():
    batches = get_all_lms_batch_for_mail_reminder()
    for batch in batches:
        batch_doc = frappe.get_doc(
            "LMS Batch",
            batch["name"],
        )
        for row in batch_doc.students:
            try:
                frappe.sendmail(
                    recipients=[row.student],
                    sender=None,
                    subject=frappe.render_template(batch_doc.custom_email_subject, { "doc": batch_doc}),
                    message=frappe.render_template(batch_doc.custom_mail_content, { "doc": batch_doc}),
                    delayed=False,
                )
                batch_doc.custom_alert_sent = True
                batch_doc.ignore_permission = True
                batch_doc.save()
            except:
                frappe.log_error()


def get_all_lms_batch_for_mail_reminder():
    reminder_before = datetime.datetime.strptime(
        str(
            frappe.db.get_single_value(
                "Jainam LMS Setup",
                "batch_reminder_mail_before",
            )
        ),
        "%H:%M:%S",
    )

    reminder_before_dt = datetime.datetime.now() + datetime.timedelta(
        hours=reminder_before.hour,
        minutes=reminder_before.minute,
        seconds=reminder_before.second,
    )
    batches = frappe.get_all(
        "LMS Batch",
        {
            "custom_alert_sent": False,
            "start_date" : datetime.datetime.now(),
            "scheduled_time": ["<", reminder_before],
        },
    )
    return batches
