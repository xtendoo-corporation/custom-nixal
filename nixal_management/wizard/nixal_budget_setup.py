import calendar
from datetime import date

from odoo import _, fields, models
from odoo.exceptions import UserError

from .nixal_analytic_structure import BUDGET_POSITIONS, PLAN_POSITION


class NixalBudgetSetupWizard(models.TransientModel):
    _name = "nixal.budget.setup.wizard"
    _description = "Crear presupuestos anuales Nixal"

    year = fields.Integer(required=True, default=lambda self: fields.Date.today().year)
    result_message = fields.Text(readonly=True)

    def _compute_display_name(self):
        for wizard in self:
            wizard.display_name = _("Crear presupuestos Nixal")

    def _get_positions(self, company):
        """name -> account.budget.post for `company`, creating the missing ones."""
        Post = self.env["account.budget.post"]
        Account = self.env["account.account"].with_company(company)
        positions = {}
        for name, prefixes in BUDGET_POSITIONS.items():
            post = Post.search([("name", "=", name), ("company_id", "=", company.id)], limit=1)
            if not post:
                accounts = Account.search(
                    [("company_ids", "in", company.id)]
                ).filtered(lambda a: a.code and a.code.startswith(tuple(prefixes)))
                if not accounts:
                    raise UserError(_(
                        "La compañía %(company)s no tiene cuentas contables que "
                        "empiecen por %(prefixes)s.",
                        company=company.name, prefixes=", ".join(prefixes),
                    ))
                post = Post.create({
                    "name": name,
                    "company_id": company.id,
                    "account_ids": [(6, 0, accounts.ids)],
                })
            positions[name] = post
        return positions

    def action_create_budgets(self):
        self.ensure_one()
        Budget = self.env["crossovered.budget"]
        analytic_accounts = self.env["account.analytic.account"].search([
            ("plan_id.name", "in", list(PLAN_POSITION)),
            ("company_id", "!=", False),
        ])
        if not analytic_accounts:
            raise UserError(_("No hay cuentas analíticas Nixal. Crea antes la estructura analítica."))

        months = [
            (date(self.year, m, 1), date(self.year, m, calendar.monthrange(self.year, m)[1]))
            for m in range(1, 13)
        ]
        created = []
        for company in analytic_accounts.company_id:
            name = _("Presupuesto %(company)s %(year)s", company=company.name, year=self.year)
            if Budget.search_count([("name", "=", name), ("company_id", "=", company.id)]):
                continue
            positions = self._get_positions(company)
            lines = []
            for account in analytic_accounts.filtered(lambda a: a.company_id == company):
                post = positions[PLAN_POSITION[account.plan_id.name]]
                for date_from, date_to in months:
                    lines.append((0, 0, {
                        "analytic_account_id": account.id,
                        "general_budget_id": post.id,
                        "date_from": date_from,
                        "date_to": date_to,
                        "planned_amount": 0.0,
                    }))
            Budget.create({
                "name": name,
                "company_id": company.id,
                "date_from": date(self.year, 1, 1),
                "date_to": date(self.year, 12, 31),
                "crossovered_budget_line_ids": lines,
            })
            created.append(company.name)

        self.result_message = (
            _("Presupuestos creados para: %s", ", ".join(created))
            if created else _("Los presupuestos de %s ya existían.", self.year)
        )
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Presupuestos Nixal"),
                "message": self.result_message,
                "sticky": True,
            },
        }
