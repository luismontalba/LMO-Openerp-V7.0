# -*- coding: utf-8 -*-

from openerp.osv import fields, osv
from openerp import tools

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
    
    
class lascuentas_periodo(osv.osv):
    _name = 'lascuentas.periodo'
    _description = 'Periodo contable'
    
    _order = 'name desc'
    
    def calcular_saldo_total(self, cr, uid, ids, saldo_total, arg, context=None):
        if not ids: return {}
        cr.execute( 'SELECT periodo_id, SUM(importe) ' 
                    'FROM lascuentas_saldo '
                    'WHERE periodo_id IN %s '
                    'GROUP BY periodo_id', (tuple(ids),)
        )
        result = dict(cr.fetchall())
        for id in ids:
            result.setdefault(id, 0.00)
        return result
        
    def actualizar_saldo_total(self, cr, uid, ids, context=None):
        #Caso de solo actualizar los registros tocados:
        #return [s.id for s in self.pool.get('lascuentas.saldo').browse(cr, uid, ids, context=None)]
        return self.search(cr, uid, [], context=None)
        
    def calcular_saldo_reservado(self, cr, uid, ids, saldo_reservado, arg, context=None):
        if not ids: return {}
        cr.execute( 'SELECT periodo_id, SUM(reserva_historica) ' 
                    'FROM lascuentas_gasto '
                    'WHERE periodo_id IN %s '
                    'GROUP BY periodo_id', (tuple(ids),)
        )
        result = dict(cr.fetchall())
        for id in ids:
            result.setdefault(id, 0.00)
        return result
    
    def actualizar_saldo_reservado(self, cr, uid, ids, context=None):
        return self.search(cr, uid, [], context=None)
        
    def calcular_saldo_disponible(self, cr, uid, ids, saldo_disponible, arg, context=None):
        result = {}
        periodo_obj = self.browse(cr, uid, ids, context=None)
        for p in periodo_obj:
            result[p.id] = p.saldo_total - p.saldo_reservado
        return result
    #borrable    
    def actualizar_saldo_disponible(self, cr, uid, ids, saldo_disponible, arg, context=None):
        return self.search(cr, uid, [], context=None)
        
    def calcular_prevision_anual_total(self, cr, uid, ids, prevision_anual_total, arg, context=None):
        if not ids: return {}
        cr.execute( 'SELECT periodo_id, SUM(prevision_anual) ' 
                    'FROM lascuentas_gasto '
                    'WHERE periodo_id IN %s '
                    'GROUP BY periodo_id', (tuple(ids),)
        )
        result = dict(cr.fetchall())
        return result
        
    def calcular_dias_cubiertos(self, cr, uid, ids, dias_cubiertos, arg, context=None):
        result = {}
        periodo_obj = self.browse(cr, uid, ids)
        for p in periodo_obj:
            if p.prevision_anual_total<>0:
                result[p.id] = (p.saldo_disponible / p.prevision_anual_total)*365
        return result
        
    _columns = {
        'name': fields.char('Periodo', size=64, required=True),
        'abierto': fields.boolean('Abierto'),
        'saldo_total': fields.function(
            calcular_saldo_total,
            type="float", string="Saldo total", digits=(12,2),
            store = {
                'lascuentas.saldo':(
                    actualizar_saldo_total,
                    ['importe'],
                    10
                )
            }),
        'saldo_reservado': fields.function(
            calcular_saldo_reservado,
            type="float", string="Saldo reservado", digits=(12,2),
            store = {
                'lascuentas.gasto':(
                    actualizar_saldo_reservado,
                    ['reserva_historica'],
                    10
                )
            }),
        'saldo_disponible': fields.function(
            calcular_saldo_disponible,
            type="float", string="Saldo disponible", digits=(12,2), store=True),
        'prevision_anual_total': fields.function(
            calcular_prevision_anual_total,
            type="float", string="Previsión anual", digits=(12,2), store=True),
        'dias_cubiertos': fields.function(
            calcular_dias_cubiertos,
            type="float", string="Dias cubiertos", digits=(12,0), store=True),
    }
    
    _sql_constraints = [
        ('periodo_name_uniq', 'unique(name)', 'El nombre del registro debe ser único'),
    ]
    
    _defaults = {
        'abierto': True,
    }
 
 
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
    
class lascuentas_caja(osv.osv):
    _name = 'lascuentas.caja'
    _description = 'Banco o caja'
    
    _columns = {
        'name': fields.char('Caja', size=64, required=True),
    }
    
    _sql_constraints = [
        ('caja_name_uniq', 'unique(name)', 'El nombre del registro debe ser único'),
    ]

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
        
    def calcular_reserva_actual(self, cr, uid, ids, reserva_actual, arg, context=None):
        result = {}
        concepto_obj = self.browse(cr, uid, ids)
        for c in concepto_obj:
            result[c.id] = c.reserva_inicial - c.desviacion_total
        return result

    _columns = {
        'tipo_id': fields.many2one('lascuentas.tipo', 'Tipo', required=True),
        'orden': fields.integer('Orden'),
        'name': fields.char('Concepto', size=64, required=True),
        'activo': fields.boolean('Activo'),
        'reserva_inicial': fields.float('Reserva inicial', digits=(12,2)),
        'frecuencia_anual': fields.float('Frecuencia anual', digits=(6,3), required=True),
        'importe_unitario': fields.float('Importe unitario', digits=(12,2), required=True),
        'prevision_anual': fields.function(
            calcular_prevision_anual,
            type="float", string="Previsión anual", digits=(12,2), store=True),
        'prevision_mensual': fields.function(
            calcular_prevision_mensual,
            type="float", string="Previsión mensual", digits=(12,2), store=True),
        'ajustar': fields.boolean('Ajustar'),
        #La desviacion total se calcula sumando las desviaciones historicas para respetar criterios pasados
        'desviacion_total': fields.float('Desviación total', digits=(12,2), readonly=True),
        'reserva_actual': fields.function(
            calcular_reserva_actual,
            type="float", string="Reserva actual", digits=(12,2), store=True),
    }
    
    _sql_constraints = [
        ('concepto_name_uniq', 'unique(name)', 'El nombre del registro debe ser único'),
        ('concepto_importe_unitario_check', 'check(importe_unitario<>0)', 'El valor del importe unitario no puede ser cero'),
        ('concepto_frecuencia_anual_check', 'check(frecuencia_anual<>0)', 'El valor de la frecuencia anual no puede ser cero'),
    ]
    
    _defaults = {
        'orden': 100,
        'ajustar': True,
        'activo': True,
        'frecuencia_anual': 12,
    }

    
class lascuentas_pago(osv.osv):
    _name = 'lascuentas.pago'
    _description = 'Pagos realizados'
    
    _order = 'periodo_id desc, users_id, concepto_id'
    
    _columns = {
        'periodo_id': fields.many2one('lascuentas.periodo', 'Periodo', required=True),
        'users_id': fields.many2one('res.users', 'Usuario'),
        'concepto_id': fields.many2one('lascuentas.concepto', 'Concepto', required=True),
        'importe': fields.float('Importe', digits=(12,2), required=True),
    }
    
    _sql_constraints = [
        ('concepto_importe_check', 'check(importe<>0)', 'El valor del importe no puede ser cero'),
    ]

    
class lascuentas_gasto(osv.osv):
    _name = 'lascuentas.gasto'
    _description = 'Gastos realizados'
    
    _order = 'periodo_id desc, concepto_id'
    
    _columns = {
        'periodo_id': fields.many2one('lascuentas.periodo', 'Periodo', readonly=True),
        'concepto_id': fields.many2one('lascuentas.concepto', 'Concepto', readonly=True),
        'reserva_inicial': fields.float('Reserva inicial', digits=(12,2), readonly=True ),
        'frecuencia_anual': fields.float('Frecuencia anual', digits=(6,3), readonly=True),
        'importe_unitario': fields.float('Importe unitario', digits=(12,2), readonly=True),
        'prevision_anual': fields.float('Previsión anual', digits=(12,2), readonly=True),
        'prevision_mensual': fields.float('Previsión mensual', digits=(12,2), readonly=True),
        'ajustar': fields.boolean('Ajustar', readonly=True), 
        'pagado': fields.float('Pagado', digits=(12,2), readonly=True),
        'desviacion': fields.float('Desviacion', digits=(12,2), readonly=True),
        'reserva_historica': fields.float('Reserva histórica', digits=(12,2), readonly=True),
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
                    cr.execute( 'SELECT SUM(importe) ' 
                                'FROM lascuentas_pago '
                                'WHERE concepto_id=%s '
                                'AND periodo_id=%s ',(c.id,p.id,)
                    )
                    suma = cr.fetchone()[0] or 0.00
                    if c.ajustar:
                        desv = c.prevision_mensual - suma
                    else: desv = 0.00
                    resh = c.reserva_inicial - desv
                    gasto_pool.create(cr, uid,
                        {
                            'periodo_id': p.id,
                            'concepto_id': c.id,
                            'reserva_inicial': c.reserva_inicial,
                            'frecuencia_anual': c.frecuencia_anual,
                            'importe_unitario': c.importe_unitario,
                            'previsión_anual': c.prevision_anual,
                            'prevision_mensual': c.prevision_mensual,
                            'ajustar': c.ajustar,
                            'pagado': suma,
                            'desviacion': desv,
                            'reserva_historica': resh,
                        }
                    )
        
        con_list = concepto_pool.search(cr, uid, [])
        for c in concepto_pool.browse(cr, uid, con_list):
            creados = gasto_pool.search(cr, uid, [('concepto_id','=',c.id)])
            total = sum(g.desviacion for g in gasto_pool.browse(cr, uid, creados))
            concepto_pool.write(cr, uid, c.id, {'desviacion_total':total})
        
        
        return True