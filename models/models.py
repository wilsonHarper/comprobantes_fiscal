# -*- coding: utf-8 -*-

from odoo import models, fields, api


class comprobantes(models.Model):
    _name = 'comprobantes.comprobantes'
    _description = 'comprobantes.comprobantes'

    #Buscar todos los tipos de comprobante, utilizarlo en el dicionario
    TIPO_COMPROBANTE =[
        ('consumidor', 'Consumidor'),
        ('credito_fiscal', 'Credito fiscal'),
    ]

    prefijo = fields.Char(string='Prefijo', required=True)
    numero_comprobante = fields.Char(string='Número comprobante fiscal', required=True, copy=False, default='Nuevo')
    tipo = fields.Selection(TIPO_COMPROBANTE, string='Tipo de comprobante fiscal', required=True)
    #sequence = fields.Char(string='Secuencia', readonly=True, copy=False, default=lambda self: self.create())


    @api.model
    def create(self, vals):
        if vals.get('numero_comprobante', 'Nuevo') == 'Nuevo':
            vals['numero_comprobante'] = self.env['ir.sequence'].next_by_code('comprobantes.comprobantes.sequence') or 'Error: No se pudo general el numero de comrpbante'
            
            return super(comprobantes, self).create(vals)
        
class account_invoice(models.Model):
    _inherit = 'account.move'
    
    comprobante_id = fields.Many2one('comprobantes.comprobantes', string='Comprobante Fiscal')