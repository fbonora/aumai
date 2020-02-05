from flask import Blueprint, current_app
from wtforms import Form, StringField, validators, DecimalField, PasswordField, SelectField, SubmitField, IntegerField, \
    HiddenField, BooleanField
from wtforms.fields.html5 import EmailField, DateField, TimeField

from .static_data import role_list,  tipi_spesa, tipi_contratto

form_validator = Blueprint('form_validator', __name__)


class LoginForm(Form):
    name = StringField('Name', [validators.Length(min=4, max=25)])
    password = PasswordField('Password')


class UserRole(Form):
    ruolo = SelectField(u'Ruolo', choices=role_list)


class DipendenteForm(Form):
    username = StringField(u'Username', [validators.required()])
    password = StringField(u'Password', [validators.required(),
                                         validators.Length(min=3, max=8, message='Minimo 3 massimo 8 caratteri')])
    nome = StringField(u'Name', [validators.required()])
    cognome = StringField(u'Cognome', [validators.required()])
    residenza = StringField(u'Residenza', [validators.required()])
    banca = StringField(u'Banca', [validators.required()])
    iban = StringField(u'IBAN', [validators.required(),
                                 validators.Length(min=27, max=27, message='IBAN deve avere 27 caratteri')])
    base = DecimalField(u'Stipendio Base', [validators.required()])
    stato = SelectField(u'Stato', [validators.required()], choices=[], coerce=int)


class CassiereForm(DipendenteForm):
    negozio = SelectField(u'Negozio', choices=[], coerce=int)


class VersamentoForm(Form):
    cassa = StringField(u'Cassa')
    fondo_cassa = DecimalField('Fondo Cassa', places=None, rounding=None, use_locale=False, number_format=None)
    contante = DecimalField('Contante', places=None, rounding=None, use_locale=False, number_format=None)
    bancomat = DecimalField('Bancomat', places=None, rounding=None, use_locale=False, number_format=None)
    totale = DecimalField('totale', places=None, rounding=None, use_locale=False, number_format=None)
    chiusura_fiscale = DecimalField('Chiusura Fiscale', places=None, rounding=None, use_locale=False,
                                    number_format=None)
    resi = DecimalField('Resi', places=None, rounding=None, use_locale=False, number_format=None)
    annulli = DecimalField('Annulli', places=2, rounding=None, use_locale=False, number_format=None)



class ChiusuraVersamentoForm(VersamentoForm):
    totale_fiscale = DecimalField('Totale Fiscale', places=None, rounding=None, use_locale=False, number_format=None)
    differenza = DecimalField('Differenza', places=None, rounding=None, use_locale=False, number_format=None)
    data = DateField('Data', format='%Y-%m-%d', validators=[validators.required()])
    spedito = BooleanField('Spedito')
    id_versamento = HiddenField()
    submit = SubmitField(u'Salva')

class AdminVersamentoForm(ChiusuraVersamentoForm):
    negozio =  StringField(u'Negozio')

class ResocontoGiornalieroForm(Form):
    cassa_inizio = DecimalField('Cassa inizio', places=None, rounding=None, use_locale=False, number_format=None)
    incasso =  DecimalField('Incasso', places=None, rounding=None, use_locale=False, number_format=None)
    spese = DecimalField('Cassa inizio', places=None, rounding=None, use_locale=False, number_format=None)
    cassa_fine =  DecimalField('Incasso', places=None, rounding=None, use_locale=False, number_format=None)
    versamento = DecimalField('Incasso', places=None, rounding=None, use_locale=False, number_format=None)
    id_resoconto = HiddenField()
    submit = SubmitField(u'Salva')


class NegozioForm(Form):
    nome = StringField(u'Nome', [validators.required()])
    localita = StringField(u'Località', [validators.required()])
    indirizzo = StringField(u'Indirizzo', [validators.required()])
    societa = SelectField(u'Società', choices=[], coerce=int)
    cassa1 = StringField(u'Cassa1', [validators.required()])
    cassa2 = StringField(u'Cassa2', [validators.Optional()])
    cassa3 = StringField(u'Cassa3', [validators.Optional()])
    cassa4 = StringField(u'Cassa4', [validators.Optional()])
    cassa5 = StringField(u'Cassa5', [validators.Optional()])
    cassa6 = StringField(u'Cassa6', [validators.Optional()])
    cassa7 = StringField(u'Cassa7', [validators.Optional()])
    cassa8 = StringField(u'Cassa8', [validators.Optional()])
    cassa9 = StringField(u'Cassa9', [validators.Optional()])
    cassa10 = StringField(u'Cassa10', [validators.Optional()])

    id_negozio = HiddenField()
    submit = SubmitField(u'Aggiungi')
    cancel = SubmitField(u'Cancella')

class FornitoreForm(Form):
    nome = StringField(u'Nome', [validators.required()])
    telefono = StringField(u'Telefono', [validators.required()])
    cellulare = StringField(u'Cellulare', [validators.required()])
    email = EmailField(u'Email', [validators.DataRequired(), validators.Email()])
    indirizzo = StringField(u'Indirizzo', [validators.required()])
    localita = StringField(u'Localita', [validators.required()])
    contratto = SelectField(u'Contratto',  choices=tipi_contratto, coerce=int)
    descrizione = StringField(u'Descrizione')


class SpeseForm(Form):
    dipendente = SelectField(u'Dipendente', validators=[validators.optional()], choices=[], coerce=int)
    cassa = SelectField(u'Cassa', validators=[validators.optional()], choices=[], coerce=int)
    causale = SelectField(u'Causale', validators=[validators.required()], choices=tipi_spesa, coerce=int)
    descrizione = StringField(u'Descrizione', validators=[validators.Optional()])
    data = DateField('Data', format='%Y-%m-%d', validators=[validators.required()])
    importo = DecimalField(u'Importo', validators=[validators.required()], places=None, rounding=None, use_locale=False,
                           number_format=None)

    id_spesa = HiddenField()
    submit = SubmitField(u'Aggiungi')


class SpesaPersonaleForm(SpeseForm):
    inizio = StringField(u'Inizio', validators=[validators.Optional(),
                                                validators.Regexp('\d+:\d+', message="Orario nel formato hh:mm")])
    fine = StringField(u'Fine', validators=[validators.Optional(),
                                            validators.Regexp('\d+:\d+', message="Orario nel formato hh:mm")])


class SpesaAziendaleForm(SpeseForm):
    km_auto = StringField(u'KM Auto', validators=[validators.Optional()])
    targa_auto = StringField(u'Targa', validators=[validators.Optional()])


def calcolaTotale(form):
    _001 = get_euro(form.v_001)
    _002 = get_euro(form.v_002)
    _005 = get_euro(form.v_005)
    _01 = get_euro(form.v_010)
    _02 = get_euro(form.v_020)
    _05 = get_euro(form.v_050)
    _1 = get_euro(form.v_1)
    _2 = get_euro(form.v_2)
    _5 = get_euro(form.v_5)
    _10 = get_euro(form.v_10)
    _20 = get_euro(form.v_20)
    _50 = get_euro(form.v_50)
    _100 = get_euro(form.v_100)
    _200 = get_euro(form.v_200)
    _500 = get_euro(form.v_500)

    return _001 + _002 + _005 + _01 + _02 + _05 + _1 + _2 + _5 + _10 + _20 + _50 + _100 + _200 + _500


def get_euro(field):
    current_app.logger.debug('get_euro for field {}'.format(field.label))
    return field.data * float(field.label.text)


def calcola_reso(form):
    tot = form.imp_reso1.data + form.imp_reso2.data + form.imp_reso3.data + form.imp_reso4.data + form.imp_reso5.data + \
    form.imp_reso6.data + form.imp_reso7.data + form.imp_reso8.data + form.imp_reso9.data + form.imp_reso10.data + \
    form.imp_reso11.data + form.imp_reso12.data + form.imp_reso13.data + form.imp_reso14.data + form.imp_reso15.data

    return tot


def calcola_prelievi(form):
    tot = form.imp_prelievo1.data + form.imp_prelievo2.data + form.imp_prelievo3.data + form.imp_prelievo4.data + form.imp_prelievo5.data + \
          form.imp_prelievo6.data + form.imp_prelievo7.data + form.imp_prelievo8.data + form.imp_prelievo9.data + form.imp_prelievo10.data + \
          form.imp_prelievo11.data + form.imp_prelievo12.data + form.imp_prelievo13.data + form.imp_prelievo14.data + form.imp_prelievo15.data

    return tot


class DettaglioVersamento(Form):
    cassa = SelectField(u'Cassa', validators=[validators.required()], choices=[], coerce=int)
    v_001 = IntegerField(u'0.01', validators=[validators.Optional()], default=0)
    v_002 = IntegerField(u'0.02', validators=[validators.Optional()], default=0)
    v_005 = IntegerField(u'0.05', validators=[validators.Optional()], default=0)
    v_010 = IntegerField(u'0.10', validators=[validators.Optional()], default=0)
    v_020 = IntegerField(u'0.20', validators=[validators.Optional()], default=0)
    v_050 = IntegerField(u'0.50', validators=[validators.Optional()], default=0)
    v_1 = IntegerField(u'1.00', validators=[validators.Optional()], default=0)
    v_2 = IntegerField(u'2.00', validators=[validators.Optional()], default=0)
    v_5 = IntegerField(u'5.00', validators=[validators.Optional()], default=0)
    v_10 = IntegerField(u'10.00', validators=[validators.Optional()], default=0)
    v_20 = IntegerField(u'20.00', validators=[validators.Optional()], default=0)
    v_50 = IntegerField(u'50.00', validators=[validators.Optional()], default=0)
    v_100 = IntegerField(u'100.00', validators=[validators.Optional()], default=0)
    v_200 = IntegerField(u'200.00', validators=[validators.Optional()], default=0)
    v_500 = IntegerField(u'500.00', validators=[validators.Optional()], default=0)
    totale_contanti = HiddenField()

    fondo_cassa = DecimalField(u'Fondo Cassa', validators=[validators.required()], places=None, rounding=None,
                               use_locale=False,
                               number_format=None)
    bancomat = DecimalField(u'Bancomat', validators=[validators.required()], places=None, rounding=None,
                            use_locale=False,
                            number_format=None)

    ora_reso1 = TimeField('Inizio', format='%H:%M', validators=[validators.optional()])
    ora_reso2 = TimeField('Inizio', format='%H:%M', validators=[validators.optional()])
    ora_reso3 = TimeField('Inizio', format='%H:%M', validators=[validators.optional()])
    ora_reso4 = TimeField('Inizio', format='%H:%M', validators=[validators.optional()])
    ora_reso5 = TimeField('Inizio', format='%H:%M', validators=[validators.optional()])
    ora_reso6 = TimeField('Inizio', format='%H:%M', validators=[validators.optional()])
    ora_reso7 = TimeField('Inizio', format='%H:%M', validators=[validators.optional()])
    ora_reso8 = TimeField('Inizio', format='%H:%M', validators=[validators.optional()])
    ora_reso9 = TimeField('Inizio', format='%H:%M', validators=[validators.optional()])
    ora_reso10 = TimeField('Inizio', format='%H:%M', validators=[validators.optional()])
    ora_reso11 = TimeField('Inizio', format='%H:%M', validators=[validators.optional()])
    ora_reso12 = TimeField('Inizio', format='%H:%M', validators=[validators.optional()])
    ora_reso13 = TimeField('Inizio', format='%H:%M', validators=[validators.optional()])
    ora_reso14 = TimeField('Inizio', format='%H:%M', validators=[validators.optional()])
    ora_reso15 = TimeField('Inizio', format='%H:%M', validators=[validators.optional()])

    scontrino_reso1 = StringField(u'', validators=[validators.Optional()])
    scontrino_reso2 = StringField(u'', validators=[validators.Optional()])
    scontrino_reso3 = StringField(u'', validators=[validators.Optional()])
    scontrino_reso4 = StringField(u'', validators=[validators.Optional()])
    scontrino_reso5 = StringField(u'', validators=[validators.Optional()])
    scontrino_reso6 = StringField(u'', validators=[validators.Optional()])
    scontrino_reso7 = StringField(u'', validators=[validators.Optional()])
    scontrino_reso8 = StringField(u'', validators=[validators.Optional()])
    scontrino_reso9 = StringField(u'', validators=[validators.Optional()])
    scontrino_reso10 = StringField(u'', validators=[validators.Optional()])
    scontrino_reso11 = StringField(u'', validators=[validators.Optional()])
    scontrino_reso12 = StringField(u'', validators=[validators.Optional()])
    scontrino_reso13 = StringField(u'', validators=[validators.Optional()])
    scontrino_reso14 = StringField(u'', validators=[validators.Optional()])
    scontrino_reso15 = StringField(u'', validators=[validators.Optional()])

    imp_reso1 = DecimalField(validators=[validators.Optional()], default=0)
    imp_reso2 = DecimalField(validators=[validators.Optional()], default=0)
    imp_reso3 = DecimalField(validators=[validators.Optional()], default=0)
    imp_reso4 = DecimalField(validators=[validators.Optional()], default=0)
    imp_reso5 = DecimalField(validators=[validators.Optional()], default=0)
    imp_reso6 = DecimalField(validators=[validators.Optional()], default=0)
    imp_reso7 = DecimalField(validators=[validators.Optional()], default=0)
    imp_reso8 = DecimalField(validators=[validators.Optional()], default=0)
    imp_reso9 = DecimalField(validators=[validators.Optional()], default=0)
    imp_reso10 = DecimalField(validators=[validators.Optional()], default=0)
    imp_reso11 = DecimalField(validators=[validators.Optional()], default=0)
    imp_reso12 = DecimalField(validators=[validators.Optional()], default=0)
    imp_reso13 = DecimalField(validators=[validators.Optional()], default=0)
    imp_reso14 = DecimalField(validators=[validators.Optional()], default=0)
    imp_reso15 = DecimalField(validators=[validators.Optional()], default=0)
    totale_resi = DecimalField()


    id_versamento = HiddenField()
    calcola = SubmitField(u'Calcola')
    aggiungi = SubmitField(u'Aggiungi')


class ChiamataForm(Form):
    apparecchiatura = SelectField(u'Apparecchiatura', validators=[validators.required()], choices=[], coerce=int)
    fornitore = StringField(u'Fornitore', validators=[validators.required()])
    contatto = StringField(u'Contatto', validators=[validators.required()])
    descrizione = StringField(u'Descrizione', validators=[validators.Optional()])
    data_apertura = DateField('Data', format='%Y-%m-%d', validators=[validators.required()])

    data_chiusura = DateField('Data', format='%Y-%m-%d', validators=[validators.optional()])
    ora_inizio = TimeField('Inizio', format='%H:%M', validators=[validators.optional()])
    ora_fine = TimeField('Fine', format='%H:%M', validators=[validators.optional()])
    esito = StringField(u'Esito', validators=[validators.Optional()])

    chiamata_id = HiddenField()

    submit = SubmitField(u'Aggiungi')


class ApparecchiaturaForm(Form):
    negozio = SelectField(u'Negozio', validators=[validators.required()], choices=[], coerce=int)
    fornitore = SelectField(u'Fornitore', validators=[validators.required()], choices=[], coerce=int)
    codice = SelectField(u'Codice', validators=[validators.required()], choices=[], coerce=int)
    descrizione = StringField(u'Descrizione', validators=[validators.required()])

    submit = SubmitField(u'Aggiungi')


class TimbraturaForm(Form):
    dipendente = SelectField(u'Dipendente', validators=[validators.required()], choices=[], coerce=int)
    data = DateField('Data', format='%Y-%m-%d', validators=[validators.required()])
    ora_inizio = TimeField('Inizio', format='%H:%M', validators=[validators.required()])
    ora_fine = TimeField('Fine', format='%H:%M', validators=[validators.required()])
    pausa = TimeField('Pausa', format='%H:%M', validators=[validators.required()])
    assenza = TimeField('Assenza', format='%H:%M', validators=[validators.required()])
    descrizione = StringField(u'Descrizione', validators=[validators.optional()])

    id_timbratura = HiddenField()
    submit = SubmitField(u'Aggiungi')


class SocietaForm(Form):
    codice = IntegerField('Codice')
    name = StringField(u'Descrizione', validators=[validators.required()])