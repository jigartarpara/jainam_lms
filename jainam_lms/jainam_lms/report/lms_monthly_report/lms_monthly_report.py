# Copyright (c) 2024, Jigar Tarpara and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
	columns = get_columns()
	data = get_data()
	return columns, data

def get_columns():
	return [
        {
            'fieldname': 'date_taken',
            'label': _('Date Taken'),
            'fieldtype': 'Date',
        },
        {
            'fieldname': 'department',
            'label': _('Department'),
            'fieldtype': 'Link',
            'options': 'Department'
        },
        {
            'fieldname': 'candidate_name',
            'label': _('Candidate Name'),
            'fieldtype': 'Data',
        },
		{
            'fieldname': 'mail_id',
            'label': _('Candidate Mail Id'),
            'fieldtype': 'Data',
        },
		{
            'fieldname': 'course',
            'label': _('Course'),
            'fieldtype': 'Link',
            'options': 'LMS Course'
        },
		{
            'fieldname': 'instructor',
            'label': _('Instructor'),
            'fieldtype': 'Data',
        },
		{
            'fieldname': 'quiz',
            'label': _('Quiz'),
            'fieldtype': 'Link',
            'options': 'LMS Quiz'
        },
		{
            'fieldname': 'total_questions',
            'label': _('Total Questions'),
            'fieldtype': 'Data',
        },
		{
            'fieldname': 'average_score',
            'label': _('Average Score'),
            'fieldtype': 'Data',
        },
		{
            'fieldname': 'total_score',
            'label': _('Total Score'),
            'fieldtype': 'Data',
        },
		{
            'fieldname': 'percentage',
            'label': _('Percentage'),
            'fieldtype': 'Data',
        },
		{
            'fieldname': 'no_of_attempt',
            'label': _('No of Attempt'),
            'fieldtype': 'Data',
        },
		{
            'fieldname': 'result',
            'label': _('Result'),
            'fieldtype': 'Data',
        },
    ]

def get_data():
	data = []
	quiz_submissions = frappe.get_all(
		"LMS Quiz Submission", 
		["name", "creation", "quiz", "course",  "member", "member_name", "score", "attempt", "percentage", "passing_percentage"]
	)
	average_score = frappe.db.sql("select quiz, avg(score) as score from `tabLMS Quiz Submission` group by quiz", as_dict=True)
	average_socre_array = {}
	for row in average_score:
		average_socre_array[row.quiz] = row.score
	
	no_of_attempt = frappe.db.sql("select quiz, avg(score) as score from `tabLMS Quiz Submission` group by quiz", as_dict=True)
	average_socre_array = {}
	for row in average_score:
		average_socre_array[row.quiz] = row.score
	
	for row in quiz_submissions:
		quiz = frappe.get_cached_doc("LMS Quiz", row.quiz)
		total_questions = len(quiz.questions)
		instructor = ""
		if quiz.course:
			course = frappe.get_cached_doc("LMS Course", quiz.course)
			for instructor_row in course.instructors:
				instructor += instructor_row.instructor
		data.append({
			"quiz": row.quiz,
			"date_taken": row.creation,
			"candidate_name": row.member_name,
			"mail_id": frappe.db.get_value("User", row.member, "email"),
			"total_questions": total_questions,
			"average_score": average_socre_array[row.quiz],
			"total_score": row.score,
			"percentage": row.percentage,
			"no_of_attempt": row.attempt,
			"result": "Pass" if row.percentage >= row.passing_percentage else "Fail",
			"course": quiz.course,
			"instructor": instructor,
			"department": frappe.db.get_value("User", row.member, "department")
		})
	return data