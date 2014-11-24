# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo - Analytic carrier
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

class account_analytic_account_carrier(osv.osv):
    _name = 'account.analytic.account'
    _inherit = 'account.analytic.account'
    _description = 'Analytic Account Carrier'

    def _children_calc(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}
        result = {}
        def get_family(acc_obj):
            for child in acc_obj.child_ids:
                family.append(child.id)
                get_family(child)
            return family
        for acc_obj in self.browse(cr, uid, ids, context=context):
            family = []
            result[acc_obj.id] = get_family(acc_obj)
        return result
    
    def _unit_amount_km_calc(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}
        result = {}
        for acc_obj in self.browse(cr, uid, ids, context=context):
            val1=0.0
            for lin_obj in acc_obj.line_ids:
                if lin_obj.product_uom_id.name == "km" and lin_obj.journal_id.type == "sale":
                    val1 += lin_obj.unit_amount
            val2=0.0
            for child_obj in acc_obj.children:
                for lin_obj in child_obj.line_ids:
                    if lin_obj.product_uom_id.name == "km" and lin_obj.journal_id.type == "sale":
                        val2 += lin_obj.unit_amount
            result[acc_obj.id] = val1 + val2
        return result        
            
    def _debit_per_qtty(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.unit_amount_km != 0.0:
                result[rec.id] = rec.debit/rec.unit_amount_km
            else:
                result[rec.id] = None
        return result
    
    def _credit_per_qtty(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.unit_amount_km != 0.0:
                result[rec.id] = rec.credit/rec.unit_amount_km
            else:
                result[rec.id] = None
        return result
    
    _columns = {
        'children': fields.function(_children_calc, relation='account.analytic.account', string="Account Hierarchy Total", type='many2many'),
        'unit_amount_km':fields.function(_unit_amount_km_calc, type='float', string='Kilometers', digits_compute=dp.get_precision('Account')),
        'debit_yield':fields.function(_debit_per_qtty, type='float', string='Incomes/Km', digits_compute=dp.get_precision('Account')),
        'credit_yield':fields.function(_credit_per_qtty, type='float', string='Expenses/Km', digits_compute=dp.get_precision('Account')),
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
