# -*- coding: utf-8 -*-
# from odoo import http


# class Comprobantes(http.Controller):
#     @http.route('/comprobantes/comprobantes', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/comprobantes/comprobantes/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('comprobantes.listing', {
#             'root': '/comprobantes/comprobantes',
#             'objects': http.request.env['comprobantes.comprobantes'].search([]),
#         })

#     @http.route('/comprobantes/comprobantes/objects/<model("comprobantes.comprobantes"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('comprobantes.object', {
#             'object': obj
#         })
