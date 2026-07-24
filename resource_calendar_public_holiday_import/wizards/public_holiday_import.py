# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from datetime import datetime, time

from pytz import timezone, utc

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class PublicHolidayImport(models.TransientModel):
    _name = "public.holiday.import"
    _description = "Import Public Holidays"

    country_id = fields.Many2one("res.country", required=True)
    year = fields.Integer(
        required=True, default=lambda self: fields.Date.context_today(self).year
    )
    provider = fields.Selection(selection="_selection_provider")
    subdivision_code = fields.Char(
        string="Subdivision",
        help="ISO 3166-2 code (e.g. ES-CT) to import only this region's "
        "holidays. Leave empty to import the whole country.",
    )

    @api.model
    def _selection_provider(self):
        return []

    def _fetch_holidays(self):
        self.ensure_one()
        if not self.provider:
            raise UserError(_("Please select a provider."))
        return getattr(self, "_fetch_%s_holidays" % self.provider)()

    def _filter_by_subdivision(self, holidays):
        code = (self.subdivision_code or "").strip().upper()
        if not code:
            return holidays
        available = {s for h in holidays for s in h["subdivisions"]}
        if code not in available:
            raise UserError(
                _("No holidays found for subdivision '%s'. Check the ISO 3166-2 code.")
                % code
            )
        return [h for h in holidays if h["national"] or code in h["subdivisions"]]

    def _get_leave_datetimes(self, holiday_date):
        tz = timezone(self.env.company.resource_calendar_id.tz or "UTC")
        date_from = tz.localize(datetime.combine(holiday_date, time.min))
        date_to = tz.localize(datetime.combine(holiday_date, time.max))
        return (
            date_from.astimezone(utc).replace(tzinfo=None),
            date_to.astimezone(utc).replace(tzinfo=None),
        )

    def _create_leaves(self, holidays):
        leaves = self.env["resource.calendar.leaves"]
        count = 0
        for holiday in holidays:
            name = holiday["name"]
            if not holiday.get("national") and holiday.get("subdivisions"):
                name = "%s [%s]" % (name, ", ".join(holiday["subdivisions"]))
            date_from, date_to = self._get_leave_datetimes(holiday["date"])
            if leaves.search_count(
                [
                    ("resource_id", "=", False),
                    ("company_id", "=", self.env.company.id),
                    ("date_from", "<=", date_to),
                    ("date_to", ">=", date_from),
                ]
            ):
                continue
            leaves.create(
                {
                    "name": name,
                    "date_from": date_from,
                    "date_to": date_to,
                    "resource_id": False,
                    "calendar_id": False,
                    "time_type": "leave",
                }
            )
            count += 1
        return count

    def action_import(self):
        self.ensure_one()
        holidays = self._filter_by_subdivision(self._fetch_holidays())
        count = self._create_leaves(holidays)
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "type": "success",
                "message": _("%s public holidays imported.") % count,
                "next": {"type": "ir.actions.act_window_close"},
            },
        }
