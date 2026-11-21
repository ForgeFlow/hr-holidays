# Copyright 2023 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class HrEmployeePublic(models.Model):
    _inherit = "hr.employee.public"

    hr_leave_summary_type = fields.Selection(
        selection=[("no", "No"), ("daily", "Daily"), ("weekly", "Weekly")],
        string="Leave Summary Email",
        compute="_compute_hr_leave_summary_type",
    )

    def _compute_hr_leave_summary_type(self):
        self._compute_from_employee("hr_leave_summary_type")
