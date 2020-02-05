import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import current_user, login_required
from flask_user import roles_required

from .form_validator import NegozioForm, UserRole, DipendenteForm, CassiereForm, FornitoreForm, ApparecchiaturaForm, AdminVersamentoForm
from .static_data import tipi_contratto
from .models import Cassiere, Negozio, Versamento, Cassa, User, Role, Dipendente, Societa, Fornitore, Apparecchiatura, StatoDipendente, TipoContratto, TipoApparecchiatura
from . import db


main = Blueprint('main', __name__)


@main.route('/', methods=['GET', 'POST'])
@login_required
def index():
    current_app.logger.debug('index')
    if current_user.is_authenticated:
        cassiere = Cassiere.query.get(current_user.id)
        if cassiere is not None:
            return render_template('index.html', negozio=cassiere.negozio)
    return render_template('index.html')



@main.route('/select_role', methods=['GET', 'POST'])
@login_required
@roles_required('Amministratore')
def select_role():
    form = UserRole(request.form)
    if request.method == 'POST':
        role_id = form.ruolo.data
        current_app.logger.info('Selected role: ' + role_id)
        role_name = Role.query.get(role_id)
        return redirect(url_for('main.utente', role=role_name.name))

    return render_template('admin/tipo_utente.html', form=form)


@main.route('/utenti/<role>', methods=['GET', 'POST'])
@login_required
@roles_required('Amministratore')
def utente(role):
    current_app.logger.info('Ruolo utente: ' + role)
    if role in ['Cassiere', 'Responsabile negozio']:
        form = CassiereForm(request.form)
        form.negozio.choices = [(neg.id, neg.descrizione) for neg in Negozio.query.all()]
        current_app.logger.info(form.negozio.choices)
    else:
        form = DipendenteForm(request.form)

    form.stato.choices = [(stato.id, stato.stato) for stato in StatoDipendente.query.all()]
    ruolo = role
    if request.method == 'POST':
        if form.validate():
            #Controllo se nome utente esiste
            user = User.query.filter(User.name == form.username.data).first()
            if user is None:
                user = User(name=form.username.data, password=form.password.data)
            user_role = Role.query.filter_by(name=ruolo).first()
            current_app.logger.debug('Ruolo utente dal DB {}'.format(user_role.name))
            statoDipendente = StatoDipendente.query.get(form.stato.data)
            if user_role:
                user.roles.append(user_role)
            else:
                current_app.logger.error('Ruolo {} non trovato nel database'.format(ruolo), 'error')
                flash('Ruolo {} non trovato nel database'.format(ruolo), 'error')
                return redirect(url_for('main.utente', role=role))

            if role in ['Cassiere', 'Responsabile negozio']:
                negozio = Negozio.query.get(form.negozio.data)
                current_app.logger.debug('Creo dipendente in negozio {}'.format(negozio.descrizione))

                dipendente = Cassiere.query.filter(Cassiere.username == form.username.data).first()
                if dipendente is None:
                    dipendente = Cassiere()
                    negozio.cassieri.append(dipendente)
                    dipendente.negozio = negozio
                else:
                    #se cambia negozio rimuovo vecchio e metto nuovo
                    dipendente.negozio_id = form.negozio.data



            else:
                current_app.logger.debug('Creo dipendente con user.id {}'.format(user))
                dipendente = Dipendente()

            dipendente.username=form.username.data
            dipendente.nome = form.nome.data
            dipendente.cognome = form.cognome.data
            dipendente.residenza = form.residenza.data
            dipendente.banca = form.banca.data
            dipendente.iban = form.iban.data
            dipendente.base = float(form.base.data)
            dipendente.stato = statoDipendente.stato
            dipendente.user = user
            user.dipendente = dipendente
            current_app.logger.debug('Dipendente con user {}'.format(user))
            db.session.add(dipendente)
            db.session.add(user)
            db.session.commit()
            current_app.logger.info('Dipendente {} creato con success'.format(dipendente.username))

            return redirect(url_for('main.home_admin', panel='utenti'))
        else:
            errors = ', '.join(form.errors)
            flash(u'Utente con dati invalidi: ' + errors, 'error')
            current_app.logger.error(u'Utente con dati invalidi: {}'.format(errors))
            return redirect(url_for('main.utente', role=role))

    if request.method == 'GET':
        return render_template('admin/utente.html', form=form, ruolo=ruolo)



@main.route('/elimina_utente/<id>', methods=['POST'])
@login_required
@roles_required('Amministratore')
def elimina_utente(id):
    current_app.logger.info('ID utente da eliminare {}'.format(id))
    if request.method == 'POST':
        dipendente = Dipendente.query.get(id)
        utente = User.query.get(id)
        db.session.delete(dipendente)
        db.session.delete(utente)
        db.session.commit()
        current_app.logger.info('Utente eliminato con successo')

    return render_template('admin/utenti_admin.html', panel='utenti', lista_utenti=getListaUtenti(), lista_negozi=Negozio.query.all())


@main.route('/modifica_utente/<id>', methods=['GET'])
@login_required
@roles_required('Amministratore')
def modifica_utente(id):
    current_app.logger.info('ID utente da modificare {}'.format(id))

    dipendente = Cassiere.query.get(id)
    if dipendente == None:
        dipendente = Dipendente.query.get(id)

    current_app.logger.info('Utente con ruolo {}'.format(dipendente.user.roles[0].name))
    if dipendente.user.roles[0].name in ['Cassiere', 'Responsabile negozio']:
        form = CassiereForm(request.form)
        form.negozio.choices = [(neg.id, neg.descrizione) for neg in Negozio.query.all()]
        current_app.logger.info(form.negozio.choices)
        form.negozio.data = dipendente.negozio.id
    else:
        form = DipendenteForm(request.form)

    form.stato.choices = [(stato.id, stato.stato) for stato in StatoDipendente.query.all()]
    form.stato.data = dipendente.stato
    form.nome.data = dipendente.nome
    form.username.data = dipendente.username
    form.banca.data = dipendente.banca
    form.cognome.data = dipendente.cognome
    form.base.data = dipendente.base
    form.iban.data = dipendente.iban
    form.password.data = dipendente.user.password
    form.residenza.data = dipendente.residenza


    return render_template('admin/utente.html', form=form, ruolo=dipendente.user.roles[0].name,lista_negozi=Negozio.query.all())


@main.route('/home_admin/<panel>',  defaults={'id': None, 'interval': None})
@main.route('/home_admin/<panel>/<id>', defaults={'interval': None})
@main.route('/home_admin/<panel>/<id>/<interval>')
@login_required
@roles_required('Amministratore')
def home_admin(panel, id, interval):
    panello = panel
    if panello == 'utenti':
        return render_template('admin/utenti_admin.html', panel=panello, lista_utenti=getListaUtenti(id), lista_negozi=Negozio.query.all())
    if panello == 'versamenti':
        return render_template('admin/versamenti_admin.html', panel=panello, lista_versamenti=getListaVersamenti(id, interval), lista_negozi=Negozio.query.all())
    if panello == 'negozi':
        return render_template('admin/negozi_admin.html', panel=panello, lista_negozi=Negozio.query.all())
    if panello == 'fornitori':
        return render_template('admin/fornitori_admin.html', panel=panello, lista_fornitori=Fornitore.query.all())
    if panello == 'societa':
        return render_template('admin/societa_admin.html', panel=panello, lista_societa=Societa.query.all())
    if panello == 'apparecchiature':
        return render_template('admin/apparecchiature_admin.html', panel=panello, lista_apparecchiature=getListaApparecchiature(id), lista_negozi=Negozio.query.all())
    return render_template('admin/home_admin.html', panel=panello)


def getListaApparecchiature(id):
    if id is None:
        apparecchiature = Apparecchiatura.query.all()
    else :
        apparecchiature = Apparecchiatura.query.filter(Apparecchiatura.negozio_id == id).all()
    return apparecchiature


def getListaVersamenti(id, interval):
    current_app.logger.info('getListaVersamenti({}, {})'.format(id,interval))
    if id is None:
        intialDate = datetime.date.today() - datetime.timedelta(days=7)
        versamenti = Versamento.query.filter(Versamento.data > intialDate).order_by(Versamento.data.desc()).all()
    elif interval:
        intialDate = datetime.date.today() - datetime.timedelta(days=int(interval))
        versamenti = Versamento.query.filter(Versamento.data > intialDate).order_by(Versamento.data.desc()).all()
    else :
        versamenti = Versamento.query.filter(Versamento.negozio_id == id).all()
    return versamenti



def getListaUtenti(id):
    if id is None:
        dipendenti = Dipendente.query.all()
    else :
        dipendenti = Cassiere.query.filter(Cassiere.negozio_id == id).all()
    lista_utenti = []
    for dipendente in dipendenti:
        cassiere = Cassiere.query.get(dipendente.id)
        if cassiere:
            negozio = cassiere.negozio.descrizione
        else:
            negozio = ''
        lista_utenti.append({'dipendente': dipendente, 'ruolo': dipendente.user.roles[0], 'negozio': negozio})
    return lista_utenti


@main.route('/elimina_versamento/<id>', methods=['GET'])
@login_required
@roles_required('Amministratore')
def elimina_versamento(id):
    return redirect(url_for('main.home_admin', panel='versamenti'))


@main.route('/modifica_versamento/<id>', methods=['GET'])
@login_required
@roles_required('Amministratore')
def modifica_versamento(id):
    form = AdminVersamentoForm(request.form)
    if request.method == 'GET':
        versamento = Versamento.query.get(id)
        current_app.logger.info(versamento)
        form.data.data = versamento.data
        form.negozio = versamento.negozio.descrizione
        form.spedito.data = versamento.spedito_agenzia
        form.totale_fiscale.data = versamento.totale_fiscale
        form.totale.data = versamento.totale
        form.chiusura_fiscale.data = versamento.chiusura_fiscale
        form.differenza.data = versamento.differenza
        form.resi.data = versamento.resi
        form.bancomat.data = versamento.bancomat
        form.fondo_cassa.data = versamento.fondo_cassa
        form.contante.data = versamento.contante
        form.cassa = versamento.cassa.matricola
        form.id_versamento = id
        current_app.logger.info(versamento)

        return render_template('admin/modifica_versamento.html', panel='versamenti', form=form)


@main.route('/salva_versamento', methods=['POST'])
@login_required
@roles_required('Amministratore')
def salva_versamento():
    form = AdminVersamentoForm(request.form)
    if request.method == 'POST':
        if form.validate():
            current_app.logger.debug(form.id_versamento)

            versamento = Versamento.query.get(form.id_versamento.data)
            versamento.data = form.data.data
            versamento.spedito_agenzia = form.spedito.data
            versamento.totale_fiscale = form.totale_fiscale.data
            versamento.totale = form.totale.data
            versamento.chiusura_fiscale = form.chiusura_fiscale.data
            versamento.differenza = form.differenza.data
            versamento.resi = form.resi.data
            versamento.bancomat = form.bancomat.data
            versamento.fondo_cassa = form.fondo_cassa.data
            versamento.contante = form.contante.data
            #versamento.cassa =form.cassa.data

            db.session.add(versamento)
            db.session.commit()
        else:
            errors = ', '.join(form.errors)
            flash(u'Versamento con dati invalidi: ' + errors, 'error')
            current_app.logger.error(u'Versamento con dati invalidi: {}'.format(errors))

        return redirect(url_for('main.home_admin', panel='versamenti'))



@main.route('/modifica_societa/<id>', methods=['GET'])
@login_required
@roles_required('Amministratore')
def modifica_societa(id):
    societa = Societa.query.filter(Societa.id == id).first()
    if societa:
        current_app.logger.debug('Inizio a cancellare societa {}'.format(societa.name))
        db.session.delete(societa)
        db.session.commit()
        current_app.logger.info('societa {} cancellata'.format(societa.name))
    return redirect(url_for('main.home_admin', panel='societa'))


@main.route('/elimina_societa/<id>', methods=['GET'])
@login_required
@roles_required('Amministratore')
def elimina_societa(id):
    societa = Societa.query.filter(Societa.id == id).first()
    if societa:
        current_app.logger.debug('Inizio a cancellare societa {}'.format(societa.name))
        db.session.delete(societa)
        db.session.commit()
        current_app.logger.info('societa {} cancellata'.format(societa.name))
    return redirect(url_for('main.home_admin', panel='societa'))



@main.route('/elimina_negozio/<id>', methods=['GET'])
@login_required
@roles_required('Amministratore')
def elimina_negozio(id):
    current_app.logger.debug('Elimina negozio')
    negozio = Negozio.query.filter(Negozio.id == id).first()
    if negozio:
        current_app.logger.debug('Inizio a cancellare negozio {} e sue casse'.format(negozio.descrizione))
        for cassa in negozio.casse:
            current_app.logger.debug('cancello cassa {}'.format(cassa.matricola))
            db.session.delete(cassa)
        db.session.delete(negozio)
        db.session.commit()
        current_app.logger.info('negozio {} cancellato'.format(negozio.descrizione))

    return redirect(url_for('main.home_admin', panel='negozi'))


@main.route('/modifica_negozio/<id>', methods=['GET'])
@login_required
@roles_required('Amministratore')
def modifica_negozio(id):
    current_app.logger.debug('Elimina negozio')
    negozio = Negozio.query.filter(Negozio.id == id).first()
    form = NegozioForm()
    form.nome.data = negozio.descrizione
    form.societa.choices = [(societa.id, societa.name) for societa in Societa.query.all()]
    form.societa.data = negozio.societa.id
    form.localita.data = negozio.localita
    form.indirizzo.data = negozio.indirizzo
    num_casse = 1
    for cassa in negozio.casse:
        if num_casse == 1:
            form.cassa1.data = cassa.matricola
        elif num_casse == 2:
            form.cassa2.data = cassa.matricola
        elif num_casse == 3:
            form.cassa3.data = cassa.matricola
        elif num_casse == 4:
            form.cassa4.data = cassa.matricola
        elif num_casse == 5:
            form.cassa5.data = cassa.matricola
        elif num_casse == 6:
            form.cassa6.data = cassa.matricola
        elif num_casse == 7:
            form.cassa7.data = cassa.matricola
        elif num_casse == 8:
            form.cassa8.data = cassa.matricola
        elif num_casse == 9:
            form.cassa9.data = cassa.matricola
        elif num_casse == 10:
            form.cassa10.data = cassa.matricola
        num_casse = num_casse + 1

    return render_template('admin/negozio.html', form=form, lista_societa=Societa.query.all())


@main.route('/negozio', methods=['GET', 'POST'])
@login_required
@roles_required('Amministratore')
def negozio():
    form = NegozioForm(request.form)
    form.societa.choices = [(societa.id, societa.name) for societa in Societa.query.all()]
    if request.method == 'POST':
        if form.validate():
            current_app.logger.debug('Controllo negozio {}'.format(form.nome.data))
            #Controllo se negozio esiste basandosi sul nome del negozio
            negozio = Negozio.query.filter(Negozio.descrizione == form.nome.data).first()
            if negozio is None:
                current_app.logger.info("Nuovo negozio {}".format(form.nome.data))
                negozio = Negozio()

            negozio.descrizione = form.nome.data
            negozio.localita = form.localita.data
            negozio.indirizzo = form.indirizzo.data
            negozio.societa_id = form.societa.data
            societa = Societa.query.get(form.societa.data)
            societa.negozi.append(negozio)
            current_app.logger.debug('Aggiunto negozio a societa {}'.format(societa.name))
            current_app.logger.debug(negozio)

            # Casse
            #Aggiungo di default il BOX
            #box = Cassa(matricola='BOX',negozio_id=negozio.id)
            #negozio.casse.append(box)
            #db.session.add(box)
            """
            Gestione delle casse
                - cerco le casse associate al negozio
                - creo lista nuove casse dalla form
                - aggiungo casse nuove
                - rimuovo casse cancellate
            """
            lista_casse_negozio = Cassa.query.filter(Cassa.negozio_id == negozio.id).all()
            lista_casse_esistenti = [x.matricola for x in  lista_casse_negozio]
            lista_casse_form = []
            if form.cassa1.data != '':
                lista_casse_form.append(form.cassa1.data)
            if form.cassa2.data != '':
                lista_casse_form.append(form.cassa2.data)
            if form.cassa3.data != '':
                lista_casse_form.append(form.cassa3.data)
            if form.cassa4.data != '':
               lista_casse_form.append(form.cassa4.data)
            if form.cassa5.data != '':
                lista_casse_form.append(form.cassa5.data)
            if form.cassa6.data != '':
                lista_casse_form.append(form.cassa6.data)
            if form.cassa7.data != '':
                lista_casse_form.append(form.cassa7.data)
            if form.cassa8.data != '':
               lista_casse_form.append(form.cassa8.data)
            if form.cassa9.data != '':
                lista_casse_form.append(form.cassa9.data)
            if form.cassa10.data != '':
                lista_casse_form.append(form.cassa10.data)

            current_app.logger.debug(lista_casse_esistenti)
            current_app.logger.debug(lista_casse_form)
            nuove_casse  = [item for item in lista_casse_form if item not in lista_casse_esistenti]
            casse_da_rimuovere = [item for item in lista_casse_esistenti if item not in lista_casse_form]
            current_app.logger.debug(nuove_casse)
            current_app.logger.debug(casse_da_rimuovere)

            for nuova_cassa in nuove_casse:
                current_app.logger.info('Creo nuova cassa {}'.format(nuova_cassa))
                cassa = Cassa(matricola=nuova_cassa, negozio_id=negozio.id, societa_id=negozio.societa_id)
                db.session.add(cassa)

            for rimuovi_cassa in casse_da_rimuovere:
                current_app.logger.info('Rimuovo cassa {}'.format(rimuovi_cassa))
                cassa = Cassa.query.filter(Cassa.matricola == rimuovi_cassa, Cassa.negozio_id == negozio.id).first()
                db.session.delete(cassa)

            db.session.add(negozio)
            db.session.add(societa)
            db.session.commit()
            current_app.logger.info("Negozio {} creato con successo".format(negozio.descrizione))

            return redirect(url_for('main.home_admin', panel='negozi'))
        else:
            errors = ', '.join(form.errors)
            flash(u'Negozio con dati invalidi: ' + errors, 'error')
            current_app.logger.error(u'Negozio con dati invalidi: {}'.format(errors))
            return redirect(url_for('main.negozio'))

    if request.method == 'GET':
        return render_template('admin/negozio.html', form=form, lista_societa=Societa.query.all())


@main.route('/fornitore/nuovo', methods=['GET'])
@login_required
@roles_required('Amministratore')
def nuovo_fornitore():
    form = FornitoreForm(request.form)
    return render_template('admin/fornitore.html', form=form, tipi_contratto=tipi_contratto, panel='fornitori')



@main.route('/fornitore', methods=['GET', 'POST'])
@login_required
@roles_required('Amministratore')
def fornitore():
    form = FornitoreForm(request.form)
    if request.method == 'POST':
        if 'cancel' in request.form:
            return render_template('admin/fornitore.html', form=form, tipi_contratto=tipi_contratto, panel='fornitori')

        if form.validate():
            forn = Fornitore(nome=form.nome.data, telefono=form.telefono.data,
                             cell=form.cellulare.data, email=form.email.data,
                             indirizzo=form.indirizzo.data, localita=form.localita.data,
                             contratto=tipi_contratto[form.contratto.data-1][1],
                             descrizione=form.descrizione.data)

            db.session.add(forn)
            db.session.commit()
            current_app.logger.info("Fornitore {} creato con successo".format(forn.email))
            return redirect(url_for('main.home_admin', panel='fornitori'))
        else:
            errors = ', '.join(form.errors)
            flash(u'Fornitore con dati invalidi: ' + errors, 'error')
            current_app.logger.error(u'Fornitore con dati invalidi: {}'.format(errors))
            return render_template('admin/fornitore.html', form=form, tipi_contratto=tipi_contratto, panel='fornitori')

    if request.method == 'GET':
        current_app.logger.info(request.args)
        if 'nuovo_fornitore' in request.args:
            return render_template('admin/fornitore.html', form=form, tipi_contratto=TipoContratto.query.all(), panel='fornitori')
        else:
            return redirect(url_for('main.home_admin', panel='fornitori'))


@main.route('/elimina_fornitore', methods=['POST'])
@login_required
@roles_required('Amministratore')
def elimina_fornitore():
    current_app.logger.info(request.form)
    if 'id_fornitore' in request.form:
        forn = Fornitore.query.get(request.form['id_fornitore'])
        current_app.logger.debug(forn)
        if forn is not None:
            db.session.delete(forn)
            db.session.commit()
            current_app.logger.info('Fornitore {} creato'.format(forn.email))
    else:
        current_app.logger.error(u'Impossibile cancellare fornitore')
        flash(u'Impossibile cancellare fornitore', 'error')

    return redirect(url_for('main.home_admin', panel='fornitori'))



@main.route('/apparecchiatura/', methods=[ 'GET', 'POST'])
@login_required
@roles_required('Amministratore')
def apparecchiatura():
    form = ApparecchiaturaForm(request.form)
    form.negozio.choices=[(neg.id, neg.descrizione) for neg in Negozio.query.all()]
    form.fornitore.choices=[(fornitore.id, fornitore.nome) for fornitore in Fornitore.query.all()]
    form.codice.choices=[(app.id, app.descrizione) for app in TipoApparecchiatura.query.all()]
    if request.method == 'POST':
        if form.validate():
            negozio_id = form.negozio.data
            negozio = Negozio.query.get(negozio_id)
            app = Apparecchiatura(cod_app_id=form.codice.data,descrizione=form.descrizione.data)
            app.negozio=negozio
            negozio.apparecchiature.append(app)
            fornitore = Fornitore.query.get(form.fornitore.data)
            app.fornitore=fornitore
            fornitore.apparecchiature.append(app)
            db.session.add(negozio)
            db.session.add(fornitore)
            db.session.add(app)
            db.session.commit()
            return redirect(url_for('main.home_admin', panel='apparecchiature'))
        else:
            errors = ', '.join(form.errors)
            flash(u'Apparecchiatura con dati invalidi: ' + errors, 'error')
            return render_template("admin/apparecchiatura.html",  form=form)


    return render_template('admin/apparecchiatura.html', form=form)



@main.route('/modifica_apparecchiatura/<id>', methods=['GET'])
@login_required
@roles_required('Amministratore')
def modifica_apparecchiatura(id):
    apparecchiatura = Apparecchiatura.query.get(id)
    form = ApparecchiaturaForm()
    form.negozio.choices=[(neg.id, neg.descrizione) for neg in Negozio.query.all()]
    form.fornitore.choices=[(fornitore.id, fornitore.nome) for fornitore in Fornitore.query.all()]

    form.codice.choices=[(app.id, app.descrizione) for app in TipoApparecchiatura.query.all()]
    form.codice.data = apparecchiatura.cod_app_id
    form.negozio.data = apparecchiatura.negozio
    form.descrizione.data = apparecchiatura.descrizione
    form.fornitore.data = apparecchiatura.fornitore
    return render_template('admin/apparecchiatura.html', form=form)


@main.route('/elimina_apparecchiatura/<id>', methods=['GET'])
@login_required
@roles_required('Amministratore')
def elimina_apparecchiatura(id):
    apparecchiatura = Apparecchiatura.query.get(id)
    if apparecchiatura is not None:
        current_app.logger.info('Elimino apparecchiatura {} da negozio {}'.format(apparecchiatura.descrizione, apparecchiatura.negozio.descrizione))
        db.session.delete(apparecchiatura)
        db.session.commit()
    else:
        flash(u'Impossibile cancellare apparecchiatura', 'error')
        current_app.logger.error(u'Impossibile cancellare apparecchiatura')
    return redirect(url_for('main.home_admin', panel='apparecchiature'))
