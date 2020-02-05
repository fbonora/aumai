import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import current_user, login_required
from flask_user import roles_required

from .form_validator import VersamentoForm,  DettaglioVersamento, calcolaTotale, calcola_reso, calcola_prelievi
from .models import Cassiere, Versamento, Cassa, Contante, Reso, Societa
from . import db


cassiere = Blueprint('cassiere', __name__)


@cassiere.route('/home_cassiere/<panel>')
@login_required
@roles_required('Cassiere')
def home_cassiere(panel):
    panello = panel
    cassiere = Cassiere.query.filter(Cassiere.id == current_user.id).first()

    if cassiere and panello == 'versamenti':
        lista_versamenti = Versamento.query.filter(Versamento.cassiere == current_user.id).filter(Versamento.data == datetime.date.today()).all()
        return render_template('cassiere/versamenti_cassiere.html', panel=panello,  lista_versamenti=lista_versamenti, negozio=cassiere.negozio)

    return render_template('cassiere/home_cassiere.html', panel=panello, negozio = cassiere.negozio)


@cassiere.route('/versamento', methods=['GET', 'POST'])
@login_required
@roles_required('Cassiere')
def versamento():
    form = VersamentoForm(request.form)
    if request.method == 'POST':
        if form.validate():
            versamento = Versamento(cassiere=current_user.dipendente.id,
                                    data=datetime.datetime.fromisoformat(datetime.datetime.now().strftime('%Y-%m-%d')))
            versamento.cassa = form.cassa.data
            versamento.fondo_cassa = form.fondo_cassa.data
            versamento.contante = form.contante.data
            versamento.bancomat = form.bancomat.data
            versamento.totale = form.totale.data
            versamento.chiusura_fiscale = form.chiusura_fiscale.data
            versamento.resi = form.resi.data
            #versamento.totale_fiscale = form.totale_fiscale.data
            #versamento.differenza = form.differenza.data

            db.session.add(versamento)
            db.session.commit()

            return redirect(url_for('cassiere.home_cassiere', panel='versamenti'))
        else:
            errors = ', '.join(form.errors)
            flash(u'Versamento con dati invalidi: ' + errors, 'error')
            current_app.logger.error('Versamento con dati invalidi')
            return redirect(url_for('cassiere.versamento'))

    if request.method == 'GET':
        negozio = current_user.dipendente.negozio

        return render_template('cassiere/versamento.html', form=form, negozio=negozio)



@cassiere.route('/versamento/resoconto', methods=['GET', 'POST'])
@login_required
@roles_required('Cassiere')
def resoconto_versamento():
    current_app.logger.debug(request.form)
    cassiere = Cassiere.query.filter(Cassiere.id == current_user.id).first()
    return render_template('cassiere/versamenti_cassiere.html', negozio = cassiere.negozio)


@cassiere.route('/versamento/dettaglio', defaults={'id': None}, methods=['GET', 'POST'])
@cassiere.route('/versamento/dettaglio/', defaults={'id': None}, methods=['GET', 'POST'])
@cassiere.route('/versamento/dettaglio/<id>', methods=['GET', 'POST'])
@login_required
@roles_required('Cassiere')
def dettaglio_versamento(id):
    form = DettaglioVersamento(request.form)
    if id:
        form.id_versamento.data = id
    cassiere = Cassiere.query.filter(Cassiere.id == current_user.id).first()
    casse = [(cassa.id, cassa.matricola) for cassa in Cassa.query.filter(Cassa.negozio_id == cassiere.negozio_id).all()]
    casse.insert(0, (0,""))
    form.cassa.choices = casse
    current_app.logger.debug('casse selezionate')
    current_app.logger.debug(casse)
    if request.method == 'POST':
        if form.validate():
            form.totale_contanti.data = calcolaTotale(form)
            form.totale_resi.data = calcola_reso(form)
            #form.totale_prelievo.data = calcola_prelievi(form)
            if form.aggiungi.data == True:
                #aggiugi resoconto
                versamento = crea_versamento(form)

                #Creo dettaglio contanti
                contante = crea_dettagli_contante(form, versamento)

                # Creo dettaglio resi
                resi, resi_da_rimuovere = crea_resi(form, versamento)

                # Sistemo DB
                current_app.logger.debug("Aggiunta dettagli versamento")
                db.session.add(versamento)
                db.session.add(contante)
                for reso in resi:
                    db.session.add(reso)
                for reso_da_rimuovere in resi_da_rimuovere:
                    db.session.delete(reso_da_rimuovere)

                db.session.commit()

                return redirect(url_for('cassiere.home_cassiere', panel='versamenti', negozio = cassiere.negozio))
        else:
            errors = ', '.join(form.errors)
            flash(u'Resoconto con dati invalidi: ' + errors, 'error')
            current_app.logger.error(u'Resoconto con dati invalidi: {} '.format(errors) )
            form = DettaglioVersamento()
            form.cassa.choices = casse
            return render_template("cassiere/dettagli_versamento.html",  form=form, negozio = cassiere.negozio)

    return render_template('cassiere/dettagli_versamento.html', form=form, negozio = cassiere.negozio)


def popola_contante(form, contante):
    form.v_001.data = contante._1_cent
    form.v_002.data = contante._2_cent
    form.v_005.data = contante._5_cent
    form.v_010.data = contante._10_cent
    form.v_020.data = contante._20_cent
    form.v_050.data = contante._50_cent
    form.v_1.data = contante._1_eu
    form.v_2.data = contante._2_eu
    form.v_5.data = contante._5_eu
    form.v_10.data = contante._10_eu
    form.v_20.data = contante._20_eu
    form.v_50.data = contante._50_eu
    form.v_100.data = contante._100_eu
    form.v_200.data = contante._200_eu
    form.v_500.data = contante._500_eu
    return form


def popola_resi(form, resi):
    index = 0
    for reso in resi:
        index = index+ 1
        if index == 1:
            form.ora_reso1.data = reso.ora
            form.scontrino_reso1.data = reso.scontrino
            form.imp_reso1.data = reso.importo
        if index == 2:
            form.ora_reso2.data = reso.ora
            form.scontrino_reso2.data = reso.scontrino
            form.imp_reso2.data = reso.importo
        if index == 3:
            form.ora_reso3.data = reso.ora
            form.scontrino_reso3.data = reso.scontrino
            form.imp_reso3.data = reso.importo
        if index == 4:
            form.ora_reso4.data = reso.ora
            form.scontrino_reso4.data = reso.scontrino
            form.imp_reso4.data = reso.importo

    return form


@cassiere.route('/cassiere/modifica_versamento/<id>', methods=['GET'])
@login_required
@roles_required('Cassiere')
def modifica_versamento(id):
    current_app.logger.debug('Versamento id=' + id)
    # look for versamento
    vers = Versamento.query.get(id)
    current_app.logger.debug(vers)
    #popolo i dati della form dal versamento
    form = DettaglioVersamento(request.form)
    cassiere = Cassiere.query.filter(Cassiere.id == current_user.id).first()
    casse = [(cassa.id, cassa.matricola) for cassa in Cassa.query.filter(Cassa.negozio_id == cassiere.negozio_id).all()]
    casse.insert(0, (0,""))
    form.cassa.choices = casse
    form.fondo_cassa.data = vers.fondo_cassa
    form.cassa.data = vers.cassa_id
    form.totale_contanti.data = vers.contante
    form.bancomat.data = vers.bancomat
    form.totale_resi.data = vers.resi
    #form.totale.data = vers.totale
    #recupero containt del versamento
    contante = Contante.query.filter(Contante.versameto_id == id).first()
    current_app.logger.debug(contante)
    form = popola_contante(form, contante)
    resi = Reso.query.filter(Reso.versamento_id == id).all()
    current_app.logger.debug(resi)
    form = popola_resi(form,resi)
    form.id_versamento.data = vers.id

    current_app.logger.debug('Versamento con ID {}'.format(form.id_versamento.data))

    #return redirect(url_for('cassiere.dettaglio_versamento', id =  vers.id))
    return render_template("cassiere/dettagli_versamento.html",  form=form, negozio = cassiere.negozio)


@cassiere.route('/cassiere/elimina_versamento/<id>', methods=['GET'])
@login_required
@roles_required('Cassiere')
def elimina_versamento(id):
    current_app.logger.debug('Versamento id=' + id)
    # look for versamento
    versamento = Versamento.query.get(id)
    current_app.logger.debug(versamento)
    if versamento is not None:
        #Vanno cancellati anche resi e contanti relativi al versamento
        resi = Reso.query.filter(Reso.versamento_id == versamento.id).all()
        for reso in resi:
            db.session.delete(reso)
        contanti = Contante.query.filter(Contante.versameto_id == versamento.id).all()
        for contante in contanti:
            db.session.delete(contante)
        db.session.delete(versamento)
        db.session.commit()
        current_app.logger.warning("utente {} ha elimonato versamento {}".format(current_user, id))
    return redirect(url_for('cassiere.home_cassiere', panel='versamenti'))


def crea_reso(versamento, importo, scontrino, ora):
    reso = Reso.query.filter(Reso.versamento_id == versamento.id).filter(Reso.ora == ora).filter(Reso.scontrino == scontrino).first()
    current_app.logger.debug('Reso esistente: {}'.format(reso))
    if reso is None:
        reso = Reso()
    reso.data = datetime.datetime.today()
    reso.ora = ora
    reso.scontrino = scontrino
    reso.importo = importo
    reso.versamento = versamento
    versamento.dettagli_resi.append(reso)
    return reso



def crea_resi(form, versamento_id):
    resi = []
    if form.imp_reso1.data:
        resi.append(crea_reso(versamento_id, form.imp_reso1.data, form.scontrino_reso1.data, form.ora_reso1.data))
    if form.imp_reso2.data:
        resi.append(crea_reso(versamento_id, form.imp_reso2.data, form.scontrino_reso2.data, form.ora_reso2.data))
    if form.imp_reso3.data:
        resi.append(crea_reso(versamento_id, form.imp_reso3.data, form.scontrino_reso3.data, form.ora_reso3.data))
    if form.imp_reso4.data:
        resi.append(crea_reso(versamento_id, form.imp_reso4.data, form.scontrino_reso4.data, form.ora_reso4.data))
    if form.imp_reso5.data:
        resi.append(crea_reso(versamento_id, form.imp_reso5.data, form.scontrino_reso5.data, form.ora_reso5.data))
    if form.imp_reso6.data:
        resi.append(crea_reso(versamento_id, form.imp_reso6.data, form.scontrino_reso6.data, form.ora_reso6.data))
    if form.imp_reso7.data:
        resi.append(crea_reso(versamento_id, form.imp_reso7.data, form.scontrino_reso7.data, form.ora_reso7.data))
    if form.imp_reso8.data:
        resi.append(crea_reso(versamento_id, form.imp_reso8.data, form.scontrino_reso8.data, form.ora_reso8.data))
    if form.imp_reso9.data:
        resi.append(crea_reso(versamento_id, form.imp_reso9.data, form.scontrino_reso9.data, form.ora_reso9.data))
    if form.imp_reso10.data:
        resi.append(crea_reso(versamento_id, form.imp_reso10.data, form.scontrino_reso10.data, form.ora_reso10.data))
    if form.imp_reso11.data:
        resi.append(crea_reso(versamento_id, form.imp_reso11.data, form.scontrino_reso11.data, form.ora_reso11.data))
    if form.imp_reso12.data:
        resi.append(crea_reso(versamento_id, form.imp_reso12.data, form.scontrino_reso12.data, form.ora_reso12.data))
    if form.imp_reso13.data:
        resi.append(crea_reso(versamento_id, form.imp_reso13.data, form.scontrino_reso13.data, form.ora_reso13.data))
    if form.imp_reso14.data:
        resi.append(crea_reso(versamento_id, form.imp_reso14.data, form.scontrino_reso14.data, form.ora_reso14.data))
    if form.imp_reso15.data:
        resi.append(crea_reso(versamento_id, form.imp_reso15.data, form.scontrino_reso15.data, form.ora_reso15.data))

    #Devo verificare se vanno rimossi dei resi
    #un reso e' identificato univocamente da id_versamento scontrino
    resi_esistenti = Reso.query.filter(Reso.versamento_id == versamento_id.id).all()
    for reso in resi:
        for existingReso in resi_esistenti:
            if existingReso.scontrino == reso.scontrino:
                resi_esistenti.remove(existingReso)
                break
    current_app.logger.info("Resi da rimuovere")
    current_app.logger.info(resi_esistenti)
    return resi, resi_esistenti


def crea_dettagli_contante(form, versamento):
    contante = Contante.query.filter(Contante.versameto_id == versamento.id).first()
    if contante is None:
        contante = Contante()
    contante.versamento = versamento
    contante.data = datetime.datetime.today()
    contante._1_cent = form.v_001.data
    contante._2_cent = form.v_002.data
    contante._5_cent = form.v_005.data
    contante._10_cent = form.v_010.data
    contante._20_cent = form.v_020.data
    contante._50_cent = form.v_050.data
    contante._1_eu = form.v_1.data
    contante._2_eu = form.v_2.data
    contante._5_eu = form.v_5.data
    contante._10_eu = form.v_10.data
    contante._20_eu = form.v_20.data
    contante._50_eu = form.v_50.data
    contante._100_eu = form.v_100.data
    contante._200_eu = form.v_200.data
    contante._500_eu = form.v_500.data
    return contante


def crea_versamento(form):
    current_app.logger.debug('Cerco versamento con id {}'.format(form.id_versamento.data))
    versamento = Versamento.query.get(form.id_versamento.data)
    if versamento == None:
        current_app.logger.debug('Nuovo versamento')
        versamento = Versamento(cassiere=current_user.dipendente.id,
                                data=datetime.datetime.today())
        cassa = Cassa.query.filter(Cassa.id == form.cassa.data).first()
        societa = Societa.query.get(cassa.negozio.societa_id)
        versamento.societa = societa
        versamento.negozio = cassa.negozio
    versamento.cassa_id = form.cassa.data
    versamento.fondo_cassa = float(form.fondo_cassa.data)
    versamento.contante = float(form.totale_contanti.data)
    versamento.bancomat = float(form.bancomat.data)
    versamento.resi = float(form.totale_resi.data)
    current_app.logger.info('Totale contanti: {}'.format(form.totale_contanti.data))
    current_app.logger.info('Totale Bancomat: {}'.format(form.bancomat.data))
    versamento.totale = float(form.totale_contanti.data) + float(form.bancomat.data)
    versamento.chiusura_fiscale = versamento.totale + versamento.resi
    return versamento

