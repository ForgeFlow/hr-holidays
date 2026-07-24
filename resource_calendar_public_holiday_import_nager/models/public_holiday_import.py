# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import requests

from odoo import _, api, fields, models
from odoo.exceptions import UserError

NAGER_URL = "https://date.nager.at/api/v3/PublicHolidays/%s/%s"


class PublicHolidayImport(models.TransientModel):
    _inherit = "public.holiday.import"

    @api.model
    def _selection_provider(self):
        return super()._selection_provider() + [("nager", "Nager.Date")]

    def _fetch_nager_holidays(self):
        self.ensure_one()
        try:
            response = requests.get(
                NAGER_URL % (self.year, self.country_id.code), timeout=30
            )
            response.raise_for_status()
        except requests.RequestException as error:
            raise UserError(
                _("Could not reach the Nager.Date API: %s") % error
            ) from error
        holidays = []
        for item in response.json():
            holidays.append(
                {
                    "date": fields.Date.to_date(item["date"]),
                    "name": item["localName"],
                    "national": item.get("global"),
                    "subdivisions": item.get("counties") or [],
                }
            )
        return holidays
