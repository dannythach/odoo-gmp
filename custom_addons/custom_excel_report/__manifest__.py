{
    'name': 'Custom Excel Report from Function',
    'version': '1.0',
    'category': 'Extra Tools',
    'summary': 'Tạo báo cáo Excel dựa trên Function và Template tùy chỉnh',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/excel_report_view.xml',
    ],
    'external_dependencies': {'python': ['openpyxl']},
    'installable': True,
    'application': True,
}