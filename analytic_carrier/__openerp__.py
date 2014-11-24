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

{
    'name' : 'Analytic Carrier',
    'version': '1.0',
    'author' : 'Luis Martinez Ontalba',
    'website' : 'http://www.tecnisagra.com',
    'category': 'Hidden/Dependency',
    'depends' : ['base','account'],
    'description': """
Module for extending analytic accounting object for carrier companies.
    """,
    'data': [
        'analytic_carrier_view.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
