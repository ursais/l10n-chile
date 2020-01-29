# Copyright (C) 2020 Konos
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from datetime import datetime
import requests
import logging
_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"


    dicom_score = fields.Char(
        compute="_get_dicom", inverse="_set_dicom", string="Dicom Score")
    dicom_date = fields.Date(
        compute="_get_dicom", inverse="_set_dicom", string="Dicom Date")
    dicom_count = fields.Integer(
        compute="_get_dicom_count", string="Dicom Count")
    dicom_ids = fields.Many2many(
        "partner.dicom", string='Dicoms', compute="_get_dicom_count",
        readonly=True, copy=False)

    def _get_dicom(self):
        dicom = self.env['partner.dicom']
        for record in self:
            partner_dicom = dicom.search([('partner', '=', record.id)],
                                         limit=1, order='date desc')
            if partner_dicom:
                record.dicom_date = partner_dicom.date
                record.dicom_score = partner_dicom.dicom_score
                if partner_dicom.dicom_score < "999":
                    record.dicom_ok = True
                else:
                    record.dicom_ok = False

    def _set_dicom(self):
        for record in self:
            if record.dicom_score and record.dicom_date:
                if not self._dicom_exist():
                    data = {
                    'dicom_score': record.dicom_score,
                    'creation_date': fields.Date.context_today(record),
                    'date': self.dicom_date,
                    'partner': record.id}
                    self.env['partner.dicom'].create(data)
            else:
                _logger.warning("Fecha")
                _logger.warning(self.dicom_date)
                _logger.warning(record.dicom_score)

    def _dicom_exist(self):
        dicom_model = self.env['partner.dicom']
        for record in self:
            dicom_found = dicom_model.search([
                ('partner','=', record.id),
                ('date','=', record.dicom_date)])
            if dicom_found:
                return True
            else:
                return False

    def _get_dicom_count(self):
        dicom = self.env['partner.dicom']
        for record in self:
            partner_dicom = dicom.search([('partner', '=', record.id)])
            if partner_dicom:
                record.dicom_count = dicom.search_count([
                    ('partner', '=', record.id)])
                record.dicom_ids = partner_dicom.ids
            else:
                record.dicom_count = 0

    @api.multi
    def partner_dicom_action(self):
        dicom_ids = self.mapped('dicom_ids')
        action = \
            self.env.ref(
                'manantial_partner_dicom.partner_dicom_action').read()[0]
        if len(dicom_ids) > 0:
            action['domain'] = [('id', 'in', dicom_ids.ids)]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def onchange_document(self):
        conf = self.env["ir.config_parameter"].sudo()
        user = conf.get_param("partner.dicom.user")
        password = conf.get_param("partner.dicom.password")
        baseurl = conf.get_param("partner.dicom.baseurl")
        headers = {'content-type': 'text/xml'}
        rut = self.vat.replace('-', '').replace('CL', '')
        soap_envelope = '''
<soapenv:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
xmlns:xsd="http://www.w3.org/2001/XMLSchema"
xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
xmlns:app="http://app.gru01.wse.equifax.cl">
<soapenv:Header/>
<soapenv:Body>
<app:getInforme
soapenv:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
<Rut>%s</Rut>
<Serie></Serie>
<Usuario>%s</Usuario>
<Clave>%s</Clave>
<Descripcion></Descripcion>
</app:getInforme>
</soapenv:Body>
</soapenv:Envelope>
''' % (rut, user, password)
        _logger.warning(soap_envelope)
        response = requests.session().post(baseurl, data=soap_envelope,
                                           headers=headers)
        if response.status_code != 200:
            raise Exception(response.text)
        else:
            _logger.warning("Conectado")

    @api.one
    def update_dicom(self):
        self.onchange_document()
