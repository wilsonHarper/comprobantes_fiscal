# -*- coding: utf-8 -*-

from odoo import models, fields, api


class comprobantes(models.Model):
    _name = 'comprobantes.comprobantes'
    _description = 'comprobantes.comprobantes'

    validation_result = fields.Boolean(string='Resultado de Validación', compute='_compute_validation_result')

    #Buscar todos los tipos de comprobante, utilizarlo en el dicionario
    tipo_comprobante =fields.Selection([
        ('consumidor', 'Consumidor Final'),
        ('credito_fiscal', 'Credito Fiscal'),
    ], string='Tipo de Comprobante', required=True, default='consumidor')

    numero_comprobante = fields.Char(string='Número comprobante fiscal', copy=False, default='Nuevo',  readonly=True)
    #tipo = fields.Selection(TIPO_COMPROBANTE, string='Tipo de Comprobante', required=True, default='consumidor')
    sequence_id = fields.Many2one('ir.sequence', string='Secuencia', readonly=True)

    @api.onchange('tipo_comprobante')
    def _onchange_comprobante_type(self):
        if self.tipo_comprobante == 'consumidor':
            self.sequence_id = self.env.ref('comprobantes_fiscal.sequence_consumidor_final')
        elif self.tipo_comprobante == 'credito_fiscal':
            self.sequence_id = self.env.ref('comprobantes_fiscal.sequence_credito_fiscal')

    @api.model
    def create(self, vals):
        if vals.get('tipo_comprobante') == 'consumidor':
            sequence_id = self.env.ref('comprobantes_fiscal.sequence_consumidor_final').id
            vals['numero_comprobante'] = self.env['ir.sequence'].browse(sequence_id).next_by_code('dominican.fiscal.sequence.consumidor.final') or 'Error: No se pudo generar el numero de comprobante'

        elif vals.get('tipo_comprobante') == 'credito_fiscal':
            sequence_id = self.env.ref('comprobantes_fiscal.sequence_credito_fiscal').id
            vals['numero_comprobante'] = self.env['ir.sequence'].browse(sequence_id).next_by_code('dominican.fiscal.sequence.credito.fiscal') or 'Error: No se pudo generar el numero de comprobante'
        return super(comprobantes, self).create(vals)

    @api.depends('numero_comprobante')
    def _compute_validation_result(self):
        for record in self:
            if record.tipo_comprobante == 'consumidor':
                record.validation_result = len(record.numero_comprobante) == 11
            elif record.tipo_comprobante == 'credito_fiscal':
                record.validation_result = len(record.numero_comprobante) == 11

            else:
                record.validation_result = False
