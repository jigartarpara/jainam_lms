# Copyright (c) 2024, Jigar Tarpara and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
    filters = frappe._dict(filters or {})
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {
            'fieldname': 'enrollment_id',
            'label': _('Enrollment'),
            'fieldtype': 'Link',
            'options': 'LMS Enrollment'
        },
        {
            'fieldname': 'enrollment_date',
            'label': _('Enrollment Date'),
            'fieldtype': 'Date',
        },
        {
            'fieldname': 'candidate_name',
            'label': _('Candidate Name'),
            'fieldtype': 'Data',
            'width': 200
        },
        {
            'fieldname': 'department',
            'label': _('Department'),
            'fieldtype': 'Link',
            'options': 'Department',
            'width': 200
        },
        
        {
            'fieldname': 'mail_id',
            'label': _('Candidate Mail Id'),
            'fieldtype': 'Data',
            'width': 200
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
            'fieldname': 'submission',
            'label': _('Quiz Submission Status'),
            'fieldtype': 'Data',
        },
        {
            'fieldname': 'submission_id',
            'label': _('Quiz Submission ID'),
            'fieldtype': 'Link',
            'options': 'LMS Quiz Submission'
        },
        {
            'fieldname': 'date_taken',
            'label': _('Quiz Submission Date'),
            'fieldtype': 'Date',
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
        }
    ]
def get_quiz_conditions(conditions, filters):
    if filters.quiz:
        conditions['name'] = filters.quiz
    return conditions

def get_enrollment_conditions(conditions, filters):
    if filters.course:
        conditions['course'] = filters.course
    if filters.member:
        conditions['member'] =  filters.member
    return conditions

def get_quiz_submission_conditions(conditions, filters):
    return conditions

def get_data(filters):
    data = []
    
    average_socre_array = get_average_score()

    lms_enrollment = frappe.get_all(
        "LMS Enrollment", 
        get_enrollment_conditions({}, filters),
        ["name", "course", "member", "member_type", "creation"]
    )
    
    for enrollment in lms_enrollment:
        lms_quiz = frappe.get_all(
            "LMS Quiz",
            get_quiz_conditions(
            {
                "course": enrollment.course,
            },filters) ,
            ["name"]
        )
        for quiz in lms_quiz:
            quiz = frappe.get_cached_doc("LMS Quiz", quiz.name)
            total_questions = len(quiz.questions)
            instructor = ""

            valid_course = True
            if filters.instructor:
                valid_course = False
            if quiz.course:
                course = frappe.get_cached_doc("LMS Course", quiz.course)
                for instructor_row in course.instructors:
                    instructor += instructor_row.instructor
                    if instructor_row.instructor == filters.instructor:
                        valid_course = True
            if not valid_course:
                continue

            
            quiz_submissions = frappe.get_all(
                "LMS Quiz Submission",
                get_quiz_submission_conditions({
                    "course": enrollment.course,
                    "member": enrollment.member,
                    "quiz": quiz.name
                }, filters)
                , 
                [
                    "name", "creation", "quiz", "course",  
                    "member", "member_name", "score", 
                    "attempt", "percentage", "passing_percentage"
                ]
            )
            
            mail_id = frappe.db.get_value("User", enrollment.member, "email")
            department = frappe.db.get_value("User", enrollment.member, "department")
            candidate_name = frappe.db.get_value("User", enrollment.member, "full_name")
            
            for row in quiz_submissions:
                report_data = {
                    "submission_id": row.name,
                    "enrollment_id": enrollment.name ,
                    "enrollment_date": enrollment.creation,
                    "quiz": quiz.name,
                    "date_taken": row.creation,
                    "candidate_name": candidate_name,
                    "mail_id": mail_id,
                    "total_questions": total_questions,
                    "average_score": average_socre_array[quiz.name],
                    "total_score": row.score,
                    "percentage": row.percentage,
                    "no_of_attempt": row.attempt,
                    "result": "Pass" if row.percentage >= row.passing_percentage else "Fail",
                    "course": quiz.course,
                    "instructor": instructor,
                    "department": department,
                    "submission": "Submitted"
                }
                if not (filters.submission_status == "Submitted" or not filters.submission_status):
                    continue
                if not ((filters.result == "Pass" and row.percentage >= row.passing_percentage) or not filters.result):
                    continue
                if not ((filters.result == "Fail" and not row.percentage >= row.passing_percentage) or not filters.result):
                    continue
                data.append(report_data)
            if not quiz_submissions:
                report_data = {
                    "submission_id": "",
                    "enrollment_id": enrollment.name ,
                    "enrollment_date": enrollment.creation,
                    "quiz": quiz.name,
                    "date_taken": "",
                    "candidate_name": candidate_name,
                    "mail_id": mail_id,
                    "total_questions": total_questions,
                    "average_score": average_socre_array[quiz.name],
                    "total_score": "",
                    "percentage": "",
                    "no_of_attempt": "",
                    "result": "",
                    "course": quiz.course,
                    "instructor": instructor,
                    "department": department,
                    "submission": "Not Submitted"
                }
                need_skip_record = False
                if not (filters.submission_status == "Not Submitted" or not filters.submission_status):
                    need_skip_record = True
                if not need_skip_record:
                    data.append(report_data)
    return data

def get_average_score():
    average_score = frappe.db.sql("""
        select 
            quiz, avg(score) as score 
        from 
            `tabLMS Quiz Submission` 
        group by quiz
    """, as_dict=True)
    
    average_socre_array = {}
    for row in average_score:
        average_socre_array[row.quiz] = row.score
    
    return average_socre_array