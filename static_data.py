role_list = [
    (1, 'Amministratore'),
    (2, 'Responsabile negozio'),
    (3, 'Cassiere'),
    (4, 'Commesso')
]

tipi_apparecchiature = [
    ('',''),
    ('PA', 'Porte Automatiche'),
    ('ASC', 'Ascensore'),
    ('INC', 'Antincendio'),
    ('COND', 'Condizionamento')
]

stati_dipendente = [
    (1, 'ATTIVO'),
    (2, 'CESSATO')
]

casuali_spesa = [
    (1, 'Alimentari'),
    (2, 'Carburante')
]

tipi_contratto = [
    (1, 'ABBONAMENTO'),
    (2, 'LIBERO')
]

tipi_spesa = [
    (0, ''),
    (1, 'Spesa aziendale senza Fattura'),
    (2, 'Spesa aziendale con Fattura'),
    (3, 'Varie'),
    (4, 'Personale')
]


lista_societa = [
    (111, 'AM S.R.L.'),
    (222, 'HAO MAI 2 S.R.L.'),
    (331, 'AM 3 S.R.L.'),
    (333, 'HAO MAI 3 S.R.L.'),
    (441, 'AM 4 S.R.L.'),
    (444, 'HAO MAI 4 S.R.L.'),
    (555, 'SAMA S.R.L.'),
    (661, 'AM 6 S.R.L.'),
    (666, 'AM 5 S.R.L.'),
    (771, 'AM 7 S.R.L.'),
    (777, 'AM 1 S.R.L.'),
    (881, 'AM 8 S.R.L.'),
    (999, 'AUMAI S.P.A.')
]

lista_fornitori = [
    {'nome': 'Fabio Bonora', 'telefono': '029523456', 'cell': '334567890', 'email': 'fb@gmail.com',
     'indirizzo': 'via pinco 2', 'localita': 'pallino','contratto': '', 'descrizione': ''},
    {'nome': 'Alex Casalini', 'telefono': '01123455', 'cell': '34567890', 'email': 'secondo@gmail.com',
     'indirizzo': 'via pluto 34', 'localita': 'paperino','contratto': '', 'descrizione': ''},

]


lista_negozi = [
    {'societa': '111', 'nome': '1 - AM S.R.L. TADINI', 'indirizzo': 'Via A.Tadini 23', 'localita': 'BRESCIA', 'casse': ['(1) xxxx1', '(2) xxxx2']},
    {'societa': '111', 'nome': '4 - AM S.R.L. VIA VOLTA', 'indirizzo': 'Via Volta N.72', 'localita': 'BRESCIA','casse': ['(1) xxxx4', '(2) xxxx5', '(3) xxxx6']},
    {'societa': '111', 'nome': '17 - AM S.R.L. RODENGO', 'indirizzo': 'Via Del Commercio 12 . Loc. Moie', 'localita': 'RODENGO SAIANO (BS)','casse': ['(1) yyyy1', '(2) yyyy2', '(3) yyyy3']}
]
