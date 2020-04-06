# Copyright (C) 2020 Konos
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#!/usr/bin/env python
# encoding: utf-8 
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime
import requests
import xml.etree.ElementTree as ET
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
                'connector_dicom.partner_dicom_action').read()[0]
        if len(dicom_ids) > 0:
            action['domain'] = [('id', 'in', dicom_ids.ids)]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def onchange_documents(self):
        conf = self.env["ir.config_parameter"].sudo()
        username = conf.get_param("dicom.user")
        password = conf.get_param("dicom.password")
        url = conf.get_param("dicom.url")
        headers = {'content-type': 'text/xml'}
        rut = self.vat.replace('-', '').replace('CL', '')
        form = '''
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:get="http://cl.equifax.com/schema/Platinum360/GetInformePlatinum360BReq">
    <soapenv:Header/> 
    <soapenv:Body>
        <get:getInformePlatinum360Request> 
        <get:Username>%s</get:Username> 
        <get:Password>%s</get:Password> 
        <get:RUT>%s</get:RUT> 
        <get:SerialNumber></get:SerialNumber> 
        <get:IdTransaction></get:IdTransaction> 
        <get:Platform>6</get:Platform> 
        <get:Channel>6</get:Channel> 
        <get:AditionalInformation></get:AditionalInformation> 
        <get:BoletinConcursal></get:BoletinConcursal> 
        <get:EspecialInformation>
            <!--Zero or more repetitions:--> <get:EspecialInformationType>
            <get:Section></get:Section> 
            </get:EspecialInformationType>
            </get:EspecialInformation> 
        </get:getInformePlatinum360Request>
    </soapenv:Body> 
</soapenv:Envelope>
'''  %(username, password, rut)
        encoded_request = form.encode('utf-8')
        response = requests.post(url,headers = headers,data = encoded_request)
        if response==False:
            raise UserError(_('Connection Error'))
        Count = 0
        tree = ET.fromstring(response.text)
        result = {}
        for item in tree.getiterator():
            if Count == 7:
                self.dicom_score = item.text
                self.dicom_date = fields.Date.context_today(self)
            Count += 1
            

    @api.one
    def update_dicom(self):
        self.onchange_documents()