from odoo import fields, models, api

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    
    discount_amount = fields.Float(string="Discount Amount")
    
    @api.depends('quantity', 'discount', 'price_unit', 'tax_ids', 'currency_id', 'discount_amount')
    def _compute_totals(self):
        # First, compute totals without our custom discount_amount
        result = super(AccountMoveLine, self)._compute_totals()
        
        for line in self:
            if line.display_type in ('line_section', 'line_note'):
                continue
                
            if line.quantity and line.discount_amount:
                # Calculate the price after percentage discount
                line_discount_price_unit = line.price_unit * (1 - (line.discount / 100.0))
                
                # Calculate total before fixed discount
                subtotal_before_fixed = line.quantity * line_discount_price_unit
                
                # Apply fixed discount
                subtotal_after_fixed = subtotal_before_fixed - line.discount_amount
                
                # Ensure subtotal doesn't go negative
                if subtotal_after_fixed < 0:
                    subtotal_after_fixed = 0
                
                # Calculate effective price unit after both discounts
                effective_price_unit = subtotal_after_fixed / line.quantity if line.quantity else 0
                
                if line.tax_ids:
                    # Recompute taxes with the effective price unit
                    taxes_res = line.tax_ids.compute_all(
                        effective_price_unit,
                        quantity=line.quantity,
                        currency=line.currency_id,
                        product=line.product_id,
                        partner=line.partner_id,
                        is_refund=line.is_refund,
                    )
                    line.price_subtotal = taxes_res['total_excluded']
                    line.price_total = taxes_res['total_included']
                else:
                    line.price_subtotal = subtotal_after_fixed
                    line.price_total = subtotal_after_fixed
                
                # line.price_tax = line.price_total - line.price_subtotal
        
        return result
    
    