// Copyright (c) 2024, Jigar Tarpara and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["LMS Monthly Report V2"] = {
	"filters": [
		{
			fieldname: "quiz_submissions_creation",
			label: __("Quiz Submission Creation"),
			fieldtype: "DateRange",
		}
	]
};
