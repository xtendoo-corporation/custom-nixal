from odoo import _, fields, models
from odoo.exceptions import UserError

NO_TAX = [(6, 0, [])]

# Real FY 2024/2025 (Sep 2024 - Aug 2025) figures from "Ppto 24-25 2Oct.xlsx",
# used as the planned amount of the demo budget (that period is now closed,
# so it can be compared against the real actuals from the bulk import).
AGRI_BUDGET_FY2425 = {
    "Vacuno": {"income": 180485.14, "expense": 17141.55},
    "Porcino": {"income": 137044.66, "expense": 7140.89},
    "Ovino": {"income": 0.0, "expense": 0.0},
}


class NixalDemoImportWizard(models.TransientModel):
    _name = "nixal.demo.import.wizard"
    _description = "Importar un ejemplo real de flujo completo por línea de negocio"

    result_message = fields.Text(readonly=True)

    def _compute_display_name(self):
        for wizard in self:
            wizard.display_name = _("Importar ejemplo por línea de negocio")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _get_company(self, name):
        company = self.env["res.company"].search([("name", "=", name)], limit=1)
        if not company:
            raise UserError(_(
                "No existe la compañía '%s'. Ejecuta antes el asistente "
                "'Crear compañías Nixal'."
            ) % name)
        return company

    def _allow_company(self, company):
        """Return a copy of the wizard whose environment has `company`
        among the *allowed* companies for this request, regardless of
        which company the user currently has active in the top-right
        switcher - otherwise multi-company record rules block writes to
        that company's journal entries (e.g. when registering payments).
        """
        allowed = set(self.env.context.get("allowed_company_ids") or self.env.companies.ids)
        allowed.add(company.id)
        return self.with_context(allowed_company_ids=list(allowed))

    def _get_partner(self, name, **extra):
        partner = self.env["res.partner"].search(
            [("name", "=", name), ("company_id", "=", False)], limit=1
        )
        if not partner:
            vals = {"name": name, "is_company": True, "company_id": False}
            vals.update(extra)
            partner = partner.create(vals)
        return partner

    def _get_product(self, name, product_type):
        product = self.env["product.product"].search(
            [("name", "=", name), ("company_id", "=", False)], limit=1
        )
        if not product:
            product = product.create({
                "name": name,
                "type": product_type,
                "company_id": False,
                "invoice_policy": "order",
                # Bill on ordered quantities: there is no stock/receipt flow
                # involved in these demo examples.
                "purchase_method": "purchase",
            })
        return product

    def _get_agri_analytic_account(self, company, species):
        account = self.env["account.analytic.account"].search([
            ("company_id", "=", company.id),
            ("name", "=", species),
        ], limit=1)
        if not account:
            raise UserError(_(
                "No existe la cuenta analítica '%s' en NixAl Agri. Ejecuta "
                "antes el asistente 'Crear compañías Nixal'."
            ) % species)
        return account

    def _register_payment(self, moves, payment_date):
        wizard = self.env["account.payment.register"].with_context(
            active_model="account.move", active_ids=moves.ids
        ).create({"payment_date": payment_date})
        wizard.action_create_payments()

    def _notify(self, message):
        self.result_message = message
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Ejemplo Nixal importado"),
                "message": message,
                "sticky": True,
            },
        }

    # ------------------------------------------------------------------
    # Trade: compra a Alvinesa + transporte GEODIS -> venta a Lipsa-BP
    # ------------------------------------------------------------------
    def action_import_trade(self):
        self.ensure_one()
        return self._notify(self._do_import_trade())

    def _do_import_trade(self):
        company = self._get_company("Nixal Trade")
        self = self._allow_company(company)

        alvinesa = self._get_partner("Alvinesa", supplier_rank=1)
        geodis = self._get_partner("GEODIS", supplier_rank=1)
        lipsa = self._get_partner("Lipsa-BP Energía España", customer_rank=1)

        product_alcohol = self._get_product("Alcohol vínico a granel", "consu")
        product_transporte = self._get_product("Transporte de mercancía", "service")

        # Compra a Alvinesa - Fra. 20241710 (31/12/2024)
        po_alvinesa = self.env["purchase.order"].with_company(company).create({
            "partner_id": alvinesa.id,
            "company_id": company.id,
            "date_order": "2024-12-15 09:00:00",
            "order_line": [(0, 0, {
                "product_id": product_alcohol.id,
                "name": "Alcohol vínico a granel - Fra. 20241710",
                "product_qty": 1,
                "price_unit": 62557.80,
                "tax_ids": NO_TAX,
            })],
        })
        po_alvinesa.button_confirm()
        po_alvinesa.action_create_invoice()
        bill_alvinesa = po_alvinesa.invoice_ids
        bill_alvinesa.write({"invoice_date": "2024-12-31", "ref": "20241710"})
        bill_alvinesa.action_post()
        self._register_payment(bill_alvinesa, "2025-01-15")

        # Transporte GEODIS (abril 2025)
        po_geodis = self.env["purchase.order"].with_company(company).create({
            "partner_id": geodis.id,
            "company_id": company.id,
            "date_order": "2025-04-01 09:00:00",
            "order_line": [(0, 0, {
                "product_id": product_transporte.id,
                "name": "Transporte operación Alvinesa -> Lipsa-BP",
                "product_qty": 1,
                "price_unit": 71100.00,
                "tax_ids": NO_TAX,
            })],
        })
        po_geodis.button_confirm()
        po_geodis.action_create_invoice()
        bill_geodis = po_geodis.invoice_ids
        bill_geodis.write({"invoice_date": "2025-04-15"})
        bill_geodis.action_post()
        self._register_payment(bill_geodis, "2025-04-30")

        # Venta a Lipsa-BP - Fra. 2025/TOE/001 (10/01/2025)
        so_lipsa = self.env["sale.order"].with_company(company).create({
            "partner_id": lipsa.id,
            "company_id": company.id,
            "date_order": "2025-01-05 09:00:00",
            "order_line": [(0, 0, {
                "product_id": product_alcohol.id,
                "name": "Alcohol vínico a granel - Fra. 2025/TOE/001",
                "product_uom_qty": 1,
                "price_unit": 211281.77,
                "tax_ids": NO_TAX,
            })],
        })
        so_lipsa.action_confirm()
        invoice_lipsa = so_lipsa._create_invoices()
        invoice_lipsa.write({"invoice_date": "2025-01-10", "ref": "2025/TOE/001"})
        invoice_lipsa.action_post()
        self._register_payment(invoice_lipsa, "2025-01-20")

        return _(
            "Trade: compra Alvinesa (62.557,80€) + transporte GEODIS "
            "(71.100€) -> venta a Lipsa-BP (211.281,77€), todo facturado y cobrado/pagado."
        )

    # ------------------------------------------------------------------
    # NC: suscripción Alcodis
    # ------------------------------------------------------------------
    def action_import_nc(self):
        self.ensure_one()
        return self._notify(self._do_import_nc())

    def _do_import_nc(self):
        company = self._get_company("Nixal NC")
        self = self._allow_company(company)
        alcodis = self._get_partner("Alcodis", customer_rank=1)
        product_nc = self._get_product(
            "Suscripción anual - Market Intelligence", "service"
        )

        so_alcodis = self.env["sale.order"].with_company(company).create({
            "partner_id": alcodis.id,
            "company_id": company.id,
            "date_order": "2026-01-01 09:00:00",
            "order_line": [(0, 0, {
                "product_id": product_nc.id,
                "name": "Suscripción anual Market Intelligence 2026 - Alcodis",
                "product_uom_qty": 1,
                "price_unit": 16000.00,
                "tax_ids": NO_TAX,
            })],
        })
        so_alcodis.action_confirm()
        invoice_alcodis = so_alcodis._create_invoices()
        invoice_alcodis.write({"invoice_date": "2026-03-01"})
        invoice_alcodis.action_post()
        self._register_payment(invoice_alcodis, "2026-03-10")

        return _(
            "NC: contrato de suscripción anual Alcodis (16.000€, 2026-01-01 "
            "a 2027-01-01), facturado y cobrado en marzo 2026."
        )

    # ------------------------------------------------------------------
    # NixAl Agri: venta de terneros
    # ------------------------------------------------------------------
    def action_import_agri(self):
        self.ensure_one()
        return self._notify(self._do_import_agri())

    def _do_import_agri(self):
        company = self._get_company("NixAl Agri")
        self = self._allow_company(company)
        vacuno = self._get_agri_analytic_account(company, "Vacuno")
        comprador = self._get_partner(
            "Comprador de Terneros (genérico)", customer_rank=1
        )
        product_ternero = self._get_product("Venta de terneros/as", "consu")

        so_agri = self.env["sale.order"].with_company(company).create({
            "partner_id": comprador.id,
            "company_id": company.id,
            "date_order": "2026-08-20 09:00:00",
            "order_line": [(0, 0, {
                "product_id": product_ternero.id,
                "name": "Venta de terneros - agosto 2026",
                "product_uom_qty": 1,
                "price_unit": 28490.25,
                "tax_ids": NO_TAX,
                "analytic_distribution": {str(vacuno.id): 100.0},
            })],
        })
        so_agri.action_confirm()
        invoice_agri = so_agri._create_invoices()
        invoice_agri.write({"invoice_date": "2026-08-31"})
        invoice_agri.action_post()
        self._register_payment(invoice_agri, "2026-09-01")

        budget_msg = self._create_agri_budget(company)

        return _(
            "NixAl Agri: venta de terneros de agosto 2026 (28.490,25€, "
            "categoría analítica Vacuno) a un comprador genérico (el Excel "
            "no identifica al comprador real en esta hoja), facturada y "
            "cobrada.\n%s"
        ) % budget_msg

    def _create_agri_budget(self, company):
        """Demo 'presupuesto vs. real' for FY 2024/2025 (closed period),
        one line per species, using account_budget_oca."""
        name = "Presupuesto Ganadero FY 2024/2025"
        budget = self.env["crossovered.budget"].search([
            ("name", "=", name), ("company_id", "=", company.id),
        ], limit=1)
        if budget:
            return _("Presupuesto '%s' ya existía.") % name

        income_accounts = self.env["account.account"].search([
            ("company_ids", "in", company.id),
            ("account_type", "in", ("income", "income_other")),
        ])
        expense_accounts = self.env["account.account"].search([
            ("company_ids", "in", company.id),
            ("account_type", "in", (
                "expense", "expense_other", "expense_depreciation", "expense_direct_cost",
            )),
        ])
        post_income = self.env["account.budget.post"].create({
            "name": "Ingresos NixAl Agri",
            "company_id": company.id,
            "account_ids": [(6, 0, income_accounts.ids)],
        })
        post_expense = self.env["account.budget.post"].create({
            "name": "Gastos NixAl Agri",
            "company_id": company.id,
            "account_ids": [(6, 0, expense_accounts.ids)],
        })

        date_from, date_to = "2024-09-01", "2025-08-31"
        lines = []
        for species, amounts in AGRI_BUDGET_FY2425.items():
            analytic_account = self._get_agri_analytic_account(company, species)
            lines.append((0, 0, {
                "general_budget_id": post_income.id,
                "analytic_account_id": analytic_account.id,
                "date_from": date_from,
                "date_to": date_to,
                "planned_amount": amounts["income"],
            }))
            lines.append((0, 0, {
                "general_budget_id": post_expense.id,
                "analytic_account_id": analytic_account.id,
                "date_from": date_from,
                "date_to": date_to,
                # Expenses are budgeted as negative amounts, matching the
                # sign convention account_budget_oca uses for the actual
                # (practical_amount is -balance, i.e. negative for costs).
                "planned_amount": -amounts["expense"],
            }))

        self.env["crossovered.budget"].create({
            "name": name,
            "company_id": company.id,
            "date_from": date_from,
            "date_to": date_to,
            "crossovered_budget_line_ids": lines,
        })
        return _(
            "Presupuesto '%s' creado (previsión por especie de aquel año "
            "frente a lo realmente facturado)."
        ) % name

    # ------------------------------------------------------------------
    def action_import_all(self):
        self.ensure_one()
        messages = [
            self._do_import_trade(),
            self._do_import_nc(),
            self._do_import_agri(),
        ]
        return self._notify("\n\n".join(messages))
