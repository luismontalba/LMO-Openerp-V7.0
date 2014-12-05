# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo - BoM cost
#    Copyright (C) 2014 Luis Martinez Ontalba (www.tecnisagra.com).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

import time
from openerp.report import report_sxw
from openerp.osv import osv
from openerp import pooler

class bom_cost_structure(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(bom_cost_structure, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_children':self.get_children,
        })

    def get_children(self, object):
        result = []
        for l in object:
            res = {}
            res['name'] = l.name
            res['pname'] = l.product_id.name
            res['pcode'] = l.product_id.default_code
            res['pqty'] = l.product_qty
            res['uname'] = l.product_uom.name
            res['ucost'] = l.cost_unit
            res['cost'] = l.cost
            res['code'] = l.code
            result.append(res)
        return result

report_sxw.report_sxw('report.bom.cost.structure','mrp.bom','bom_cost/bom_cost_structure.rml',parser=bom_cost_structure,header='internal')


