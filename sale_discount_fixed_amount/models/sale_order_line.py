from odoo import fields, models, api

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    discount_amount = fields.Float(string='Discount Amount', default=0.0)
    
    def _prepare_base_line_for_taxes_computation(self, **kwargs):
        """Override to apply fixed discount amount into tax base."""
        self.ensure_one()
        company = self.order_id.company_id or self.env.company

        # Calculate the effective unit price after both discounts
        price_unit = self.price_unit
        
        if self.product_uom_qty:
            # Calculate total amount after percentage discount
            total_before_fixed = self.price_unit * self.product_uom_qty * (1 - self.discount / 100.0)
            
            # Subtract fixed discount
            total_after_fixed = total_before_fixed - self.discount_amount
            
            # Calculate effective unit price
            price_unit = total_after_fixed / self.product_uom_qty if self.product_uom_qty else self.price_unit

        base_values = {
            'tax_ids': self.tax_ids,
            'quantity': self.product_uom_qty,
            'partner_id': self.order_id.partner_id,
            'currency_id': self.order_id.currency_id or company.currency_id,
            'rate': self.order_id.currency_rate,
            'name': self.name,
            'price_unit': price_unit,
            'discount': 0.0,  # Already applied in calculation
        }

        if self._is_global_discount():
            base_values['special_type'] = 'global_discount'
        elif self.is_downpayment:
            base_values['special_type'] = 'down_payment'

        base_values.update(kwargs)

        return self.env['account.tax']._prepare_base_line_for_taxes_computation(
            self, **base_values
        )


    # ---------------------------------------------------------
    # COMPUTE AMOUNTS (UNCHANGED, BUT DEPENDS UPDATED)
    # ---------------------------------------------------------
    @api.depends(
        'product_uom_qty',
        'discount',
        'discount_amount',
        'price_unit',
        'tax_ids'
    )
    def _compute_amount(self):
        AccountTax = self.env['account.tax']

        for line in self:
            company = line.company_id or self.env.company

            base_line = line._prepare_base_line_for_taxes_computation()
            AccountTax._add_tax_details_in_base_line(base_line, company)
            AccountTax._round_base_lines_tax_details([base_line], company)

            line.price_subtotal = base_line['tax_details']['total_excluded_currency']
            line.price_total = base_line['tax_details']['total_included_currency']
            line.price_tax = line.price_total - line.price_subtotal

    
    def _prepare_invoice_line(self, **optional_values):
        self.ensure_one()
        invoice_line_vals = super(SaleOrderLine, self)._prepare_invoice_line(**optional_values)
        invoice_line_vals['discount_amount'] = self.discount_amount
        return invoice_line_vals