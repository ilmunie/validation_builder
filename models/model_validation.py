from odoo import api,models,fields,_
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import ValidationError

class ModelValidation(models.Model):
    _name = 'model.validation'

    @api.model
    def name_get(self):
        res = []
        for rec in self:
            name = rec.name if rec.name else ''
            name += rec.model_id.name + ' (' + rec.model_id.model + ')'
            res.append((rec.id, name))
        return res

    name = fields.Char(string="Name")
    active = fields.Boolean(default=True)
    model_id = fields.Many2one('ir.model', domain=[('model', 'in', ('product.product','product.template','res.partner','crm.lead','sale.order','account.move', 'purchase.order','stock.picking', 'stock.picking'))])
    model_name = fields.Char(related='model_id.model')
    line_ids = fields.One2many('model.validation.line', 'config_id')
    domain_trigger = fields.Char()


class ModelValidationLine(models.Model):
    _name = 'model.validation.line'

    model_id = fields.Many2one(related='config_id.model_id', store=True)
    model_name = fields.Char(related='model_id.model', store=True)
    config_id = fields.Many2one('model.validation')
    domain_condition = fields.Selection(selection=[('match','Match'),('no_match','No Match')])
    domain_to_check = fields.Char()
    validation_type = fields.Selection(selection=[('warning', 'Warning'), ('exception', 'Raise Exception')])
    validation_message = fields.Text()
    active = fields.Boolean(default=True)
    register_in_chatter = fields.Boolean()


class ModelValidatorMixin(models.AbstractModel):
    _name = 'model.validator.mixing'


    def write(self, vals):
        res = super().write(vals)
        validation_configs_to_check = self.env['model.validation'].search([('model_id', '=', self._name), ('active', '=', True)])
        if validation_configs_to_check:
            messages = []
            error = False
            for validation_config_to_check in validation_configs_to_check:
                conditions = safe_eval(validation_config_to_check.domain_trigger)
                conditions.append(('id', '=', self.id))
                result = self.env[self._name].search_count(conditions)
                if result and result > 0:
                    for validation_rule in validation_config_to_check.line_ids.filtered(lambda x: x.active):
                        conditions = safe_eval(validation_rule.domain_to_check)
                        conditions.append(('id', '=', self.id))
                        result = self.env[self._name].search_count(conditions)
                        trigger_rule = False
                        if validation_rule.domain_condition == 'match':
                            if result and result > 0:
                                trigger_rule = True
                        else:
                            if not result:
                                trigger_rule = True
                        if trigger_rule:
                            if validation_rule.validation_type == 'exception':
                                error = True
                                messages.append(f'ERROR | {self.display_name} | {validation_rule.validation_message}')
                                if validation_rule.register_in_chatter:
                                    self.message_post(body=f'ERROR | {self.display_name} | {validation_rule.validation_message}')
                            else:
                                messages.append(f'INFO | {self.display_name} | {validation_rule.validation_message}')
                                if validation_rule.register_in_chatter:
                                    self.message_post(body=f'INFO | {self.display_name} | {validation_rule.validation_message}')
                if messages:
                    if error:
                        raise ValidationError('\n'.join(messages))
                    else:
                        self.env.user.notify_warning(message='\n'.join(messages))
        return res


class CrmLead(models.Model, ModelValidatorMixin):
    _inherit = 'crm.lead'


class SaleOrder(models.Model, ModelValidatorMixin):
    _inherit = 'sale.order'


class AccountMove(models.Model, ModelValidatorMixin):
    _inherit = 'account.move'


class PurchaseOrder(models.Model, ModelValidatorMixin):
    _inherit = 'purchase.order'


class StockPicking(models.Model, ModelValidatorMixin):
    _inherit = 'stock.picking'


class ProductProduct(models.Model, ModelValidatorMixin):
    _inherit = 'product.product'


class ProductTemplate(models.Model, ModelValidatorMixin):
    _inherit = 'product.template'


class ResPartner(models.Model, ModelValidatorMixin):
    _inherit = 'res.partner'
