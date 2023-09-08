# -*- coding: utf-8 -*-
{
    'name': 'validation_builder',
    'version': '2.0',
    'category': 'Base',
    'sequence': 15,
    'summary': 'Odoo v15 module that allows to configure fields validation for diferent conditions in any model. The module patchs the write method, evaluating ui configurable validations in order to raise or send warning messages',
    'description': """To add another model to the validation builter you have to do de following steps:
                   1. Add module as dependency (if necesary)
                   2. Include the desired module technical name in domain of field 'model_id' in model 'model.validation'
                   3. Instance the python class of your desired model with the abstact class ModelValidatorMixin (examples in end of file 'model_validation.py')
                   """,
    'website': '',
    'depends': [
        'crm',
        'sale',
        'purchase',
        'stock',
        'account',
        'web_notify',
    ],
    'data': [
        'views/model_validation_form_views.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
