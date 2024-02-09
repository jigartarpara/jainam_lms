# Copyright (c) 2024, Jigar Tarpara and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import  flt
def execute(filters=None):
    filters = frappe._dict(filters or {})
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {
            'fieldname': 'batch_id',
            'label': _('Batch'),
            'fieldtype': 'Link',
            'options': 'LMS Batch'
        },
        {
            'fieldname': 'batch_date',
            'label': _('Batch Date'),
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
            'label': _('Quiz Attempt Status'),
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

def get_lms_batch_conditions(conditions, filters):
    return conditions

def get_quiz_submission_conditions(conditions, filters):
    return conditions

def get_data(filters):
    data = []
    
    average_socre_array = get_average_score()

    lms_batchs = frappe.get_all(
        "LMS Batch", 
        get_lms_batch_conditions({}, filters),
        ["name", "start_date", "end_date", "start_time", "end_time"]
    )
    
    for lms_batch in lms_batchs:
        batch = frappe.get_doc("LMS Batch", lms_batch['name'])
        for assement in batch.assessment:
            if assement.assessment_type == "LMS Quiz":
                if filters.quiz and filters.quiz != assement.assessment_name:
                    continue
                
                quiz = frappe.get_cached_doc("LMS Quiz", assement.assessment_name)
                
                total_questions = len(quiz.questions)

                for student in batch.students:
                    if filters.member and filters.member != student.student:
                        continue

                    quiz_submissions = frappe.get_all(
                        "LMS Quiz Submission",
                        get_quiz_submission_conditions({
                            "member": student.student,
                            "quiz": quiz.name
                        }, filters)
                        , 
                        [
                            "name", "creation", "quiz", "course",  
                            "member", "member_name", "score", 
                            "attempt", "percentage", "passing_percentage"
                        ]
                    )
                    
                    mail_id = frappe.db.get_value("User", student.student, "email")
                    department = frappe.db.get_value("User", student.student, "department")
                    candidate_name = frappe.db.get_value("User", student.student, "full_name")
                    
                    for row in quiz_submissions:
                        report_data = {
                            "submission_id": row.name,
                            "batch_id": batch.name ,
                            "batch_date": batch.creation,
                            "quiz": quiz.name,
                            "date_taken": row.creation,
                            "candidate_name": candidate_name,
                            "mail_id": mail_id,
                            "total_questions": total_questions,
                            "average_score": average_socre_array.get(quiz.name),
                            "total_score": row.score,
                            "percentage": row.percentage,
                            "no_of_attempt": row.attempt,
                            "result": "Pass" if row.percentage >= row.passing_percentage else "Fail",
                            "course": quiz.course,
                            "department": department,
                            "submission": "Attempted"
                        }
                        if filters.submission_status:
                            if filters.submission_status == "Not Attempted":
                                continue
                        if filters.result:
                            if filters.result == "Fail" and row.percentage >= row.passing_percentage:
                                continue
                            if filters.result == "Pass" and flt(row.percentage) < flt(row.passing_percentage):
                                continue
                        data.append(report_data)
                    if not quiz_submissions:
                        report_data = {
                            "submission_id": "",
                            "batch_id": batch.name ,
                            "batch_date": batch.creation,
                            "quiz": quiz.name,
                            "date_taken": "",
                            "candidate_name": candidate_name,
                            "mail_id": mail_id,
                            "total_questions": total_questions,
                            "average_score": average_socre_array.get(quiz.name),
                            "total_score": "",
                            "percentage": "",
                            "no_of_attempt": "",
                            "result": "",
                            "course": quiz.course,
                            "department": department,
                            "submission": "Not Attempted"
                        }
                        need_skip_record = False
                        if filters.submission_status:
                            if filters.submission_status == "Attempted":
                                need_skip_record = True
                        if filters.result:
                            if filters.result == "Fail" :
                                pass
                                # need_skip_record = True
                            if filters.result == "Pass":
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