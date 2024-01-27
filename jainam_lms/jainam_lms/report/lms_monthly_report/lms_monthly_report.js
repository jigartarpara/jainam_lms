// Copyright (c) 2024, Jigar Tarpara and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["LMS Monthly Report"] = {
	"filters": [
		{
			fieldname: "quiz",
			label: __("Quiz"),
			fieldtype: "Link",
			options: "LMS Quiz",
		},
		{
			fieldname: "course",
			label: __("Course"),
			fieldtype: "Link",
			options: "LMS Course",
		},
		{
			fieldname: "member",
			label: __("Member"),
			fieldtype: "Link",
			options: "User",
		},
		{
			fieldname: "submission_status",
			label: __("Submission Status"),
			fieldtype: "Select",
			options: "\nSubmitted\nNot Submitted",
		},
		{
			fieldname: "instructor",
			label: __("Instructor"),
			fieldtype: "Link",
			options: "User",
		},
		{
			fieldname: "result",
			label: __("Result"),
			fieldtype: "Select",
			options: "\nPass\nFail",
		},
	]
};
