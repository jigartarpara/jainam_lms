from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
import frappe 

def setup_custom_fields():
	custom_fields = {
		"LMS Quiz Submission": [
            dict(fieldname='attempt',
                label='Attempt',
                fieldtype='Data',
                insert_after='passing_percentage'
            ),
		],
		"User": [
            dict(fieldname='department',
                label='Department',
                fieldtype='Link',
				options = 'Department',
                insert_after='country'
            ),
			dict(fieldname='division_1',
                label='Division 1',
                fieldtype='Link',
				options = 'LMS Division',
                insert_after='department'
            ),
			dict(fieldname='division_2',
                label='Division 2',
                fieldtype='Link',
				options = 'LMS Division',
                insert_after='division_1'
            ),
			dict(fieldname='division_3',
                label='Division 3',
                fieldtype='Link',
				options = 'LMS Division',
                insert_after='division_2'
            ),
		]
	}
	try:
		create_custom_fields(custom_fields)
	except:
		print("Exception while createing customfield")
		frappe.error_log()
		