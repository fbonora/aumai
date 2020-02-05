import datetime

import sqlalchemy

from .static_data import lista_societa, lista_fornitori, lista_negozi, role_list, tipi_apparecchiature, stati_dipendente, tipi_spesa, tipi_contratto
from .models import Societa, Fornitore, Negozio, Cassa, User, Role, Cassiere, Versamento, Apparecchiatura, Dipendente, TipoApparecchiatura, StatoDipendente, TipoContratto, TipoSpesa
from . import db
from flask import make_response, Blueprint, current_app

rest = Blueprint('rest', __name__)


def load_fornitori():
    for item in lista_fornitori:
        fornitore = Fornitore.query.filter(Fornitore.email == item['email']).first()
        if fornitore is None:
            obj = Fornitore(
                nome=item['nome'],
                descrizione=item['descrizione'],
                email=item['email'],
                telefono=item['telefono'],
                indirizzo=item['indirizzo'],
                localita=item['localita'],
                cell=item['cell'],
                contratto=item['contratto']
            )
            db.session.add(obj)

    db.session.commit()


@rest.route("/api/v2/load/<module>")
def load(module):
    mod = module
    headers = {"Content-Type": "application/json"}
    if mod == 'societa':
        error = load_societa()
    if mod == 'fornitori':
        error = load_fornitori()
    if mod == 'negozi':
        error = load_negozi()

    if error is not None:
        return make_response('Load ' + mod + ' with error', 500)

    return make_response('Load ' + mod + ' DONE', 200)


def load_societa():
    for item in lista_societa:
        societa = Societa.query.filter(Societa.id == item[0]).first()
        if societa is None:
            soc = Societa(id=item[0], name=item[1])
            db.session.add(soc)

    db.session.commit()



def load_negozi():
    for item in lista_negozi:
        societa = Societa.query.filter(Societa.id == item['societa']).first()
        if societa is None:
            return "Societa' {} non trovata".format(item['societa'])
        negozio = Negozio.query.filter(Negozio.societa_id==item['societa']).filter(Negozio.descrizione==item['nome']).first()
        if negozio is None:
            negozio = Negozio(
                descrizione=item['nome'],
                localita=item['localita'],
                indirizzo=item['indirizzo'],
            )
            casse = item['casse']
            for matricola in casse:
                cassa = Cassa(matricola=matricola)
                negozio.casse.append(cassa)
                cassa.negozio = negozio
                cassa.societa = societa
                db.session.add(cassa)

            negozio.societa = societa
            societa.negozi.append(negozio)
            db.session.add(negozio)

    db.session.commit()


def init_test():
    db.drop_all()
    db.create_all()
    # Create 'user007' user with 'secret' and 'agent' roles
    if not User.query.filter(User.name == 'admin').first():
        adm_role = Role(id=1, name='admin')
        cass_role = Role(id=2, name='cassiere')
        oper_role = Role(id=3, name='operatore')
        user1 = User(id=2, name='cassiere', password='pwd')
        user2 = User(id=1, name='admin', password='admin')
        user3 = User(id=3, name='operatore', password='pwd')
        user4 = User(id=4, name='fabio', password='pwd')
        cassiere1 = Cassiere(id=2, username='cassiere', banca='Fineco', iban='IT93V0301503200000000039609', base=1000)
        cassiere2 = Cassiere(id=4, username='fabio', banca='Fineco', iban='IT85V0301583200000000055555', base=1500)
        load_societa()
        load_negozi()
        load_fornitori()
        versamento1 = Versamento(data=datetime.date.today(),
                                 fondo_cassa=float(150.00), bancomat=float(850.00), contante=float(1052.00))
        versamento2 = Versamento(data=datetime.date.today(),
                                 fondo_cassa=float(50.00), bancomat=float(450.00), contante=float(32.50))
        versamento3 = Versamento(data=datetime.date.today(),
                                 fondo_cassa=float(0.00), bancomat=float(1230.32), contante=float(978.00))

        app1 = Apparecchiatura(cod_app='COND', descrizione='condizionatore reparto intimo')
        app2 = Apparecchiatura(cod_app='ASC', descrizione='scala 2')

        negozio1 = Negozio.query.filter(Negozio.id == 1).first()
        negozio2 = Negozio.query.filter(Negozio.id == 2).first()
        fornitore1 = Fornitore.query.filter(Fornitore.id == 1).first()
        fornitore2 = Fornitore.query.filter(Fornitore.id == 2).first()
        fornitore1.apparecchiature.append(app1)
        fornitore2.apparecchiature.append(app2)
        app1.fornitore = fornitore1
        app1.negozio = negozio1
        negozio1.apparecchiature.append(app1)
        app2.fornitore = fornitore2
        app2.negozio = negozio1
        negozio1.apparecchiature.append(app2)

        # cassiere -- user -- ruolo
        cassiere1.user = user1
        cassiere1.user_id = user1.id
        cassiere2.user = user4
        cassiere2.user_id = user4.id
        user1.roles.append(cass_role)
        user2.roles.append(adm_role)
        user2.roles.append(cass_role)
        user3.roles.append(oper_role)
        user4.roles.append(cass_role)

        # negozio -cassiere
        negozio1.cassieri.append(cassiere1)
        cassiere1.negozio = negozio1
        negozio2.cassieri.append(cassiere2)
        cassiere2.negozio = negozio2


        # versamento
        versamento1.cassiere = cassiere1.id
        versamento1.cassa_id = negozio1.casse[0].id
        versamento2.cassiere = cassiere1.id
        versamento2.cassa_id = negozio1.casse[0].id
        versamento3.cassiere = cassiere2.id
        versamento3.cassa_id = negozio2.casse[0].id

        db.session.add(user1)
        db.session.add(user2)
        db.session.add(user3)
        db.session.add(user4)
        db.session.add(cassiere1)
        db.session.add(cassiere2)

        db.session.add(versamento1)
        db.session.add(versamento2)
        db.session.add(versamento3)
        db.session.add(app1)
        db.session.add(app2)


        db.session.commit()


@rest.route("/api/v2/initDB/<ipDB>")
def init(ipDB):
    if ipDB == 'mysql':
        USER = 'root'
        PASSWORD = 'aumai123!'
        HOST = ipDB
        DATABASE = 'aumaiDB'
        url = 'mysql+pymysql://%s:%s@%s' % (USER, PASSWORD, HOST)
        engine = sqlalchemy.create_engine(url)  # connect to server

        create_str = "CREATE DATABASE IF NOT EXISTS %s ;" % (DATABASE)
        engine.execute(create_str)
        engine.execute("USE {};".format(DATABASE))
        db.create_all()


    #if User.query.filter(User.name == 'admin').first():
    db.drop_all()
    db.create_all()


    for role in role_list:
        newRole = Role(id=role[0],name=role[1])
        current_app.logger.debug("Aggiungo ruolo id={} nome={}".format(role[0],role[1]))
        db.session.add(newRole)

    #Ad ogni utente deve corrispondere un dipendente.
    user_admin = User(id=1, name='admin', password='admin')
    user_admin.roles.append(Role.query.get(1))
    dipendente = Dipendente(id=1,username='admin',nome='admin',cognome='admin')
    dipendente.user_id = dipendente.id
    dipendente.user = user_admin

    #Inizializzo i dati statici
    current_app.logger.info("Aggiungo dati statici al DB")
    for apptype in tipi_apparecchiature:
        app = TipoApparecchiatura(descrizione=apptype[1])
        db.session.add(app)
    for stato in stati_dipendente:
        obj = StatoDipendente(stato=stato[1])
        db.session.add(obj)
    for spesa in tipi_spesa:
        obj = TipoSpesa(tipo=spesa[1])
        db.session.add(obj)
    for contratto in tipi_contratto:
        obj = TipoContratto(tipo=contratto[1])
        db.session.add(obj)

    current_app.logger.info("Aggiungo utente ammin e relativo dipendente")
    db.session.add(user_admin)
    db.session.add(dipendente)
    db.session.commit()

    return make_response('Database created', 200)


@rest.route("/api/v2/populateDB")
def populateDB():
    init_test()

    return make_response('Database populated', 200)