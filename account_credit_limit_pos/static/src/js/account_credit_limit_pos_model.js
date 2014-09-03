function account_credit_limit_pos_models(instance, module){ //module is instance.point_of_sale
    var QWeb = instance.web.qweb;
    var _t = instance.web._t;

    var round_di = instance.web.round_decimals;
    var round_pr = instance.web.round_precision;
    
    var _super_initialize = module.PosModel.prototype.initialize;
    
    function AddCustomerFields(pos_model) {
        var res_partner_model = pos_model.find_model('res.partner');
        if (Object.size(res_partner_model) == 1) {
            var res_partner_index = parseInt(Object.keys(res_partner_model)[0]);
            pos_model.models[res_partner_index].fields.push('property_payment_term','blocked_customer','amount_blocked')
        }
    };
    
    module.PosModel.prototype.initialize = function(session, attributes){
        _super_initialize.call(this, session, attributes);
        AddCustomerFields(this);
    }   
}