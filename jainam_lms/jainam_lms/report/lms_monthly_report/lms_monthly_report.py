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
            'fieldname': 'submission',
            'label': _('Submission Status'),
            'fieldtype': 'Data',
        },
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

def get_data():
    data = []
    
    average_socre_array = get_average_score()

    lms_enrollment = frappe.get_all(
        "LMS Enrollment", 
        ["name", "course", "member", "member_type"]
    )
    
    for enrollment in lms_enrollment:
        lms_quiz = frappe.get_all(
            "LMS Quiz",
            {
                "course": enrollment.course
            } ,
            ["name"]
        )
        for quiz in lms_quiz:   
            
            quiz = frappe.get_cached_doc("LMS Quiz", quiz.name)
            total_questions = len(quiz.questions)
            instructor = ""
            if quiz.course:
                course = frappe.get_cached_doc("LMS Course", quiz.course)
                for instructor_row in course.instructors:
                    instructor += instructor_row.instructor
            
            quiz_submissions = frappe.get_all(
                "LMS Quiz Submission",
                {
                    "course": enrollment.course,
                    "member": enrollment.member,
                    "quiz": quiz.name
                }
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
                data.append(report_data)
            else:
                report_data = {
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
                data.append(report_data)
    print(data)
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