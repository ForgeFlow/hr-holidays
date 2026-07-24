# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import requests

from odoo import _, api, fields, models
from odoo.exceptions import UserError

CALENDARIFIC_URL = "https://calendarific.com/api/v2/holidays"


class PublicHolidayImport(models.TransientModel):
    _inherit = "public.holiday.import"

    @api.model
    def _selection_provider(self):
        return super()._selection_provider() + [("calendarific", "Calendarific")]

    def _fetch_calendarific_holidays(self):
        self.ensure_one()
        api_key = (
            self.env["ir.config_parameter"].sudo().get_param("calendarific.api_key")
        )
        if not api_key:
            raise UserError(
                _(
                    "Set your Calendarific API key in Settings > Employees > "
                    "Public Holidays Import."
                )
            )
        params = {
            "api_key": api_key,
            "country": self.country_id.code,
            "year": self.year,
            "type": "national,local",
        }
        try:
            response = requests.get(CALENDARIFIC_URL, params=params, timeout=30)
            response.raise_for_status()
        except requests.RequestException as error:
            raise UserError(
                _("Could not reach the Calendarific API: %s") % error
            ) from error
        data = response.json()
        if data.get("meta", {}).get("code") != 200:
            raise UserError(_("Calendarific API error: %s") % data.get("meta"))
        holidays = []
        for item in data["response"]["holidays"]:
            states = item.get("states")
            if isinstance(states, list):
                national = False
                subdivisions = [s.get("iso", "").upper() for s in states]
            else:
                national = True
                subdivisions = []
            holidays.append(
                {
                    "date": fields.Date.to_date(item["date"]["iso"][:10]),
                    "name": item["name"],
                    "national": national,
                    "subdivisions": subdivisions,
                }
            )
        return holidays
