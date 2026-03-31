from odoo import fields, models, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    discount_account_id = fields.Many2one(
        'account.account',
        string='Discount Account',
        config_parameter='sale.discount_account_id'
    )