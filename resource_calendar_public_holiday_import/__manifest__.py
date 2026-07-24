# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Resource Calendar Public Holiday Import",
    "summary": "Base to import public holidays as global calendar leaves",
    "version": "16.0.1.0.0",
    "license": "LGPL-3",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/hr-holidays",
    "category": "Human Resources/Time Off",
    "maintainers": ["RicardCForgeFlow"],
    "depends": ["hr_holidays"],
    "data": [
        "security/ir.model.access.csv",
        "wizards/public_holiday_import_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "resource_calendar_public_holiday_import/static/src/views/"
            "public_holiday_import_list_controller.esm.js",
            "resource_calendar_public_holiday_import/static/src/views/"
            "public_holiday_import_list_buttons.xml",
        ],
    },
    "installable": True,
}
