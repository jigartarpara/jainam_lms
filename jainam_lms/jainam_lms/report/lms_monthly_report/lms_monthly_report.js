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
			fieldname: "member",
			label: __("Member"),
			fieldtype: "Link",
			options: "User",
		},
		{
			fieldname: "submission_status",
			label: __("Attempt Status"),
			fieldtype: "Select",
			options: "\nAttempted\nNot Attempted",
		},
		{
			fieldname: "result",
			label: __("Result"),
			fieldtype: "Select",
			options: "\nPass\nFail",
		},
		{
			fieldname: "batch_start_date",
			label: __("Batch Start Date"),
			fieldtype: "DateRange",
		},
		{
			fieldname: "batch_creation_date",
			label: __("Batch Creation Date"),
			fieldtype: "DateRange",
		},
	]
};
