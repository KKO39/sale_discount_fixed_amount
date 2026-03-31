{
    'name': 'Discount Fixed Accounting',
    'summary': 'Discount Fixed Accounting',
    'category': 'Customization/Customization',
    'description': """
        Discount Accounting
    """,
    'author': 'Kay Khaing Oo',
    'license': 'LGPL-3',
    'depends': ['base', 'sale', 'account'],
    'demo': [],
    'data': [
        'views/sale_order_views.xml',
        'views/account_move_views.xml',
        'views/res_config_settings_views.xml'
        ],
    'installable': True,
    'application': True,
    'currency': 'USD',
    'price': '0.00',
}