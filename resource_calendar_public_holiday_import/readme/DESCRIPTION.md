Base module to import public holidays into Odoo as global resource calendar
leaves (the records Odoo shows under *Time Off > Public Holidays*).

It provides the import wizard (available from the *Public Holidays* view via the
*Action* menu) and an extensible provider mechanism. Install a provider module
(e.g. *Resource Calendar Public Holiday Import: Nager.Date*) to fetch the data
from an actual source.

When a holiday is not national (it only applies to some subdivisions), the
subdivision codes are appended to the leave name (e.g. `Sant Joan [ES-CT]`).
