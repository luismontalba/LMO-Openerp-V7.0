# -*- coding: utf-8 -*-

from openerp.osv import fields, osv
from openerp import tools
from datetime import datetime


class lascuentas_pago(osv.osv):
    _name = 'lascuentas.pago'
    _description = 'Pagos realizados'
    
    _order = 'periodo_id desc, users_id, concepto_id'
    
    _columns = {
        'periodo_id': fields.many2one('lascuentas.periodo', 'Periodo', required=True),
        'users_id': fields.many2one('res.users', 'Usuario', required=True),
        'caja_id': fields.many2one('lascuentas.caja', 'Caja', required=True),
        'concepto_id': fields.many2one('lascuentas.concepto', 'Concepto', required=True),
        'fecha': fields.date('Fecha'),
        'importe': fields.float('Importe', digits=(12,2), required=True),
    }
    
    _sql_constraints = [
        ('concepto_importe_check', 'check(importe<>0)', 'El valor del importe no puede ser cero'),
    ]
    
    _defaults = {
        'periodo_id': lambda self,cr,uid,c: self.pool.get('lascuentas.periodo').search(cr,uid,[],limit=1)[0],
        'users_id': lambda self,cr,uid,c: self.pool.get('res.users').search(cr,uid,[],limit=1)[0],
    }
