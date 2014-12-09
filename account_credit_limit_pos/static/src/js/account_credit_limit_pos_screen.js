function account_credit_limit_pos_screens(instance, module){
    var QWeb = instance.web.qweb,
    _t = instance.web._t;

    module.ClientListScreenWidget.include({
        
        init: function(parent, options){
            this._super(parent, options);
        },

        line_select: function(event,$line,id){
            res = this._super(event,$line,id);
            parent = this
            new instance.web.Model('res.partner').query(['blocked_customer', 'amount_blocked']).filter([[ 'id', '=', id]]).context(null).all().then(function (partners){
                if (partners[0].blocked_customer == true) {
                    parent.pos_widget.screen_selector.show_popup('error', {
                        message: _t('This customer is blocked !'),
                        comment : (_t('Amount blocked : ') + partners[0].amount_blocked)
                    });
                }
            }).fail(function(error, event) {
                event.preventDefault();
                parent.pos_widget.screen_selector.show_popup('error', {
                    message : _t('Offline Mode'),
                    comment : _t('Impossible to get information about customer blocked.')
                });
            });
            return res
        }
    });
}
