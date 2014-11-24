# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo - BoM cost
#    Copyright (C) 2014 Luis Martinez Ontalba (www.tecnisagra.com).
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

from openerp.osv import fields, osv
from openerp import tools
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

class mrp_bom_cost(osv.osv):
    _name = 'mrp.bom'
    _inherit = 'mrp.bom'
	
    def _get_cost(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.product_qty != 0.0:
                result[rec.id] = rec.product_qty * rec.cost_unit
            else:
                result[rec.id] = None
        return result
    
    _columns = {
	    'cost_unit':fields.related(
            'product_id',
            'cost_price',
            type="float",
            string="Unit cost",
            readonly=True,
            store=False),
        'cost':fields.function(
            _get_cost,
            type='float',
            string='Cost',
            digits_compute=dp.get_precision('Account'),
			help="This is the quantity multiplied by the unit cost" ),
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
