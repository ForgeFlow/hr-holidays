# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from unittest.mock import patch

from odoo.tests.common import TransactionCase

_MODULE = (
    "odoo.addons.resource_calendar_public_holiday_import_nager"
    ".models.public_holiday_import"
)


class TestPublicHolidayImportNager(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.wizard = cls.env["public.holiday.import"].create(
            {
                "country_id": cls.env.ref("base.es").id,
                "year": 2099,
                "provider": "nager",
            }
        )

    @patch("%s.requests.get" % _MODULE)
    def test_fetch_normalizes(self, mock_get):
        mock_get.return_value.raise_for_status.return_value = None
        mock_get.return_value.json.return_value = [
            {
                "date": "2099-01-01",
                "localName": "Cap d'Any",
                "name": "New Year's Day",
                "global": True,
                "counties": None,
            },
            {
                "date": "2099-06-24",
                "localName": "Sant Joan",
                "name": "St John",
                "global": False,
                "counties": ["ES-CT", "ES-VC"],
            },
        ]
        result = self.wizard._fetch_nager_holidays()
        self.assertEqual(len(result), 2)
        self.assertTrue(result[0]["national"])
        self.assertEqual(result[0]["subdivisions"], [])
        self.assertFalse(result[1]["national"])
        self.assertEqual(result[1]["subdivisions"], ["ES-CT", "ES-VC"])
