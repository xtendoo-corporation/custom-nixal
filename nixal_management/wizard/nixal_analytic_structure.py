"""Analytic structure of the Nixal "cuadro de gestión" spreadsheet.

Each block (header row) of a sheet is an analytic plan; each line under it
is an analytic account of the company that owns the sheet. Only the
structure is defined here - no amounts.
"""

ROOT_PLAN = "Nixal"

AGRI = "NixAl Agri"
NC = "Nixal NC"
TRADE = "Nixal Trade"
FIN = "Nixal Financiación e Inversiones"

# (company name, plan name, [analytic account names])
STRUCTURE = [
    # Hoja Act.Ganadera
    (AGRI, "Act. Ganadera - Ventas", [
        "Venta de Carne Vacuno",
        "Subvención reforestación y sequia",
        "Subvención Reforestación II",
        "Propios porcino",
    ]),
    (AGRI, "Act. Ganadera - Gastos explotación", [
        "Siembra y cosechado",
        "Teneros",
        "Medicamentos y vetrinario vacas y cerdos",
        "Seguro Vacas",
        "Asaja",
        "Registro Angus",
        "Alimento",
        "Portes (Para venta de carne)",
        "Compra de carne",
        "Matadero (Para venta de carne)",
        "Portes",
    ]),
    (AGRI, "Act. Ganadera - Gastos generales", [
        "Seguro vehículos y maquinaria veyrema",
        "Seguro RC",
        "Otras tasas e impuestos (IBI, RM, IVTM, …)",
        "Mantenimiento finca y maquinaria",
        "Formación y asesoría Regen Academy",
        "Gasoil A o gasolina",
        "Salario Mariano Lopez",
        "Servicios legales",
        "Gestoría laboral",
        "Gestión Forestal Sostenible",
        "Servicios y comisiones financieras",
        "Seguro Vida Caixa Alfonso- Préstamo Reforestación",
        "Prev. Riesgos laborales",
        "Servicios informáticos",
        "Butano",
        "Varios, correos, etc.",
        "Gtos. Subvención Cortafuegos",
        "Gtos. Subvención Reforestación I",
        "Gtos. Subvención Reforestación II",
        "Gtos. Subvención PAC extra ucrania y sequia",
        "Gtos. Subvención Sequía",
    ]),
    # Hoja Inversiones
    (AGRI, "Inversiones Act. Ganadera", [
        "Tractor y segadora - en cuadro financiación",
        "Empacadora II y ensiladora - en cuadro financiación",
        "Compra maquinaria y elementos varios",
        "Instalaciones: Vallas y caminos",
        "Licencias programas informaticos",
        "Reformas construcciones fincas",
        "Compra de vacas",
        "Fincas María y Miguel",
        "Finca Hermanos Gutierrez",
        "Finca Lucía",
        "Finca Federico de Santa Ana",
    ]),
    (NC, "Inversiones NC", [
        "Inmueble República Argentina",
        "Coche Land Rover BBVA",
        "Coche Land Rover GYSA-Cetelem",
        "Compra vivienda Iceberg",
        "Compras inmobilizado",
    ]),
    # Hojas NC-Ingresos / NC-Gastos (los clientes son contactos, no analítica)
    (NC, "NC - Ingresos", [
        "Market Intelligence",
    ]),
    (NC, "NC - Gastos generales", [
        "Conferencia Dropet",
        "Compras inmobilizado",
        "Suministros informáticos y mantenimiento",
        "Trips/commercial expenses",
        "Personnel - Felipe Fontes",
        "Personnel - Alfonso Carmona Bosch",
        "Personnel - Alberto Carmona",
        "Personnel - Rosa Jiménez",
        "Personnel - María Lacañina",
        "Soc. Security",
        "Fiscal, Accounting agency",
        "Laboral Agency",
        "Legal",
        "ISCC",
        "ICE",
        "OPIS + SCI + TRS + FO Licht + ISO+ARA Storage",
        "AgriCensus (Fastmarkets) + European Gas Hub+Quantum",
        "IVA",
        "IRPF",
        "IS",
        "Otros impuestos",
        "Gastos Bancarios y comisiones",
        "Mto. y gasolina Coche",
        "Publicidad y propaganda",
        "Bus",
        "Adaptext traducciones",
        "Mensajería",
        "Vodafone-Orange",
        "Seguros salud trabajadores",
        "Seguro Qualitas/Mutua Madrileña Auto",
        "Seguro Mapfre Auto",
        "Seguro Allianz Hogar",
        "Seguro Allianz Vida Alberto- Leasing coche",
        "Seguro Allianz Vida Alfonso- Póliza crédito",
        "Seguro Vida Caixa Alfonso- Préstamo Reforestación",
        "Seguro de Convenio Caixa",
        "Segur Caixa Salud",
        "Seguro vida Caixa Alberto- Préstamo",
        "Seguro vida Caixa Alberto- Préstamo 150.000€ (Cta 1117)",
        "Seguro vida Caixa Alberto- Préstamo 150.000€ 03/10/25 (Cta 1117)",
        "Seguro vida Caixa Alberto- Préstamo 150.000€ (Cta 5871)",
        "Seguro Responsabilidad Civil Préstamo y crédito BBVA",
        "Iberica Feeding Stuff",
        "Safinco- Comunidad y agua Rep. Argentina",
        "Safinco- Comunidad edificio Iceberg",
        "Electricidad- Total Energies",
        "Gastos reforma Rep. Argentina 11",
        "Electricidad- Gana Energía Gas",
        "Otros",
    ]),
    # Hojas Trade-Ingresos / Trade-Gastos (una línea por factura en el Excel)
    (TRADE, "Trade - Ingresos", ["Ventas Trade"]),
    (TRADE, "Trade - Gastos", ["Compras Trade"]),
    # Hoja Financiación
    (FIN, "Financiación - Préstamos y créditos", [
        "Prestamo ICO Caixa - 99k Eur",
        "Prestamo ICO Santander - 100k Eur",
        "Hipotecario RA11 - BBVA",
        "Hipotecario San Rafael - Santander",
        "Hipotecario María, Miguel, FedeSantana - Caixa",
        "Hipotecario Hnos. Gutierrez - BBVA",
        "Crédito Reforestación - Caixa",
        "Crédito Reforestación ll- Caixa",
        "Préstamo Caixa- 150K Eur para Paragon",
        "Préstamo Caixa- 150K Eur",
        "Crédito Reforestación ll - Caja Rural",
        "Préstamo Bankinter - 75k Eur",
        "Préstamo Bankinter Vivienda Iceberg- 151.900 Eur",
        "Financiación IS Bankinter",
    ]),
    (FIN, "Financiación - Intereses", [
        "Intereses circulante Caixa - 100k",
        "Intereses préstamo Caixa - 150k para Paragon",
        "Intereses préstamo Caixa - 150k",
        "Intereses circulante BBV - 75k",
        "Intereses circulante Bankinter - 100k",
        "Intereses préstamo Bankinter - 151,9k",
    ]),
    (FIN, "Financiación - Leasings y otros", [
        "NixAl Agri",
        "Alberto Carmona",
        "Leasing tractor y segadora - Caixa",
        "Leasing empacadora - Caja Rural",
        "Conchita Carmona",
        "Herederos de Carmona Viñau",
        "Alberto Bello",
        "Gonzalo Jimenez",
        "Agro Energia de Africa",
        "Pierna Seca",
    ]),
]

# Budgetary positions (account.budget.post), created in every company from
# the Spanish PYMES chart: name -> account code prefixes. account_budget_oca
# only counts analytic lines whose general account belongs to the position.
BUDGET_POSITIONS = {
    "Ingresos": ["7"],
    "Gastos de explotación": ["60", "61", "62", "63", "64", "65", "68"],
    "Gastos financieros": ["66"],
    "Inversiones": ["20", "21", "22", "23"],
    "Financiación": ["17", "52"],
}

# Position used by the budget lines of every account of a plan.
PLAN_POSITION = {
    "Act. Ganadera - Ventas": "Ingresos",
    "Act. Ganadera - Gastos explotación": "Gastos de explotación",
    "Act. Ganadera - Gastos generales": "Gastos de explotación",
    "Inversiones Act. Ganadera": "Inversiones",
    "Inversiones NC": "Inversiones",
    "NC - Ingresos": "Ingresos",
    "NC - Gastos generales": "Gastos de explotación",
    "Trade - Ingresos": "Ingresos",
    "Trade - Gastos": "Gastos de explotación",
    "Financiación - Préstamos y créditos": "Financiación",
    "Financiación - Intereses": "Gastos financieros",
    "Financiación - Leasings y otros": "Financiación",
}
