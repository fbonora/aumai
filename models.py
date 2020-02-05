import datetime

from flask_user import UserMixin


from . import db


# Define the User data model. Make sure to add flask_user UserMixin!!
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    # User authentication information
    name = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False, server_default='')

    # Relationships
    roles = db.relationship('Role', secondary='user_roles',
                            backref=db.backref('users', lazy='dynamic'))
    dipendente = db.relationship('Dipendente', uselist=False, back_populates='user')

    def has_roles(self, *args):
        return set(args).issubset({role.name for role in self.roles})



# Define the Role data model
class Role(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)


# Define the UserRoles data model
class UserRoles(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('role.id', ondelete='CASCADE'))


class Dipendente(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    nome = db.Column(db.String(128))
    cognome = db.Column(db.String(128))
    residenza = db.Column(db.String(128))
    banca = db.Column(db.String(128))
    iban = db.Column(db.String(128))
    base = db.Column(db.Float)
    stato = db.Column(db.String(64))
    bloccato = db.Column(db.Boolean)
    #Relationships
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', back_populates='dipendente')
    spese = db.relationship('Spesa', back_populates='dipendente')
    timbrature = db.relationship('Timbratura', back_populates='dipendente')

    type = db.Column(db.String(50))

    __mapper_args__ = {
        'polymorphic_identity':'dipendente',
        'polymorphic_on':type
    }


class Cassiere(Dipendente):
    negozio_id = db.Column(db.Integer, db.ForeignKey('negozio.id'))
    # Relationships
    negozio = db.relationship('Negozio', back_populates='cassieri')
    versamenti = db.relationship('Versamento')
    chiamate = db.relationship('Chiamata', back_populates='dipendente')


    __mapper_args__ = {
        'polymorphic_identity':'cassiere',
    }


class Timbratura(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Date())
    inizio = db.Column(db.Time(timezone=True))
    fine = db.Column(db.Time(timezone=True))
    pausa = db.Column(db.Time(timezone=True))
    assenza = db.Column(db.Time(timezone=True), default = '00:00')
    descrizione = db.Column(db.String(255))
    ore_lavorate = db.Column(db.Integer())

    # Relationships
    dipendente_id = db.Column(db.Integer, db.ForeignKey('dipendente.id'))
    dipendente = db.relationship('Dipendente', back_populates='timbrature')


class Negozio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descrizione = db.Column(db.String(255))
    localita = db.Column(db.String(255))
    indirizzo = db.Column(db.String(255))
    # Relationships
    cassieri = db.relationship('Cassiere', back_populates='negozio')
    societa_id = db.Column(db.Integer, db.ForeignKey('societa.id'))
    societa = db.relationship('Societa', back_populates='negozi')
    spese = db.relationship('Spesa', back_populates='negozio')
    casse = db.relationship('Cassa', back_populates='negozio')
    apparecchiature = db.relationship('Apparecchiatura', back_populates='negozio')
    versamenti = db.relationship('Versamento', back_populates='negozio')
    totali_giornalieri = db.relationship('TotaleGiornaliero', back_populates='negozio')


class Societa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    # Relationships
    negozi = db.relationship('Negozio',back_populates='societa')
    casse = db.relationship('Cassa',back_populates='societa')
    versamenti = db.relationship('Versamento', back_populates='societa')
    totali_giornalieri = db.relationship('TotaleGiornaliero', back_populates='societa')
    spese = db.relationship('Spesa', back_populates='societa')


class Cassa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    matricola = db.Column(db.String(24))
    #Relationships
    versamenti = db.relationship('Versamento',back_populates='cassa')
    negozio_id = db.Column('Negozio', db.ForeignKey('negozio.id'))
    negozio = db.relationship('Negozio', back_populates='casse')
    societa_id = db.Column(db.Integer, db.ForeignKey('societa.id'))
    societa = db.relationship('Societa', back_populates='casse')
    spese = db.relationship('Spesa',back_populates='cassa')


class Versamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Date, default=datetime.date.today())
    fondo_cassa = db.Column(db.Float, default=float(0))
    contante = db.Column(db.Float, default=float(0))
    bancomat = db.Column(db.Float, default=float(0))
    totale = db.Column(db.Float, default=float(0))
    chiusura_fiscale = db.Column(db.Float, default=float(0))
    resi = db.Column(db.Float, default=float(0))
    totale_fiscale = db.Column(db.Float, default=float(0))
    differenza = db.Column(db.Float, default=float(0))
    spedito_agenzia = db.Column(db.Boolean, default=False)


    # Relationships
    cassiere = db.Column(db.Integer, db.ForeignKey('dipendente.id'))
    cassa_id = db.Column(db.Integer, db.ForeignKey('cassa.id'))
    cassa = db.relationship('Cassa', back_populates='versamenti')
    dettagli_contante = db.relationship('Contante', back_populates='versamento')
    dettagli_resi = db.relationship('Reso', back_populates='versamento')
    societa_id = db.Column(db.Integer, db.ForeignKey('societa.id'))
    societa = db.relationship('Societa', back_populates='versamenti')
    negozio_id = db.Column(db.Integer, db.ForeignKey('negozio.id'))
    negozio = db.relationship('Negozio', back_populates='versamenti')


class TotaleGiornaliero(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Date, default=datetime.date.today())
    fondo_cassa_iniziale = db.Column(db.Float, default=float(0))
    fondo_cassa_finale = db.Column(db.Float, default=float(0))
    totale_fiscale_negozio = db.Column(db.Float, default=float(0))
    totale_spese_negozio = db.Column(db.Float, default=float(0))
    versamento = db.Column(db.Float, default=float(0))

    societa_id = db.Column(db.Integer, db.ForeignKey('societa.id'))
    societa = db.relationship('Societa', back_populates='totali_giornalieri')
    negozio_id = db.Column(db.Integer, db.ForeignKey('negozio.id'))
    negozio = db.relationship('Negozio', back_populates='totali_giornalieri')


class Contante(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Date, default=datetime.date.today())
    _1_cent =  db.Column(db.Integer, default=0)
    _2_cent = db.Column(db.Integer, default=0)
    _5_cent = db.Column(db.Integer, default=0)
    _10_cent = db.Column(db.Integer, default=0)
    _20_cent = db.Column(db.Integer, default=0)
    _50_cent = db.Column(db.Integer, default=0)
    _1_eu = db.Column(db.Integer, default=0)
    _2_eu = db.Column(db.Integer, default=0)
    _5_eu = db.Column(db.Integer, default=0)
    _10_eu = db.Column(db.Integer, default=0)
    _20_eu = db.Column(db.Integer, default=0)
    _50_eu = db.Column(db.Integer, default=0)
    _100_eu = db.Column(db.Integer, default=0)
    _200_eu = db.Column(db.Integer, default=0)
    _500_eu = db.Column(db.Integer, default=0)

    # Relationships
    versameto_id = db.Column(db.Integer, db.ForeignKey('versamento.id'))
    versamento = db.relationship('Versamento', back_populates='dettagli_contante')


class Reso(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Date, default=datetime.date.today())
    ora = db.Column(db.Time(timezone=True))
    scontrino = db.Column(db.String(16), default='')
    importo =  db.Column(db.Float, default=float(0))

    # Relationships
    versamento_id = db.Column(db.Integer, db.ForeignKey('versamento.id'))
    versamento = db.relationship('Versamento', back_populates='dettagli_resi')


class Spesa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    causale = db.Column(db.String(128),  default='')
    descrizione = db.Column(db.String(128), default='')
    importo = db.Column(db.Float, default=float(0))
    data = db.Column(db.Date())
    km = db.Column(db.Integer, default=0)
    targa = db.Column(db.String(16), default='')
    id_cassiere = db.Column(db.Integer)

    #Relationships
    #dipendente_id = db.Column(db.Integer, db.ForeignKey('dipendente.id'))
    #dipendente = db.relationship('Dipendente', back_populates='spese')
    cassa_id = db.Column(db.Integer, db.ForeignKey('cassa.id'))
    cassa = db.relationship('Cassa', back_populates='spese')
    societa_id = db.Column(db.Integer, db.ForeignKey('societa.id'))
    societa = db.relationship('Societa', back_populates='spese')
    negozio_id = db.Column(db.Integer, db.ForeignKey('negozio.id'))
    negozio = db.relationship('Negozio', back_populates='spese')
    dipendente_id = db.Column(db.Integer, db.ForeignKey('dipendente.id'))
    dipendente = db.relationship('Dipendente', back_populates='spese')


class Apparecchiatura(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    descrizione = db.Column(db.String(128))

    # Relationships
    chiamate = db.relationship('Chiamata', back_populates='apparecchiatura')
    fornitore_id = db.Column(db.Integer, db.ForeignKey('fornitore.id'))
    fornitore = db.relationship('Fornitore', back_populates='apparecchiature')
    negozio_id = db.Column(db.Integer, db.ForeignKey('negozio.id'))
    negozio = db.relationship('Negozio', back_populates='apparecchiature')
    cod_app_id = db.Column(db.Integer, db.ForeignKey('tipo_apparecchiatura.id'))
    codice_app = db.relationship('TipoApparecchiatura',back_populates='apparecchiature')


class Fornitore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(128))
    telefono = db.Column(db.String(128))
    cell = db.Column(db.String(128))
    email = db.Column(db.String(128))
    contratto = db.Column(db.String(128))
    descrizione = db.Column(db.String(255))
    indirizzo = db.Column(db.String(128))
    localita = db.Column(db.String(128))

    #Relationships
    chiamate = db.relationship('Chiamata', back_populates='fornitore')
    apparecchiature = db.relationship('Apparecchiatura', back_populates='fornitore')


class Chiamata(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    problema = db.Column(db.String(128))
    data_apertura = db.Column(db.Date())
    data_chiusura = db.Column(db.Date())
    ora_apertura =  db.Column(db.Time(timezone=True))
    ora_chiusura =  db.Column(db.Time(timezone=True))
    esito = db.Column(db.String(128))

    #Relationships
    dipendente_id = db.Column(db.Integer, db.ForeignKey('dipendente.id'))
    dipendente = db.relationship('Cassiere', back_populates='chiamate')
    fornitore_id = db.Column(db.Integer, db.ForeignKey('fornitore.id'))
    fornitore = db.relationship('Fornitore', back_populates='chiamate')
    apparecchiature_id = db.Column(db.Integer, db.ForeignKey('apparecchiatura.id'))
    apparecchiatura = db.relationship('Apparecchiatura', back_populates='chiamate')


class TipoApparecchiatura(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descrizione = db.Column(db.String(128))
    apparecchiature = db.relationship('Apparecchiatura', back_populates='codice_app')


class StatoDipendente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stato = db.Column(db.String(128))


class TipoSpesa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(128))


class TipoContratto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(128))