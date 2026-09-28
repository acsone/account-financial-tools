import {registry} from "@web/core/registry";

registry.category("web_tour.tours").add("account_account_control", {
    steps: () => [
        {
            trigger: ".o_form_view .o_field_widget[name=name] input",
            run: "edit Modified by tour",
        },
        {
            trigger: ".o_form_button_save",
            run: "click",
        },
        {
            trigger: ".modal .o_field_widget[name=reason_id] input",
            run: "edit Tour",
        },
        {
            trigger: ".o-autocomplete--dropdown-item:contains(Tour reason)",
            run: "click",
        },
        {
            trigger: ".modal .modal-footer button.btn-primary",
            run: "click",
        },
        {
            trigger: "body:not(:has(.modal)) .o_form_view .o_form_saved",
        },
    ],
});
