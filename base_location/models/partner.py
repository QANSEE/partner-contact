# -*- coding: utf-8 -*-
#
#
#    Author: Nicolas Bessi. Copyright Camptocamp SA
#    Contributor: Pedro Manuel Baeza <pedro.baeza@serviciosbaeza.com>
#                 Ignacio Ibeas <ignacio@acysos.com>
#                 Alejandro Santana <alejandrosantana@anubia.es>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
from openerp import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'
    zip_id = fields.Many2one('res.better.zip', 'City/Location')

    @api.one
    @api.onchange('zip_id')
    def onchange_zip_id(self):
        if self.zip_id:
            self.zip = self.zip_id.name
            self.city = self.zip_id.city
            self.state_id = self.zip_id.state_id
            self.country_id = self.zip_id.country_id

    @api.one
    def write(self, vals):
        """ Ensure the zip_id is filled whenever possible. This is useful in
        case segmentation is done on this field.
        Try to match a zip_id based on country/zip/city or country/zip.
        """
        if 'zip_id' not in vals and (
            'city' in vals or
            'zip' in vals or
            'country_id' in vals):
            domain = []
            zip_ids = []
            values = {}

            if 'country_id' in vals:
                country_id = vals['country_id']
            else:
                country_id = self.country_id.id
            if 'zip' in vals:
                zipcode = vals['zip']
            else:
                zipcode = self.zip
            if 'city' in vals:
                city = vals['city']
            else:
                city = self.city

            if country_id:
                domain.append(('country_id', '=', country_id))
            if zipcode:
                domain.append(('name', '=', zipcode))
            if city:
                zip_ids = self.env['res.better.zip'].search(domain + [('city', '=', city)])
            if not city or not zip_ids:
                zip_ids = self.env['res.better.zip'].search(domain)

            if zip_ids:
                vals['zip_id'] = zip_ids[0].id

        return super(ResPartner, self).write(vals)

    def _address_fields(self, cr, uid, context=None):
        """ Returns the list of address fields that are synced from the parent
        when the `use_parent_address` flag is set. """
        return super(ResPartner, self)._address_fields(cr, uid, context=context) + ['zip_id']
