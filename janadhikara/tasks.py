# Copyright (c) 2026, Jimreeves Samuel and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import getdate, nowdate


def _age(date_of_birth):
	dob = getdate(date_of_birth)
	today = getdate(nowdate())
	age = today.year - dob.year
	if (today.month, today.day) < (dob.month, dob.day):
		age -= 1
	return age


def _category(age, categories):
	for row in categories:
		if row.min_age is not None and row.max_age is not None and row.min_age <= age <= row.max_age:
			return row.category_name
	return ""


def update_family_member_ages():
	"""Daily: recalculate age and child/youth category for every Family Member with a date of birth.
	Same behaviour as janadhikara.tasks.update_family_member_ages in the V15 app (welfare-rights-blr)."""
	categories = frappe.get_all("Age Category", fields=["category_name", "min_age", "max_age"])
	members = frappe.get_all(
		"Family Member",
		filters={"date_of_birth": ["is", "set"]},
		fields=["name", "date_of_birth", "age", "child_youth"],
	)
	for m in members:
		new_age = _age(m.date_of_birth)
		new_cat = _category(new_age, categories)
		updates = {}
		if str(new_age) != str(m.age):
			updates["age"] = new_age
		if new_cat != (m.child_youth or ""):
			updates["child_youth"] = new_cat
		if updates:
			frappe.db.set_value("Family Member", m.name, updates, update_modified=False)
	frappe.db.commit()
