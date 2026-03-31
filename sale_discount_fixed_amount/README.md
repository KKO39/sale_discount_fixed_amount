# Sale Discount Fixed Amount

## Overview
This module adds a **fixed discount amount** feature to Odoo Sales and Invoicing.

In standard Odoo, discounts are usually handled as percentages. This module allows users to enter an additional **fixed discount amount per line** on:

- **Sales Order Lines**
- **Customer Invoice Lines**

The module also posts the fixed discount to a dedicated **Discount Account** configured in Accounting Settings.

## Main Features

- Adds **Discount Amount** field on sale order lines.
- Carries the fixed discount amount from **Sales Order** to **Invoice**.
- Recalculates line subtotal and taxes after applying:
  1. Percentage discount
  2. Fixed discount amount
- Adds **Discount Amount** field on invoice lines.
- Creates accounting entries for total fixed discount during invoice posting.
- Lets users configure a **Discount Account** from Accounting settings.

## Technical Summary

### Extended Models
- `sale.order.line`
- `account.move.line`
- `account.move`
- `res.config.settings`

### Added Fields
- `discount_amount` on `sale.order.line`
- `discount_amount` on `account.move.line`
- `discount_account_id` on `res.config.settings`

### Views Updated
- Sales Order form view
- Customer Invoice form view
- Accounting Settings view

## Dependencies
This module depends on:

- `base`
- `sale`
- `account`

## Installation
1. Copy the module folder into your custom addons path.
2. Restart the Odoo server.
3. Update the Apps list.
4. Install the module **Sale Discount Fixed Amount**.

## Configuration
After installation:

1. Go to **Accounting > Configuration > Settings**.
2. Find the **Discount Account** setting.
3. Select the account that should be used to record fixed discount amounts.
4. Save the settings.

> Important: If the Discount Account is not configured, invoice posting will raise an error.

## How It Works

### Sales Order
On each sales order line, users can enter:

- **Unit Price**
- **Discount (%)**
- **Discount Amount**

The module calculates the effective line amount by:

1. Applying the percentage discount first.
2. Subtracting the fixed discount amount from the line total.
3. Recomputing taxes based on the adjusted value.

### Invoice
When the sales order is invoiced:

- The **Discount Amount** is transferred to the invoice line.
- Invoice totals are recalculated using the adjusted value.
- When the invoice is posted, the module creates journal lines for the total fixed discount.

## Example

### Example 1
- Quantity: `2`
- Unit Price: `100`
- Discount (%): `10`
- Discount Amount: `15`

Calculation:
- Total before discount = `2 x 100 = 200`
- After 10% discount = `180`
- After fixed discount = `165`

So the effective total before tax becomes **165**.

## File Structure

```text
sale_discount_fixed_amount/
├── __init__.py
├── __manifest__.py
├── README.md
├── models/
│   ├── __init__.py
│   ├── sale_order_line.py
│   ├── account_move.py
│   ├── account_move_line.py
│   └── res_config_settings.py
└── views/
    ├── sale_order_views.xml
    ├── account_move_views.xml
    └── res_config_settings_views.xml
```

## Notes
- The fixed discount is handled **in addition to** the standard percentage discount.
- The module is designed for accounting flows where fixed line discounts must be visible and posted separately.
- Make sure the selected Discount Account is valid for your company and chart of accounts.

## Author
- **Kay Khaing Oo**

## License
LGPL-3
