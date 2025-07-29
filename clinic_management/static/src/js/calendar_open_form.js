/** @odoo-module **/

import { CalendarController } from "@web/views/calendar/calendar_controller";
import { patch } from "@web/core/utils/patch";

patch(CalendarController.prototype, {
    async onCreate(ev) {
        const { start, end } = ev.data;
        const startISO = start.toISOString().split(".")[0];
        const endISO = end.toISOString().split(".")[0];

        // ✅ Open full form view directly
        this.actionService.doAction({
            type: "ir.actions.act_window",
            res_model: this.modelName, // clinic.appointment
            views: [[false, "form"]],
            target: "current",
            context: {
                default_date_start: startISO,
                default_date_end: endISO,
            },
        });
    },
});
