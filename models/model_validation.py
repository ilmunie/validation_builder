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

    name = fields.Char(string="Name", required=True)
    active_rec = fields.Boolean(default=True)
    model_id = fields.Many2one('ir.model', domain=[('model', 'in', ('product.product','product.template','res.partner','crm.lead','sale.order','account.move', 'purchase.order','stock.picking', 'stock.picking'))])
    model_name = fields.Char(related='model_id.model')
    line_ids = fields.One2many('model.validation.line', 'config_id', required=True)
    domain_trigger = fields.Char(required=True)


class ModelValidationLine(models.Model):
    _name = 'model.validation.line'

    model_id = fields.Many2one(related='config_id.model_id', store=True,)
    model_name = fields.Char(related='model_id.model', store=True)
    config_id = fields.Many2one('model.validation')
    domain_condition = fields.Selection(selection=[('match','Match'),('no_match','No Match')], required=True)
    domain_to_check = fields.Char(required=True)
    validation_type = fields.Selection(selection=[('warning', 'Warning'), ('exception', 'Raise Exception')], required=True)
    validation_message = fields.Text(required=True)
    active_rec = fields.Boolean(default=True, required=True)
    register_in_chatter = fields.Boolean()


class ModelValidatorMixin(models.AbstractModel):
    _name = 'model.validator.mixing'


    def write(self, vals):
        res = super().write(vals)
        validation_configs_to_check = self.env['model.validation'].search([('model_id', '=', self._name), ('active_rec', '=', True)])
        if validation_configs_to_check:
            messages = []
            error = False
            for validation_config_to_check in validation_configs_to_check:
                conditions = safe_eval(validation_config_to_check.domain_trigger)
                conditions.append(('id', '=', self.id))
                result = self.env[self._name].search_count(conditions)
                if result and result > 0:
                    for validation_rule in validation_config_to_check.line_ids.filtered(lambda x: x.active_rec):
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
                            with self.pool.cursor() as cr:
                                if validation_rule.validation_type == 'exception':
                                    error = True
                                    messages.append(f'ERROR | {self.display_name} | {validation_rule.validation_message}')
                                    if validation_rule.register_in_chatter:
                                        new_self = self.with_env(self.env(cr=cr))
                                        new_self.message_post(body=f'ERROR | {self.display_name} | {validation_rule.validation_message}')
                                else:
                                    messages.append(f'INFO | {self.display_name} | {validation_rule.validation_message}')
                                    if validation_rule.register_in_chatter:
                                        new_self = self.with_env(self.env(cr=cr))
                                        new_self.message_post(body=f'INFO | {self.display_name} | {validation_rule.validation_message}')
                if messages:
                    if error:
                        raise ValidationError('\n\n'.join(messages))
                    else:
                        for message in messages:
                            self.env.user.notify_warning(sticky=True, message=message)
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
