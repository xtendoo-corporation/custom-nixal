from odoo import fields, models, tools


class NixalBudgetReport(models.Model):
    """Planned (account_budget_oca lines) vs real (analytic lines) amounts of
    the Nixal analytic accounts, at the grain analytic account + month, so the
    dashboards can group by company, plan, account and period.

    Signs follow the analytic lines: income positive, expenses negative, so
    planned amounts must be entered with the same sign.
    """

    _name = "nixal.budget.report"
    _description = "Previsto vs real por cuenta analítica"
    _auto = False
    _order = "date desc, analytic_account_id"

    company_id = fields.Many2one("res.company", readonly=True)
    plan_id = fields.Many2one("account.analytic.plan", string="Plan analítico", readonly=True)
    analytic_account_id = fields.Many2one("account.analytic.account", string="Cuenta analítica", readonly=True)
    date = fields.Date(readonly=True)
    planned_amount = fields.Float(string="Previsto", readonly=True)
    real_amount = fields.Float(string="Real", readonly=True)
    deviation = fields.Float(string="Desviación (real - previsto)", readonly=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f"""
            CREATE OR REPLACE VIEW {self._table} AS (
                SELECT row_number() OVER () AS id, g.*, g.real_amount - g.planned_amount AS deviation
                FROM (
                    SELECT u.company_id, u.plan_id, u.analytic_account_id,
                           date_trunc('month', u.date)::date AS date,
                           SUM(u.planned_amount) AS planned_amount,
                           SUM(u.real_amount) AS real_amount
                    FROM (
                    SELECT l.company_id,
                           aa.plan_id,
                           l.analytic_account_id,
                           l.date_from AS date,
                           l.planned_amount AS planned_amount,
                           0.0 AS real_amount
                    FROM crossovered_budget_lines l
                    JOIN account_analytic_account aa ON aa.id = l.analytic_account_id
                    UNION ALL
                    SELECT al.company_id,
                           aa.plan_id,
                           al.account_id AS analytic_account_id,
                           al.date,
                           0.0 AS planned_amount,
                           al.amount AS real_amount
                    FROM account_analytic_line al
                    JOIN account_analytic_account aa ON aa.id = al.account_id
                    WHERE aa.company_id IS NOT NULL
                    ) u
                    GROUP BY u.company_id, u.plan_id, u.analytic_account_id, date_trunc('month', u.date)
                ) g
            )
        """)
