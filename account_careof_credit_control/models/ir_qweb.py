# -*- coding: utf-8 -*-
#
##############################################################################
#
#    Authors: Adrien Peiffer
#    Copyright (c) 2015 Acsone SA/NV (http://www.acsone.eu)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, api, _
from openerp.addons.base.ir.ir_qweb import HTMLSafe
from lxml import etree


class Contact(models.AbstractModel):
    _inherit = 'ir.qweb.field.contact'

    @api.model
    def record_to_html(self, field_name, record, options=None):
        invoice_care_of = str(record._model) ==\
            'credit.control.communication'and\
            field_name == 'contact_address' and\
            record['account_careof_partner_id']
        if invoice_care_of:
            field_name = 'account_careof_partner_id'
        res = super(Contact, self)\
            .record_to_html(field_name, record, options=options)
        if invoice_care_of:
            doc = etree.XML(res.__unicode__())
            new_div = "<div><span>%s</span></div>" % (
                record['partner_id'].name_get()[0][1].split("\n")[0])
            node_tree = etree.fromstring(new_div)
            node = doc.xpath("//div[span[@itemprop='name']]")[0]
            node.text = "%s %s" % (_("C/O"), node.text)
            node.addprevious(node_tree)
            res = HTMLSafe(etree.tostring(doc))
        return res
