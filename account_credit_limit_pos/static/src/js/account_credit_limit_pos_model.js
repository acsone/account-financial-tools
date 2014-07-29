function account_credit_limit_pos_models(instance, module){ //module is instance.point_of_sale
    var QWeb = instance.web.qweb;
    var _t = instance.web._t;

    var round_di = instance.web.round_decimals;
    var round_pr = instance.web.round_precision;
    
    /*module.PosModel.include({
        load_server_data: function(){
            this._super();
            var self = this;
            var loaded = self.fetch('res.partner', ['name','street','city','country_id','phone','zip','mobile','email','ean13','blocked_customer']).then(function(partners){
                self.partners = partners;
                self.db.add_partners(partners);
            });
        }
    });*/
}