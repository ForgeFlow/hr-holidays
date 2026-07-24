/** @odoo-module **/

import {registry} from "@web/core/registry";
import {listView} from "@web/views/list/list_view";
import {ListController} from "@web/views/list/list_controller";

export class PublicHolidayImportListController extends ListController {
    async openImportPublicHolidayWizard() {
        await this.actionService.doAction(
            {
                type: "ir.actions.act_window",
                name: "Import Public Holidays",
                res_model: "public.holiday.import",
                views: [[false, "form"]],
                target: "new",
            },
            {onClose: () => this.model.load()}
        );
    }
}

registry.category("views").add("public_holiday_import_list", {
    ...listView,
    Controller: PublicHolidayImportListController,
    buttonTemplate: "resource_calendar_public_holiday_import.ListButtons",
});
