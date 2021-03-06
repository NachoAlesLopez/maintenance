# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, _
from datetime import timedelta


class MaintenancePlan(models.Model):
    _inherit = 'maintenance.plan'

    planned_activity_ids = fields.One2many(
        'maintenance.planned.activity', 'maintenance_plan_id',
        'Planned Activities'
    )


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    def _create_new_request(self, maintenance_plan):
        existing_requests = self.maintenance_ids.filtered(
            lambda l: l.maintenance_plan_id.id == maintenance_plan.id)
        super(MaintenanceEquipment, self)._create_new_request(maintenance_plan)
        new_requests = self.maintenance_ids.filtered(
            lambda l: l.maintenance_plan_id.id == maintenance_plan.id and
            l.id not in existing_requests.ids)
        # Create planned activities for the new requests
        for request in new_requests:
            for planned_activity in maintenance_plan.planned_activity_ids:
                self.env['mail.activity'].create({
                    'activity_type_id': planned_activity.activity_type_id.id,
                    'note': _('Activity automatically generated from '
                              'maintenance plan'),
                    'user_id': planned_activity.user_id.id or self.env.user.id,
                    'res_id': request.id,
                    'res_model_id': self.env.ref(
                        'maintenance.model_maintenance_request').id,
                    'date_deadline': fields.Date.from_string(
                        request.schedule_date) - timedelta(
                        days=planned_activity.date_before_request),
                })
