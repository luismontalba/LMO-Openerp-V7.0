# -*- coding: utf-8 -*-

from openerp.osv import fields, osv
from openerp import tools


class lascuentas_tipo(osv.osv):
    _name = 'lascuentas.tipo'
    _description = 'Tipo de gasto'
    
    _order= 'orden'
    
    _columns = {
        'name': fields.char('Tipo', size=64, required=True),
        'orden': fields.integer('Orden'),
    }
    
    _sql_constraints = [
        ('tipo_name_uniq', 'unique(name)', 'El nombre del registro debe ser único'),
    ]
    
    _defaults = {
        'orden': 100,
    }
    

class lascuentas_concepto(osv.osv):
    _name = 'lascuentas.concepto'
    _description = 'Concepto de gasto'
    
    _order = 'tipo_id, orden, name'
    
    def calcular_prevision_anual(self, cr, uid, ids, prevision_anual, arg, context=None):
        result = {}
        concepto_obj = self.browse(cr, uid, ids)
        for c in concepto_obj:
            result[c.id] = c.frecuencia_anual * c.importe_unitario
        return result
        
    def calcular_prevision_mensual(self, cr, uid, ids, prevision_mensual, arg, context=None):
        result = {}
        concepto_obj = self.browse(cr, uid, ids)
        for c in concepto_obj:
            result[c.id] = c.frecuencia_anual * c.importe_unitario / 12
        return result
        
    #La desviacion total se calcula sumando las desviaciones historicas para respetar criterios pasados
    def calcular_desviacion_total(self, cr, uid, ids, desviacion_total, arg, context=None):
        result = {}
        gasto_pool = self.pool.get('lascuentas.gasto')
        for c in self.browse(cr, uid, ids):
            gastos = gasto_pool.search(cr,uid,[('concepto_id.id','=',c.id)])
            suma = sum(g.desviacion for g in gasto_pool.browse(cr, uid, gastos))
            result[c.id] = suma
        return result
    
    def calcular_reserva_actual(self, cr, uid, ids, reserva_actual, arg, context=None):
        result = {}
        concepto_obj = self.browse(cr, uid, ids)
        for c in concepto_obj:
            result[c.id] = c.reserva_inicial + c.desviacion_total
        return result

    _columns = {
        'tipo_id': fields.many2one('lascuentas.tipo', 'Tipo', required=True),
        'orden': fields.integer('Orden'),
        'name': fields.char('Concepto', size=64, required=True),
        'activo': fields.boolean('Activo'),
        'reserva_inicial': fields.float('Reserva inicial', digits=(12,2)),
        'frecuencia_anual': fields.float('Frecuencia anual', digits=(6,3)),
        'importe_unitario': fields.float('Importe unitario', digits=(12,2)),
        'prevision_anual': fields.function(
            calcular_prevision_anual,
            type="float", string="Previsión anual", digits=(12,2)),
        'prevision_mensual': fields.function(
            calcular_prevision_mensual,
            type="float", string="Previsión mensual", digits=(12,2)),
        'ajustar': fields.boolean('Ajustar'),
        'desviacion_total': fields.function(
            calcular_desviacion_total,
            type="float", string="Desviación total", digits=(12,2)),
        'reserva_actual': fields.function(
            calcular_reserva_actual,
            type="float", string="Reserva actual", digits=(12,2)),
    }
    
    _sql_constraints = [
        ('concepto_name_uniq', 'unique(name)', 'El nombre del concepto debe ser único'),
#        ('concepto_importe_unitario_check', 'check(importe_unitario<>0)', 'El valor del importe unitario no puede ser cero'),
#        ('concepto_frecuencia_anual_check', 'check(frecuencia_anual<>0)', 'El valor de la frecuencia anual no puede ser cero'),
    ]
    
    _defaults = {
        'orden': 100,
        'ajustar': True,
        'activo': True,
        'frecuencia_anual': 12,
    }

    
class lascuentas_gasto(osv.osv):
    _name = 'lascuentas.gasto'
    _description = 'Gastos realizados'
    
    _order = 'periodo_id desc, concepto_id'
    
    def calcular_pagado(self, cr, uid, ids, pagado, arg, context=None):
        result = {}
        pagos_pool = self.pool.get('lascuentas.pago')
        for g in self.browse(cr, uid, ids):
            pagos = pagos_pool.search(cr,uid,[('concepto_id.id','=',g.concepto_id.id),('periodo_id.id','=',g.periodo_id.id)])
            suma = sum(p.importe for p in pagos_pool.browse(cr, uid, pagos))
            result[g.id] = suma
        return result
        
    def calcular_desviacion(self, cr, uid, ids, desviacion, arg, context=None):
        result = {}
        gasto_obj = self.browse(cr, uid, ids)
        for g in gasto_obj:
            if g.ajustar:
                result[g.id] = g.prevision_mensual - g.pagado
            else: result[g.id] = 0.00
        return result
        
    _columns = {
        'periodo_id': fields.many2one('lascuentas.periodo', 'Periodo', required=True),
        'concepto_id': fields.many2one('lascuentas.concepto', 'Concepto', required=True),
        'reserva_inicial': fields.float('Reserva inicial', digits=(12,2)),
        'frecuencia_anual': fields.float('Frecuencia anual', digits=(6,3)),
        'importe_unitario': fields.float('Importe unitario', digits=(12,2)),
        'prevision_anual': fields.float('Previsión anual', digits=(12,2)),
        'prevision_mensual': fields.float('Previsión mensual', digits=(12,2)),
        'ajustar': fields.boolean('Ajustar'),
        'pagado': fields.function(
            calcular_pagado,
            type="float", string="Pagado", digits=(12,2)),
        'desviacion': fields.function(
            calcular_desviacion,
            type="float", string="Desviación", digits=(12,2)),
    }
    
    _sql_constraints = [
        ('gasto_multiple_uniq', 'unique(periodo_id,concepto_id)', 'El concepto ya existe para el periodo'),
    ]
    
    _defaults = {
        'ajustar': True,
        'frecuencia_anual': 12,
        'periodo_id': lambda self,cr,uid,c: self.pool.get('lascuentas.periodo').search(cr,uid,[],limit=1)[0]
    }

    
class lascuentas_actualizar(osv.osv_memory):
    
    _name = 'lascuentas.actualizar'
        
    def crear_gastos(self, cr, uid, ids, context=None):
        
        periodo_pool =self.pool.get('lascuentas.periodo')
        concepto_pool =self.pool.get('lascuentas.concepto')
        gasto_pool = self.pool.get('lascuentas.gasto')
        
        if context is None:
            context = {}
            
        abiertos = periodo_pool.search(cr, uid, [('abierto','=',True)], context=context)
        periodo_obj = periodo_pool.browse(cr,uid,abiertos,context=context)
        
        activos = concepto_pool.search(cr, uid, [('activo','=',True)], context=context)
        concepto_obj = concepto_pool.browse(cr,uid,activos,context=context)

        for p in periodo_obj:
            for c in concepto_obj:
                n = gasto_pool.search(cr, uid, [('concepto_id','=',c.id),('periodo_id','=',p.id)], count=True)
                if n > 1:
                    raise osv.except_osv('Problema', 'Hay mas de un periodo por concepto')
                elif n == 0:
                    gasto_pool.create(cr, uid,
                        {
                            'periodo_id': p.id,
                            'concepto_id': c.id,
                            'reserva_inicial': c.reserva_inicial,
                            'frecuencia_anual': c.frecuencia_anual,
                            'importe_unitario': c.importe_unitario,
                            'prevision_anual': c.prevision_anual,
                            'prevision_mensual': c.prevision_mensual,
                            'ajustar': c.ajustar,
                        }
                    )
                    
        return True