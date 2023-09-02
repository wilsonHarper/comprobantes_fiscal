# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timedelta


class comprobantes(models.Model):
    _name = 'comprobantes.comprobantes'
    _description = 'comprobantes.comprobantes'

    #===================     Inicio de los campo a utilizar variable del codigo      ===============================#
    validation_result = fields.Boolean(string='Resultado de Validación', compute='_compute_validation_result')
    num_to_generate = fields.Integer(string='Números a Generar', default=1)

    #Buscar todos los tipos de comprobante, utilizarlo en el dicionario
    tipo_comprobante =fields.Selection([
        ('consumidor', 'Consumidor Final'),
        ('credito_fiscal', 'Credito Fiscal'),
    ], string='Tipo de Comprobante', required=True, default='consumidor')

    numero_comprobante = fields.Char(string='Número comprobante fiscal', copy=False, readonly=True)
    #tipo = fields.Selection(TIPO_COMPROBANTE, string='Tipo de Comprobante', required=True, default='consumidor')
    sequence_id = fields.Many2one('ir.sequence', string='Secuencia', readonly=True)
    fecha_emision = fields.Date(string='Fecha de Emisión', default=fields.Date.context_today)
    fecha_vencimiento = fields.Date(string='Fecha de Vencimiento', compute='_compute_fecha_vencimiento')
    state = fields.Selection([
        ('disponible', 'Disponible'),
        ('asociado', 'Asociado'),
        ('vencido', 'Vencido'),
    ], string='Estado', default='disponible', readonly=True)
    
   

    #================    Find campos comprobante y asociacion de factura     ======================================#

    @api.onchange('tipo_comprobante')
    def _onchange_comprobante_type(self):
        if self.tipo_comprobante == 'consumidor':
            self.sequence_id = self.env.ref('comprobantes_fiscal.sequence_consumidor_final')
        elif self.tipo_comprobante == 'credito_fiscal':
            self.sequence_id = self.env.ref('comprobantes_fiscal.sequence_credito_fiscal')


    #======= inicio tiempo para vebcer los comprobantes=======#
    @api.depends('fecha_emision')
    def _compute_fecha_vencimiento(self):
        today = fields.Date.today()
        for record in self:
            if record.fecha_emision:
                record.fecha_vencimiento = record.fecha_emision + timedelta(days=1)
                if record.fecha_vencimiento > today and record.state != 'vencido':
                    record.state = 'vencido'

    # Crear el nuemro de acuerdo al tipo de compro vante validado
    def generate_comprobantes(self):
        for record in self:
            if record.num_to_generate >= 1:
                comprobantes = []
                for _ in range(record.num_to_generate):
                    if record.tipo_comprobante == 'consumidor':
                        sequence_code = 'dominican.fiscal.sequence.consumidor.final'
                    elif record.tipo_comprobante == 'credito_fiscal':  
                        sequence_code = 'dominican.fiscal.sequence.credito.fiscal'
                    next_number = self.env['ir.sequence'].sudo().next_by_code(sequence_code)
                    comprobantes.append({
                        'numero_comprobante': next_number,
                        'tipo_comprobante': record.tipo_comprobante,
                        'fecha_emision': record.fecha_emision,
                    })
                self.env['comprobantes.comprobantes'].create(comprobantes)
        
    # Vlidar el tipo de comprobante y general un numero de acuerdo al tipo 
    @api.depends('numero_comprobante')
    def _compute_validation_result(self):
        for record in self:
            if record.tipo_comprobante == 'consumidor':
                record.validation_result = len(record.numero_comprobante) == 11
            elif record.tipo_comprobante == 'credito_fiscal':
                record.validation_result = len(record.numero_comprobante) == 11

            else:
                record.validation_result = False

    #<----------Inicio del codigo para asocial un comprobante de la lista a la factura-------------->#
class MiFactura(models.Model):
    _inherit = 'account.move'

    tipo_comprobante = fields.Selection([
        ('consumidor', 'Consumidor Final'),
        ('credito_fiscal', 'Credito Fiscal'),
    ], string='Tipo de Comprobante')

    numero_comprobante_asignado = fields.Char(string='Número comprobante asignado', readonly=True)
    comprobante_id = fields.Many2one('comprobantes.comprobantes', string='Comprobante Asignado')



    @api.onchange('tipo_comprobante')
    def _onchange_tipo_comprobante(self):
        if self.tipo_comprobante:
            comprobante = self.env['comprobantes.comprobantes'].search([
                ('tipo_comprobante', '=', self.tipo_comprobante),
                ('numero_comprobante', '!=', False),
                ('state', '=', 'disponible'),
            ], order='create_date', limit=1)
            if comprobante:
                self.numero_comprobante_asignado = comprobante.numero_comprobante
                self.comprobante_id = comprobante

    def get_valid_comprobantes(self):
        today = fields.Date.today()
        valid_comprobantes = self.search([('fecha_vencimiento', '>=', today)])
        return valid_comprobantes

    @api.model
    def create(self, vals):
        if vals.get('tipo_comprobante'):
            comprobante = self.env['comprobantes.comprobantes'].search([
                ('tipo_comprobante', '=', vals['tipo_comprobante']),
                ('numero_comprobante', '!=', False),
                ('state', '=', 'disponible'),
            ], order='create_date', limit=1)
            if comprobante:
                vals['numero_comprobante_asignado'] = comprobante.numero_comprobante
                vals['comprobante_id'] = comprobante.id
                comprobante.write({'state': 'asociado'})
        return super(MiFactura, self).create(vals)
    

    def unlink(self):
        for factura in self:
            if factura.comprobante_id:
                comprobante = factura.comprobante_id
                comprobante.write({'state': 'disponible'})
            super(MiFactura, factura).unlink()
    
    