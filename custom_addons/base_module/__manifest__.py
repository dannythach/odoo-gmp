{
    'name': 'Base Module',
    'version': '1.0',
    'summary': 'Shared model',
    'description': 'Model dùng chung cho tất cả module khác',
    'author': 'Internal',
    'license': 'LGPL-3',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        "views/gmp_oitm_views.xml",
        "views/gmp_ouom_views.xml",
    ],
    'installable': True,
    'application': True,
}