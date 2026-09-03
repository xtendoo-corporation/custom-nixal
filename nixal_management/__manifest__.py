{
    "name": "Nixal - Gestión Multi-Compañía",
    "version": "19.0.1.0.0",
    "category": "Accounting",
    "summary": "Estructura multi-compañía y ejemplos de flujo completo para Nixal",
    "author": "Xtendoo",
    "license": "AGPL-3",
    "depends": [
        "account",
        "account_budget_oca",
        "l10n_es",
        "sale_management",
        "purchase",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/nixal_menus.xml",
        "wizard/nixal_setup_companies_views.xml",
        "wizard/nixal_demo_import_views.xml",
        "wizard/nixal_full_import_views.xml",
    ],
    "installable": True,
    "application": True,
}
