# -*- coding: utf-8 -*-

from odoo import models, fields, api


class comprobantes(models.Model):
    _name = 'comprobantes.comprobantes'
    _description = 'comprobantes.comprobantes'

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

    @api.onchange('tipo_comprobante')
    def _onchange_comprobante_type(self):
        if self.tipo_comprobante == 'consumidor':
            self.sequence_id = self.env.ref('comprobantes_fiscal.sequence_consumidor_final')
        elif self.tipo_comprobante == 'credito_fiscal':
            self.sequence_id = self.env.ref('comprobantes_fiscal.sequence_credito_fiscal')

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
