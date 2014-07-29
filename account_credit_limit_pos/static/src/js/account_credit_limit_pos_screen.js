function account_credit_limit_pos_screens(instance, module){ //module is instance.point_of_sale
    var QWeb = instance.web.qweb,
    _t = instance.web._t;

    var round_pr = instance.web.round_precision
    
    module.ClientListScreenWidget.include({
        
        start: function(parent,options){
            this._super(parent,options);
            return new instance.web.Model('res.partner').query(['name','street','city','country_id','phone','zip','mobile','email','ean13','property_payment_term','blocked_customer','amount_blocked']).filter([]).context(null).all().then(function(partners){
                for (i=0;i<partners.length;i++) {
                    if (partners[i].property_payment_term != false) {
                        partners[i].property_payment_term = partners[i].property_payment_term[1]
                    }
                }
                self.posmodel.db.add_partners(partners);
            });
        }
    });
}