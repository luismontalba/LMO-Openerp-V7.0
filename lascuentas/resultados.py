# -*- coding: utf-8 -*-

from openerp.osv import fields, osv
from openerp import tools


class lascuentas_periodo(osv.osv):
    _name = 'lascuentas.periodo'
    _description = 'Periodo contable'
    
    _order = 'name desc'
    
    def calcular_saldo_total(self, cr, uid, ids, saldo_total, arg, context=None):
        result = {}
        saldo_pool = self.pool.get('lascuentas.saldo')
        for p in self.browse(cr, uid, ids):
            saldos = saldo_pool.search(cr,uid,[('periodo_id.id','=',p.id)])
            suma = sum(s.importe for s in saldo_pool.browse(cr, uid, saldos))
            result[p.id] = suma
        return result
        
    # La suma de lo reservado de cada concepto para el que existe gasto en un periodo
    def calcular_saldo_reservado(self, cr, uid, ids, saldo_reservado, arg, context=None):
        result = {}
        gasto_pool = self.pool.get('lascuentas.gasto')
        concepto_pool = self.pool.get('lascuentas.concepto')
        conceptos = concepto_pool.search(cr, uid, [])
        periodos = self.search(cr, uid, [])
        saldo_inicial_total = sum(c.reserva_inicial for c in concepto_pool.browse(cr, uid, conceptos))
        for p in self.browse(cr, uid, ids):
            periodos_sub = periodos[periodos.index(p.id):]
            #gastos = gasto_pool.search(cr,uid,[('periodo_id','=',p.name)])
            gastos = gasto_pool.search(cr,uid,[('periodo_id.id','in',periodos_sub)])
            #suma = sum(g.concepto_id.reserva_actual for g in gasto_pool.browse(cr, uid, gastos))
            suma = saldo_inicial_total + sum(g.desviacion for g in gasto_pool.browse(cr, uid, gastos))
            result[p.id] = suma
        return result

    def calcular_saldo_disponible(self, cr, uid, ids, saldo_disponible, arg, context=None):
        result = {}
        periodo_obj = self.browse(cr, uid, ids)
        for p in periodo_obj:
            result[p.id] = p.saldo_total - p.saldo_reservado
        return result
        
    def calcular_prevision_anual_total(self, cr, uid, ids, prevision_anual_total, arg, context=None):
        result = {}
        gasto_pool = self.pool.get('lascuentas.gasto')
        for p in self.browse(cr, uid, ids):
            gastos = gasto_pool.search(cr,uid,[('periodo_id.id','=',p.id)])
            suma = sum(g.prevision_anual for g in gasto_pool.browse(cr, uid, gastos))
            result[p.id] = suma
        return result
        
    def calcular_dias_cubiertos(self, cr, uid, ids, dias_cubiertos, arg, context=None):
        result = {}
        periodo_obj = self.browse(cr, uid, ids)
        for p in periodo_obj:
            if p.prevision_anual_total != 0.00:
                result[p.id] = 365.00 * p.saldo_disponible / p.prevision_anual_total
            else: result[p.id] = 0.00
        return result
        
    _columns = {
        'name': fields.char('Periodo', size=64, required=True),
        'abierto': fields.boolean('Abierto'),
        'saldo_total': fields.function(
            calcular_saldo_total,
            type="float", string="Saldo total", digits=(12,2)),
        'saldo_reservado': fields.function(
            calcular_saldo_reservado,
            type="float", string="Saldo reservado", digits=(12,2)),
        'saldo_disponible': fields.function(
            calcular_saldo_disponible,
            type="float", string="Saldo disponible", digits=(12,2)),
        'prevision_anual_total': fields.function(
            calcular_prevision_anual_total,
            type="float", string="Previsión anual", digits=(12,2)),
        'dias_cubiertos': fields.function(
            calcular_dias_cubiertos,
            type="float", string="Dias cubiertos", digits=(12,0)),
    }
    
    _sql_constraints = [
        ('periodo_name_uniq', 'unique(name)', 'El nombre del registro debe ser único'),
    ]
    
    _defaults = {
        'abierto': True,
    }
 
 
class lascuentas_saldo(osv.osv):
    _name = 'lascuentas.saldo'
    _description = 'Saldo de bancos y cajas'
    
    _order = 'periodo_id desc, caja_id'
    
    _columns = {
        'periodo_id': fields.many2one('lascuentas.periodo', 'Periodo', required=True),
        'caja_id': fields.many2one('lascuentas.caja', 'Caja', required=True),
        'importe': fields.float('Importe', digits=(12,2), required=True),
    }
    
    _sql_constraints = [
        ('saldo_multiple_uniq', 'unique(periodo_id,caja_id)', 'El saldo ya existe'),
    ]
    
    _defaults = {
        'periodo_id': lambda self,cr,uid,c: self.pool.get('lascuentas.periodo').search(cr,uid,[],limit=1)[0]
    }
 
 
class lascuentas_caja(osv.osv):
    _name = 'lascuentas.caja'
    _description = 'Banco o caja'
    _order = 'name'
    
    _columns = {
        'name': fields.char('Caja', size=64, required=True),
    }
    
    _sql_constraints = [
        ('caja_name_uniq', 'unique(name)', 'El nombre del registro debe ser único'),
    ]

