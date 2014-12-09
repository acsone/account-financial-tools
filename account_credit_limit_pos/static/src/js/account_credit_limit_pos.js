openerp.account_credit_limit_pos = function (instance) {
    var module = instance.point_of_sale;
    account_credit_limit_pos_models(instance, module);
    account_credit_limit_pos_screens(instance, module);
};