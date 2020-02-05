import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from flask_login import current_user, login_required
from flask_user import roles_required


from .form_validator import ChiusuraVersamentoForm, TimbraturaForm, SpesaAziendaleForm, SpeseForm, ChiamataForm, ResocontoGiornalieroForm
from .static_data import tipi_spesa
from .models import Cassiere, Versamento, Chiamata, Spesa, Timbratura, Cassa, Dipendente, Apparecchiatura, TotaleGiornaliero
from . import db


responsabile = Blueprint('responsabile', __name__)


def render_ore(seconds):
    delta = datetime.timedelta(seconds=seconds)
    return delta.__str__()


@responsabile.route('/home_responsabile/<panel>/<subpanel>')
@responsabile.route('/home_responsabile/<panel>',  defaults={'subpanel': None})
@login_required
@roles_required('Responsabile negozio')
def home_responsabile(panel, subpanel):
    panello = panel
    cassiere = Cassiere.query.get(current_user.id)
    if cassiere and panello == 'resoconto':
        casse = Cassa.query.filter(Cassa.negozio == cassiere.negozio).all()
        current_app.logger.debug(casse)
        lista_versamenti = Versamento.query.filter(Versamento.cassa_id.in_([cassa.id for cassa in casse]), Versamento.data==datetime.date.today()).all()
        current_app.logger.debug(lista_versamenti)
        #Chiamate chiuse oggi
        lista_chiamate = Chiamata.query.filter(Chiamata.dipendente_id == current_user.id, Chiamata.esito!=None, Chiamata.data_chiusura==datetime.date.today()).all()
        #spese sostenute oggi da tutte le casse
        lista_spese = Spesa.query.filter(Spesa.negozio_id==cassiere.negozio_id, Spesa.data==datetime.date.today()).all()

        #Preparo form per resoconto
        #Calcolo totale versameti casse e relative spese
        #Verifico se esiste un resoconto
        form = ResocontoGiornalieroForm()
        resoconto = TotaleGiornaliero.query.filter(TotaleGiornaliero.data == datetime.date.today(), TotaleGiornaliero.negozio_id == cassiere.negozio_id).first()
        if resoconto:
            current_app.logger.info("Resoconto esistente {}".format(resoconto.id))
            form.id_resoconto.data = resoconto.id
        form.incasso.data = sum(versamento.totale_fiscale for versamento in lista_versamenti)
        form.spese.data = sum(spesa.importo for spesa in lista_spese)
        form.cassa_inizio.data = 500
        form.cassa_fine.data = 500
        form.versamento.data = (form.incasso.data + form.cassa_inizio.data) - (form.spese.data + form.cassa_fine.data)


        return render_template('responsabile/resoconto.html', panel=panello,  lista_versamenti=lista_versamenti, lista_spese=lista_spese,form = form,
                               negozio=cassiere.negozio)
    if cassiere and panello == 'versamenti':
        casse = Cassa.query.filter(Cassa.negozio == cassiere.negozio).all()
        current_app.logger.debug(casse)
        lista_versamenti = Versamento.query.filter(Versamento.cassa_id.in_([cassa.id for cassa in casse]), Versamento.data==datetime.date.today()).all()
        current_app.logger.debug(lista_versamenti)
        return render_template('responsabile/versamenti_negozio.html', panel=panello,  lista_versamenti=lista_versamenti,
                               negozio=cassiere.negozio)


    if cassiere and panello == 'chiamate':
        if subpanel == 'aperte':
            #tutte le chiamate aperte nel negozio
            lista_chiamate = Chiamata.query.filter(Chiamata.dipendente_id==current_user.id).filter(Chiamata.data_chiusura==None).all()
        elif subpanel == 'chiuse':
            lista_chiamate = Chiamata.query.filter(Chiamata.dipendente_id==current_user.id).filter(Chiamata.data_chiusura!=None).all()
            return render_template('responsabile/chiamate_chiuse.html', panel=panello, subpanel=subpanel, lista_chiamate=lista_chiamate,
                                   negozio=cassiere.negozio)
        else:
            lista_chiamate = Chiamata.query.filter(Chiamata.dipendente_id == current_user.id).all()
        return render_template('responsabile/chiamate.html', panel=panello, subpanel=subpanel, lista_chiamate=lista_chiamate,
                               negozio=cassiere.negozio)

    if cassiere and panello == 'spese':
        lista_spese = lista_spese_negozio(cassiere)
        return render_template('responsabile/spese.html', panel=panello,  lista_spese=lista_spese, negozio = cassiere.negozio, tipi_spesa=tipi_spesa)
    if cassiere and panello == 'timbrature':
        lista_timbrature = Timbratura.query.all()
        return render_template('responsabile/timbrature.html', panel=panello,  lista_timbrature=lista_timbrature, negozio = cassiere.negozio, displayHours=render_ore)


    return render_template('responsabile/home_responsabile.html', panel=panello, negozio = cassiere.negozio)


@responsabile.route('/chiusura_versamento/<id>', methods=['GET', 'POST'])
@login_required
@roles_required('Responsabile negozio')
def gestisci_chiusura_versamento(id):
    form = ChiusuraVersamentoForm(request.form)
    versamento = Versamento.query.get(id)
    cassiere = Cassiere.query.get(current_user.id)
    if versamento:
        form.cassa = versamento.cassa.matricola
        form.contante = versamento.contante
        form.fondo_cassa = versamento.fondo_cassa
        form.bancomat = versamento.bancomat
        form.totale = versamento.totale
        form.resi = versamento.resi
        form.chiusura_fiscale = versamento.chiusura_fiscale
        form.data = versamento.data
        form.totale_fiscale.data = versamento.totale_fiscale
        form.differenza = versamento.differenza
        form.id_versamento = id
        form.spedito.data = versamento.spedito_agenzia
        return render_template('responsabile/chiusura_versamento.html', form=form, panel='versamenti', negozio=cassiere.negozio)
    else:
        flash(u'Impossibile trovare versamento con id {}'.format(id))
        current_app.logger.error(u'Impossibile trovare versamento con id {}'.format(id))

    return render_template('responsabile/home_responsabile.html', panel='versamenti', negozio=cassiere.negozio)


@responsabile.route('/versamento/resoconto_giornaliero', methods=['GET', 'POST'])
@login_required
@roles_required('Responsabile negozio')
def resoconto_giornaliero():
    current_app.logger.debug(request.form)
    form = ResocontoGiornalieroForm(request.form)
    cassiere = Cassiere.query.get(current_user.id)
    #Salvo resoconto giornaliero nel DB
    resoconto = TotaleGiornaliero.query.get(form.id_resoconto.data)
    if resoconto == None:
        current_app.logger.info('Nuovo resoconto giornaliero nel negozio {}'.format(cassiere.negozio_id))
        resoconto = TotaleGiornaliero()
    resoconto.negozio = cassiere.negozio
    resoconto.societa = cassiere.negozio.societa
    resoconto.data = datetime.date.today()
    resoconto.fondo_cassa_finale = form.cassa_fine.data
    resoconto.fondo_cassa_iniziale = form.cassa_inizio.data
    resoconto.totale_fiscale_negozio = form.incasso.data
    resoconto.totale_spese_negozio = form.spese.data
    resoconto.versamento = form.versamento.data

    db.session.add(resoconto)
    db.session.commit()

    return redirect( url_for('responsabile.home_responsabile', panel='resoconto'))


@responsabile.route('/salva_chiusura_versamento', methods=[ 'POST'])
@login_required
@roles_required('Responsabile negozio')
def salva_chiusura_versamento():
    current_app.logger.debug("Eccomi")
    form = ChiusuraVersamentoForm(request.form)
    current_app.logger.debug(form)
    id = form.id_versamento.data
    tot_fiscale = form.totale_fiscale.data

    versamento = Versamento.query.get(id)
    if versamento:
        versamento.totale_fiscale = float(tot_fiscale)
        versamento.differenza = versamento.totale_fiscale - versamento.chiusura_fiscale
        versamento.spedito_agenzia = form.spedito.data

        db.session.add(versamento)
        db.session.commit()

    return redirect( url_for('responsabile.home_responsabile', panel='versamenti'))


@responsabile.route('/elimina_timbratura/<id>', methods=['GET'])
@login_required
@roles_required('Responsabile negozio')
def elimina_timbratura(id):
    timbratura = Timbratura.query.get(id)
    db.session.delete(timbratura)
    db.session.commit()

    return redirect(url_for('responsabile.home_responsabile', panel='timbrature'))


@responsabile.route('/modifica_timbratura/<id>', methods=['GET'])
@login_required
@roles_required('Responsabile negozio')
def modifica_timbratura(id):
    timbratura = Timbratura.query.get(id)
    form = TimbraturaForm(request.form)
    form.dipendente.choices = [(dip.id, dip.username) for dip in Dipendente.query.all()]
    cassiere = Cassiere.query.get(current_user.id)
    form.data.data = timbratura.data
    form.dipendente.data = timbratura.dipendente_id
    form.ora_inizio.data = timbratura.inizio
    form.ora_fine.data = timbratura.fine
    form.pausa.data = timbratura.pausa
    form.assenza.data = timbratura.assenza
    form.descrizione.data = timbratura.descrizione
    form.id_timbratura = timbratura.id

    return render_template("responsabile/timbratura.html", form=form, negozio=cassiere.negozio )


@responsabile.route('/timbratura', methods=['GET', 'POST'], defaults={'id': None})
@responsabile.route('/timbratura/<id>', methods=['POST'])
@login_required
@roles_required('Responsabile negozio')
def timbratura(id):
    form = TimbraturaForm(request.form)
    form.dipendente.choices = [(dip.id, dip.username) for dip in Dipendente.query.all()]
    cassiere = Cassiere.query.get(current_user.id)
    if request.method == 'POST':
        if form.validate():
            from datetime import datetime, date
            if id is None:
                current_app.logger.info("Aggiungi timbratura")
                timbratura = Timbratura()
            else:
                timbratura = Timbratura.query.get(id)
            timbratura.data = form.data.data
            timbratura.dipendente_id = form.dipendente.data
            timbratura.inizio = form.ora_inizio.data
            timbratura.fine = form.ora_fine.data
            timbratura.pausa = form.pausa.data
            timbratura.assenza = form.assenza.data
            timbratura.descrizione = form.descrizione.data
            secondi_totali = (datetime.combine(date.today(), timbratura.fine) -  datetime.combine(date.today(), timbratura.inizio)).total_seconds()
            secondi_pausa =(timbratura.pausa.hour * 60 + timbratura.pausa .minute) * 60
            secondi_assenza = (timbratura.assenza.hour * 60 + timbratura.assenza .minute) * 60
            timbratura.ore_lavorate = secondi_totali - secondi_pausa - secondi_assenza
            db.session.add(timbratura)
            db.session.commit()

            return redirect(url_for('responsabile.home_responsabile', panel='timbrature'))
        else:
            errors = ', '.join(form.errors)
            flash(u'Timbratura con dati invalidi: ' + errors, 'error')
            current_app.logger.error(u'Timbratura con dati invalidi: {}'.format(errors))

    return render_template("responsabile/timbratura.html", form=form, negozio=cassiere.negozio )


@responsabile.route('/spese', methods=['GET', 'POST'], defaults={'id': None})
@responsabile.route('/spese/<id>', methods=['POST'])
@login_required
@roles_required('Responsabile negozio')
def spese(id):
    form = SpeseForm(request.form)
    form.dipendente.choices = prepara_lista_dipendenti()
    cassiere = Cassiere.query.get(current_user.id)
    if request.method == 'POST' and form.validate():
        return redirect(url_for('responsabile.home_responsabile', panel='spese'))
    return render_template("responsabile/spesa.html", form=form, negozio=cassiere.negozio )



def crea_spesa_aziendale(form, id):
    current_app.logger.info('Gestisco spesa aziendale')
    cassiere = Cassiere.query.get(current_user.id)
    #Controllo se spesa esiste
    spesa = Spesa.query.get(id)
    if spesa is None:
        current_app.logger.info('Spesa con id {} non esiste'.format(id))
        spesa = Spesa()

    spesa.causale=dict(form.causale.choices).get(form.causale.data)
    spesa.descrizione=form.descrizione.data
    spesa.importo=float(form.importo.data)
    spesa.data=form.data.data
    spesa.km=form.km_auto.data if form.km_auto.data != '' else 0
    spesa.targa=form.targa_auto.data
    spesa.id_cassiere=current_user.id
    spesa.cassa_id = form.cassa.data
    spesa.negozio_id= cassiere.negozio_id
    spesa.societa_id = cassiere.negozio.societa_id
    spesa.dipendente_id = form.dipendente.data

    db.session.add(spesa)
    db.session.commit()


def prepara_lista_dipendenti():
    current_app.logger.debug('prepara_lista_dipendenti')
    lista_dipendenti = [(dip.id, dip.username) for dip in Dipendente.query.all()]
    lista_dipendenti.insert(0,(0,""))
    return lista_dipendenti



@responsabile.route('/spesa_aziendale',  defaults={'id': None}, methods=['GET', 'POST'])
@responsabile.route('/spesa_aziendale/<id>', methods=['POST'])
@login_required
@roles_required('Responsabile negozio')
def spesa_aziendale(id):
    form = SpesaAziendaleForm(request.form)
    form.dipendente.choices = prepara_lista_dipendenti()
    cassiere = Cassiere.query.get(current_user.id)
    form.cassa.choices = prepara_casse(cassiere)

    if request.method == 'POST':
        if form.validate():
            crea_spesa_aziendale(form, id)
            #Recupero le spese del negozio
            lista_spese = lista_spese_negozio(cassiere)
            return redirect(url_for('responsabile.home_responsabile', panel='spese',
                                    lista_spese=lista_spese,
                                    negozio = cassiere.negozio))
        else:
            errors = ', '.join(form.errors)
            flash(u'Spesa con dati invalidi: ' + errors, 'error')
            current_app.logger.error(u'Spesa con dati invalidi: {}'.format(errors))
            return render_template("responsabile/spesa_aziendale.html",  form=form,negozio = cassiere.negozio)

    return render_template("responsabile/spesa_aziendale.html", form=form, negozio = cassiere.negozio)


def lista_spese_negozio(cassiere):
    #casse = Cassa.query.filter(Cassa.negozio == cassiere.negozio).all()
    #current_app.logger.debug(casse)
    #lista_spese = Spesa.query.filter(Spesa.cassa_id.in_([cassa.id for cassa in casse]),Spesa.data==datetime.date.today()).all()
    lista_spese = Spesa.query.filter(Spesa.negozio_id == cassiere.negozio_id).all()
    return lista_spese


def prepara_casse(cassiere):
    casse_negozio = [(cassa.id, cassa.matricola) for cassa in cassiere.negozio.casse]
    #casse_negozio.insert(0, (0, "BOX"))
    return casse_negozio


@responsabile.route('/modifica_spesa/<id>', methods=['GET'])
@login_required
@roles_required('Responsabile negozio')
def modifica_spesa(id):
    current_app.logger.debug(request.form)
    spesa = Spesa.query.get(id)
    current_app.logger.debug(spesa)
    form = SpesaAziendaleForm(request.form)
    form.dipendente.choices = prepara_lista_dipendenti()
    cassiere = Cassiere.query.get(current_user.id)
    form.cassa.choices = prepara_casse(cassiere)
    form.dipendente.data = spesa.dipendente_id
    form.data.data = spesa.data
    form.causale.data = spesa.causale
    form.cassa.data = spesa.cassa_id
    form.descrizione.data = spesa.descrizione
    form.importo.data = spesa.importo
    form.km_auto.data = spesa.km
    form.targa_auto.data = spesa.targa
    form.id_spesa = id

    return render_template("responsabile/spesa_aziendale.html", form=form, negozio=cassiere.negozio )


@responsabile.route('/elimina_spesa/<id>', methods=['GET'])
@login_required
@roles_required('Responsabile negozio')
def elimina_spesa(id):
    current_app.logger.debug(request.form)
    cassiere = Cassiere.query.get(current_user.id)
    spesa = Spesa.query.get(id)
    current_app.logger.debug(spesa)
    if spesa is not None:
        db.session.delete(spesa)
        db.session.commit()
    else:
        current_app.logger.error('id_spesa non contenuto nella form')
        flash(u'Impossibile cancellare spesa', 'error')

    return redirect(url_for('responsabile.home_responsabile', panel='spese',
                            lista_spese=lista_spese_negozio(cassiere),
                            negozio = cassiere.negozio))


@responsabile.route('/chiamata/apparecchiature_negozio/<negozio>', methods=[ 'GET', 'POST'])
@login_required
@roles_required('Responsabile negozio')
def apparecchiature_negozio(negozio):
    apparecchiature = Apparecchiatura.query.filter_by(negozio_id = negozio).all()

    app_array = []
    for app in apparecchiature:
        appObj = {}
        appObj['id'] = app.id
        appObj['descrizione'] = app.descrizione
        app_array.append(appObj)

    return jsonify({'apparecchiature' : app_array})


@responsabile.route('/chiamata/apparecchiature_fornitore/<apparecchiatura>', methods=[ 'GET', 'POST'])
@responsabile.route('/apparecchiature_fornitore/<apparecchiatura>', methods=[ 'GET', 'POST'])
@login_required
@roles_required('Responsabile negozio')
def apparecchiature_fornitore(apparecchiatura):
    apparecchiatura = Apparecchiatura.query.get(apparecchiatura)
    app_array = []
    appObj = {}
    appObj['id'] = apparecchiatura.fornitore.id
    appObj['nome'] = apparecchiatura.fornitore.nome
    appObj['cell'] = apparecchiatura.fornitore.cell
    appObj['mail'] = apparecchiatura.fornitore.email
    app_array.append(appObj)
    current_app.logger.debug(app_array)

    return jsonify({'fornitore' : app_array})

@responsabile.route('/chiamata/', defaults={'id': None}, methods=[ 'GET', 'POST'])
@responsabile.route('/chiamata/<id>', methods=[ 'GET', 'POST'])
@login_required
@roles_required('Responsabile negozio')
def chiamata(id):
    form = ChiamataForm(request.form)
    cassiere = Cassiere.query.get(current_user.id)
    apparecchiature = [(app.id, app.descrizione) for app in Apparecchiatura.query.filter_by(negozio_id = cassiere.negozio_id).all()]
    apparecchiature.insert(0,(0,""))
    form.apparecchiatura.choices=apparecchiature
    if request.method == 'POST':
        if form.validate():
            #chack if is an update
            if id:
                chiamata = Chiamata.query.get(id)
            else:
                chiamata = Chiamata()

            app = Apparecchiatura.query.filter(Apparecchiatura.id == form.apparecchiatura.data).first()
            current_app.logger.debug(chiamata)
            chiamata.problema = form.descrizione.data
            chiamata.data_apertura= form.data_apertura.data

            chiamata.data_chiusura = form.data_chiusura.data
            chiamata.ora_apertura = form.ora_inizio.data
            chiamata.ora_chiusura = form.ora_fine.data
            chiamata.esito = form.esito.data
            chiamata.apparecchiatura = app
            chiamata.fornitore = app.fornitore
            chiamata.dipendente = Dipendente.query.get(current_user.id)
            app.fornitore.chiamate.append(chiamata)

            db.session.add(chiamata)
            db.session.add(app)
            db.session.commit()
            return redirect(url_for('responsabile.home_responsabile', panel='chiamate', negozio = cassiere.negozio))
        else:
            errors = ', '.join(form.errors)
            flash(u'Chiamata con dati invalidi: ' + errors, 'error')
            return render_template("responsabile/chiamata.html",  form=form, negozio = cassiere.negozio)


    return render_template('responsabile/chiamata.html', form=form, negozio = cassiere.negozio)


@responsabile.route('/modifica_chiamata', methods=[ 'GET', 'POST'])
@login_required
@roles_required('Responsabile negozio')
def modifica_chiamata():
    id = request.form['id_chiamata']
    chiamata = Chiamata.query.get(id)
    current_app.logger.debug(chiamata.id)
    form = ChiamataForm()
    form.chiamata_id.data = id
    form.apparecchiatura.choices=[(app.id, app.descrizione) for app in Apparecchiatura.query.filter_by(negozio_id = chiamata.apparecchiatura.negozio.id).all()]
    form.apparecchiatura.data = chiamata.apparecchiatura.id
    form.data_apertura.data = chiamata.data_apertura
    form.fornitore.data = chiamata.fornitore.nome
    form.contatto.data = chiamata.fornitore.cell
    form.descrizione.data = chiamata.problema


    cassiere = Cassiere.query.get(current_user.id)
    return render_template("responsabile/chiamata.html",  form=form, negozio = cassiere.negozio)

@responsabile.route('/chiusura_chiamata/<id>', methods=[ 'GET', 'POST'])
@login_required
@roles_required('Responsabile negozio')
def chiusura_chiamata(id):
    chiamata = Chiamata.query.get(id)
    current_app.logger.debug(chiamata.id)
    form = ChiamataForm()
    form.chiamata_id.data = id
    form.apparecchiatura.choices=[(app.id, app.descrizione) for app in Apparecchiatura.query.filter_by(negozio_id = chiamata.apparecchiatura.negozio.id).all()]
    form.apparecchiatura.data = chiamata.apparecchiatura.id
    form.data_apertura.data = chiamata.data_apertura
    form.fornitore.data = chiamata.fornitore.nome
    form.contatto.data  = chiamata.fornitore.cell
    form.descrizione.data = chiamata.problema


    cassiere = Cassiere.query.get(current_user.id)
    return render_template("responsabile/chiusura_chiamata.html",  form=form, negozio = cassiere.negozio)

@responsabile.route('/chiudi_chiamata/<id>', methods=[ 'POST'])
@login_required
@roles_required('Responsabile negozio')
def chiudi_chiamata(id):
    chiamata = Chiamata.query.get(id)
    current_app.logger.debug(chiamata.id)
    form = ChiamataForm(request.form)
    chiamata.data_chiusura = form.data_chiusura.data
    chiamata.ora_apertura = form.ora_inizio.data
    chiamata.ora_chiusura = form.ora_fine.data
    chiamata.esito = form.esito.data

    db.session.add(chiamata)
    db.session.commit()

    cassiere = Cassiere.query.get(current_user.id)
    return redirect(url_for('responsabile.home_responsabile', panel='chiamate', subpanel='chiuse', negozio = cassiere.negozio))


@responsabile.route('/elimina_chiamata/<id>', methods=[ 'POST'])
@login_required
@roles_required('Responsabile negozio')
def elimina_chiamata(id):
    chiamata = Chiamata.query.get(id)
    current_app.logger.info(chiamata)
    db.session.delete(chiamata)
    db.session.commit()

    cassiere = Cassiere.query.get(current_user.id)
    return redirect(url_for('responsabile.home_responsabile', panel='chiamate', subpanel='chiuse', negozio = cassiere.negozio))