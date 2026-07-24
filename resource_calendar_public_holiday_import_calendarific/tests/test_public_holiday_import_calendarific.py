# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from unittest.mock import patch

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase

_MODULE = (
    "odoo.addons.resource_calendar_public_holiday_import_calendarific"
    ".models.public_holiday_import"
)


class TestPublicHolidayImportCalendarific(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.icp = cls.env["ir.config_parameter"].sudo()
        cls.icp.set_param("calendarific.api_key", "TESTKEY")
        cls.wizard = cls.env["public.holiday.import"].create(
            {
                "country_id": cls.env.ref("base.es").id,
                "year": 2099,
                "provider": "calendarific",
            }
        )

    def _response(self):
        return {
            "meta": {"code": 200},
            "response": {
                "holidays": [
                    {
                        "name": "New Year's Day",
                        "date": {"iso": "2099-01-01"},
                        "states": "All",
                    },
                    {
                        "name": "Day of Andalucia",
                        "date": {"iso": "2099-02-28"},
                        "states": [{"iso": "es-an", "name": "Andalusia"}],
                    },
                ]
            },
        }

    @patch("%s.requests.get" % _MODULE)
    def test_fetch_normalizes(self, mock_get):
        mock_get.return_value.raise_for_status.return_value = None
        mock_get.return_value.json.return_value = self._response()
        result = self.wizard._fetch_calendarific_holidays()
        self.assertEqual(len(result), 2)
        self.assertTrue(result[0]["national"])
        self.assertEqual(result[0]["subdivisions"], [])
        self.assertFalse(result[1]["national"])
        self.assertEqual(result[1]["subdivisions"], ["ES-AN"])

    def test_missing_api_key_raises(self):
        self.icp.set_param("calendarific.api_key", "")
        with self.assertRaises(UserError):
            self.wizard._fetch_calendarific_holidays()
