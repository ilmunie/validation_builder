# validation_builder
Odoo v15 module that allows to configure fields validation for diferent conditions in any model. The module patchs the write method, evaluating ui configurable validations in order to raise or send warning messages.

Add different configurations in Settings/Technical/Model Validation Configuration


To add another model to the validation builter you have to do de following steps:

1. Add module as dependency (if necesary)
2. Include the desired module technical name in domain of field 'model_id' in model 'model.validation'
2. Instance the python class of your desired model with the abstact class ModelValidatorMixin (examples in end of file 'model_validation.py')

