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

{
    'name' : 'BoM Cost',
    'version': '1.0',
    'author' : 'Luis Martinez Ontalba',
    'website' : 'http://www.tecnisagra.com',
    'category': 'Hidden/Dependency',
    'depends' : ['base','mrp','product_cost_incl_bom','account'],
    'description': """
This module adds cost in the BoM tree and form view, and creates a new BoM report with the cost
of items included
    """,
    'data': [
        'bom_cost_view.xml',
        'bom_cost_report.xml'
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
