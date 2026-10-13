from odoo import _, fields, models
from odoo.exceptions import UserError

from .nixal_analytic_structure import ROOT_PLAN, STRUCTURE

LEGACY_PLAN_NAMES = ["Categorías Nixal", "Porcino"]
LEGACY_SPECIES = ["Vacuno", "Porcino", "Ovino"]


class NixalAnalyticSetupWizard(models.TransientModel):
    _name = "nixal.analytic.setup.wizard"
    _description = "Crear planes y cuentas analíticas Nixal"

    result_message = fields.Text(readonly=True)

    def _compute_display_name(self):
        for wizard in self:
            wizard.display_name = _("Crear estructura analítica Nixal")

    def _get_root_plan(self):
        """Reuse Odoo's default root plan (renamed) so that every account
        below it is stored in account.analytic.line.account_id, the only
        column account_budget_oca compares budgets against."""
        plan = self.env.ref("analytic.analytic_plan_projects")
        if plan.name != ROOT_PLAN:
            plan.name = ROOT_PLAN
        return plan

    def _cleanup_legacy(self, root):
        Plan = self.env["account.analytic.plan"]
        Account = self.env["account.analytic.account"]
        # Species accounts of the previous setup, only if never used.
        legacy_accounts = Account.search([
            ("name", "in", LEGACY_SPECIES), ("plan_id", "=", root.id),
        ])
        if legacy_accounts and not self.env["account.analytic.line"].search_count(
            [("account_id", "in", legacy_accounts.ids)]
        ):
            legacy_accounts.unlink()
        for plan in Plan.search([("name", "in", LEGACY_PLAN_NAMES), ("id", "!=", root.id)]):
            if not plan.account_ids and not plan.children_ids:
                plan.unlink()

    def action_create_structure(self):
        self.ensure_one()
        Company = self.env["res.company"].sudo()
        Plan = self.env["account.analytic.plan"]
        Account = self.env["account.analytic.account"]

        companies = {c.name: c for c in Company.search([])}
        needed = {row[0] for row in STRUCTURE}
        missing = needed - set(companies)
        if missing:
            raise UserError(_(
                "Faltan compañías: %s. Ejecuta antes 'Crear compañías'.",
                ", ".join(sorted(missing)),
            ))

        root = self._get_root_plan()
        self._cleanup_legacy(root)

        plans_created = accounts_created = 0
        for company_name, plan_name, account_names in STRUCTURE:
            company = companies[company_name]
            plan = Plan.search([("name", "=", plan_name), ("parent_id", "=", root.id)], limit=1)
            if not plan:
                plan = Plan.create({"name": plan_name, "parent_id": root.id})
                plans_created += 1
            existing = set(Account.with_context(active_test=False).search([
                ("plan_id", "=", plan.id), ("company_id", "=", company.id),
            ]).mapped("name"))
            to_create = [
                {"name": name, "plan_id": plan.id, "company_id": company.id}
                for name in account_names if name not in existing
            ]
            if to_create:
                Account.create(to_create)
                accounts_created += len(to_create)

        self.result_message = _(
            "Planes creados: %(plans)s. Cuentas analíticas creadas: %(accounts)s.",
            plans=plans_created, accounts=accounts_created,
        )
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Estructura analítica Nixal"),
                "message": self.result_message,
                "sticky": True,
            },
        }
