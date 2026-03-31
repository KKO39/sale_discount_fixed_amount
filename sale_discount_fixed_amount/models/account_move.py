from odoo import fields, models, api
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"


    def _prepare_product_base_line_for_taxes_computation(self, line):
        base_line = super()._prepare_product_base_line_for_taxes_computation(line)
        
        if line.display_type in ('line_section', 'line_note'):
            return base_line
            
        if line.quantity and line.discount_amount:
            # First apply percentage discount
            price_unit_after_percentage = base_line['price_unit'] * (1 - base_line['discount'] / 100.0)
            
            # Then apply fixed discount per unit
            price_unit_after_both = price_unit_after_percentage - (line.discount_amount / line.quantity)
            
            # Ensure price doesn't go negative
            if price_unit_after_both < 0:
                price_unit_after_both = 0
            
            base_line['price_unit'] = price_unit_after_both
            base_line['discount'] = 0.0  # We've already applied percentage discount
        
        return base_line
    
    def _post(self, soft=True):

        for move in self.filtered(lambda m: m.move_type in (
            'out_invoice', 'out_refund', 'in_invoice', 'in_refund'
        )):
            discount_account_id = self.env['ir.config_parameter'].sudo().get_param(
                'sale.discount_account_id'
            )
            if not discount_account_id:
                raise UserError(_("Please configure a Discount Account in Accounting Settings."))
            discount_account_id = int(discount_account_id)

            discount_lines = move.invoice_line_ids.filtered(lambda l: l.discount_amount > 0)
            if not discount_lines:
                continue

            total_discount = sum(discount_lines.mapped('discount_amount'))
            revenue_account = discount_lines[0].account_id

            line_commands = [
                (0, 0, {
                    'name': 'Fixed Discount',
                    'account_id': discount_account_id,
                    'debit': total_discount,
                    'credit': 0.0,
                    'display_type':'cogs',
                    'partner_id': move.partner_id.id,
                    'currency_id': move.currency_id.id,
                    'amount_currency': total_discount,
                }),
                (0, 0, {
                    'name': 'Discount Offset',
                    'account_id': revenue_account.id,
                    'debit': 0.0,
                    'credit': total_discount,
                    'display_type':'cogs',
                    'partner_id': move.partner_id.id,
                    'currency_id': move.currency_id.id,
                    'amount_currency': -total_discount,
                }),
            ]

            move.write({'line_ids': line_commands})

        return super()._post(soft=soft)