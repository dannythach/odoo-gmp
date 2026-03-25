{
    'name': 'My HR Extensions',
    'version': '1.0',
    'category': 'Human Resources',
    'summary': 'Add custom fields to the HR Employee module.',
    'author': 'Your Name',
    'depends': ['hr'], # Quan trọng: Phụ thuộc vào module 'hr' gốc
    'data': [
        'views/hr_employee_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}