# Copyright (c) 2024, Jigar Tarpara and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from jainam_lms.jainam_lms.report.report_utils import get_submission_details

def execute(filters=None):
    filters = frappe._dict(filters or {})
    columns = get_columns()
    data = get_data(filters)
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
            'options': 'Department',
            'width': 200
        },
        {
            'fieldname': 'candidate_name',
            'label': _('Candidate Name'),
            'fieldtype': 'Data',
            'width': 200
        },
        {
            'fieldname': 'mail_id',
            'label': _('Candidate Mail Id'),
            'fieldtype': 'Data',
            'width': 200
        },

        {
            'fieldname': 'enrollment_id',
            'label': _('LMS Enrollment'),
            'fieldtype': 'Link',
            'options': 'LMS Enrollment'
        },
        {
            'fieldname': 'enrollment_creation',
            'label': _('Enrollment Creation'),
            'fieldtype': 'Date',
        },
        {
            'fieldname': 'enrollment_progress',
            'label': _('Enrollment Progress'),
            'fieldtype': 'Data',
        },
        {
            'fieldname': 'confirmation_email_sent',
            'label': _('Confirmation Email Sent'),
            'fieldtype': 'Check',
        },
        {
            'fieldname': 'batch_start_date',
            'label': _('Batch Start Date'),
            'fieldtype': 'Date',
        },
        {
            'fieldname': 'batch_id',
            'label': _('LMS Batch'),
            'fieldtype': 'Link',
            'options': 'LMS Batch'
        },
        {
            'fieldname': 'batch_medium',
            'label': _('Medium'),
            'fieldtype': 'Data',
        },
        {
            'fieldname': 'batch_creation',
            'label': _('Batch Creation'),
            'fieldtype': 'Date',
        },

        {
            'fieldname': 'course',
            'label': _('Course'),
            'fieldtype': 'Link',
            'options': 'LMS Course',
            'width': 200
        },
        {
            'fieldname': 'instructor',
            'label': _('Instructor'),
            'fieldtype': 'Data',
            'width': 200
        },
        {
            'fieldname': 'quiz',
            'label': _('Quiz'),
            'fieldtype': 'Link',
            'options': 'LMS Quiz',
            'width': 200
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

def get_quiz_submission_conditions(conditions, filters):
    if filters.quiz_submissions_creation:
        conditions['creation'] =("between",[filters.quiz_submissions_creation[0], filters.quiz_submissions_creation[1]])
    return conditions

def get_data(filters):
    data = []
    quiz_submissions = frappe.get_all(
        "LMS Quiz Submission", 
        get_quiz_submission_conditions({}, filters),
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
        submission_data = get_submission_details(quiz.course, row.member, row.quiz)
        data.append({
            "quiz": row.quiz,
            "date_taken": row.creation,
            "candidate_name": row.member_name,
            "enrollment_id": submission_data.get('enrollment_id'),
            "enrollment_creation": submission_data.get('enrollment_creation'),
            "enrollment_progress": submission_data.get('enrollment_progress'),
            "batch_start_date": submission_data.get('batch_start_date'),
            "batch_id": submission_data.get('batch_id'),
            "batch_medium": submission_data.get('batch_medium'),
            "confirmation_email_sent": submission_data.get('confirmation_email_sent'),
            "batch_creation": submission_data.get('batch_creation'),
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




