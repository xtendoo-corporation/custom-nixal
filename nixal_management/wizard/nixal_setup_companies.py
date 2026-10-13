from odoo import Command, _, fields, models

COMPANY_NAMES = [
    "Nixal NC",
    "Nixal Trade",
    "NixAl Agri",
    "Nixal Financiación e Inversiones",
]
CHART_TEMPLATE = "es_pymes"


class NixalSetupCompaniesWizard(models.TransientModel):
    _name = "nixal.setup.companies.wizard"
    _description = "Crear las compañías del grupo Nixal"

    result_message = fields.Text(readonly=True)

    def _compute_display_name(self):
        for wizard in self:
            wizard.display_name = _("Crear compañías Nixal")

    def action_create_companies(self):
        self.ensure_one()
        eur = self.env.ref("base.EUR")
        spain = self.env.ref("base.es")
        company_model = self.env["res.company"]

        existing_companies = company_model.search([("name", "in", COMPANY_NAMES)])
        existing = existing_companies.mapped("name")
        missing_names = [n for n in COMPANY_NAMES if n not in existing]

        # Reuse Odoo's default bootstrap company ("My Company") as the
        # first Nixal company instead of leaving it around unused next to
        # 4 brand new ones - only if it hasn't already been claimed by one
        # of our own companies (e.g. on a second run of this wizard).
        renamed = []
        main_company = self.env.ref("base.main_company")
        if missing_names and main_company.name not in COMPANY_NAMES:
            first_name = missing_names.pop(0)
            main_company.write({
                "name": first_name,
                "currency_id": eur.id,
                "country_id": spain.id,
            })
            existing_companies |= main_company
            renamed.append(first_name)

        # Companies must be created in a single batch call: res.company's
        # own create() only triggers the country-based auto-install of
        # localization modules (e.g. account_peppol for Spain) *once*, after
        # all rows in the batch are inserted. Creating them one by one lets
        # that auto-install race with the next iteration's INSERT and leave
        # a required field without its default value.
        new_companies = company_model.create([
            {"name": name, "currency_id": eur.id, "country_id": spain.id}
            for name in missing_names
        ]) if missing_names else company_model

        companies = existing_companies | new_companies
        # Make sure every Nixal company is "allowed" for this request,
        # regardless of what the user has active in the company switcher -
        # otherwise multi-company record rules can block the chart of
        # accounts / journals being set up for a company not yet selected.
        self = self.with_context(
            allowed_company_ids=list(
                set(self.env.context.get("allowed_company_ids") or self.env.companies.ids)
                | set(companies.ids)
            )
        )
        chart_template_model = self.env["account.chart.template"]
        for company in companies:
            if not company.chart_template:
                chart_template_model.try_loading(
                    CHART_TEMPLATE, company=company, install_demo=False
                )

        created = new_companies.mapped("name")

        self.env.user.write({
            "company_ids": [Command.link(c.id) for c in companies],
        })

        message_lines = []
        if renamed:
            message_lines.append(
                _("'My Company' renombrada a: %s") % ", ".join(renamed)
            )
        if created:
            message_lines.append(_("Creadas: %s") % ", ".join(created))
        if existing:
            message_lines.append(_("Ya existían: %s") % ", ".join(existing))
        self.result_message = "\n".join(message_lines)

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Compañías Nixal"),
                "message": self.result_message,
                "sticky": True,
            },
        }
