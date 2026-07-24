# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from datetime import date, datetime

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestPublicHolidayImport(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.company.resource_calendar_id.tz = "Europe/Madrid"
        cls.wizard = cls.env["public.holiday.import"].create(
            {"country_id": cls.env.ref("base.es").id, "year": 2099}
        )

    def _global_leaves(self, extra_domain=None):
        domain = [("resource_id", "=", False), ("calendar_id", "=", False)]
        return self.env["resource.calendar.leaves"].search(
            domain + (extra_domain or [])
        )

    def test_full_day_in_company_tz(self):
        self.wizard._create_leaves(
            [{"date": date(2099, 1, 6), "name": "Reyes", "national": True}]
        )
        leave = self._global_leaves([("name", "=", "Reyes")])
        self.assertEqual(len(leave), 1)
        # Madrid (UTC+1 in winter): local 2099-01-06 00:00 == 2099-01-05 23:00 UTC
        self.assertEqual(leave.date_from, datetime(2099, 1, 5, 23, 0, 0))
        self.assertEqual(
            leave.date_to.replace(microsecond=0), datetime(2099, 1, 6, 22, 59, 59)
        )
        self.assertEqual(leave.time_type, "leave")

    def test_subdivision_appended_to_name(self):
        self.wizard._create_leaves(
            [
                {
                    "date": date(2099, 2, 28),
                    "name": "Andalucia",
                    "national": False,
                    "subdivisions": ["ES-AN"],
                }
            ]
        )
        self.assertTrue(self._global_leaves([("name", "=", "Andalucia [ES-AN]")]))

    def test_overlapping_is_skipped(self):
        holiday = {"date": date(2099, 3, 1), "name": "Test", "national": True}
        self.assertEqual(self.wizard._create_leaves([holiday]), 1)
        self.assertEqual(self.wizard._create_leaves([holiday]), 0)
        self.assertEqual(len(self._global_leaves([("name", "=", "Test")])), 1)

    def test_filter_by_subdivision(self):
        holidays = [
            {"name": "Nat", "national": True, "subdivisions": []},
            {"name": "Cat", "national": False, "subdivisions": ["ES-CT"]},
            {"name": "And", "national": False, "subdivisions": ["ES-AN"]},
        ]
        self.wizard.subdivision_code = "es-ct"
        names = [h["name"] for h in self.wizard._filter_by_subdivision(holidays)]
        self.assertEqual(names, ["Nat", "Cat"])

    def test_invalid_subdivision_raises(self):
        holidays = [{"name": "Cat", "national": False, "subdivisions": ["ES-CT"]}]
        self.wizard.subdivision_code = "ES-XX"
        with self.assertRaises(UserError):
            self.wizard._filter_by_subdivision(holidays)
