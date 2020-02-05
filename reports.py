from flask import Blueprint, render_template
from flask_user import roles_required, login_required

from .models import Versamento

reports= Blueprint('reports', __name__)

@reports.route('/report')
@login_required
@roles_required('Amministratore')
def report():
    versamenti = Versamento.query.filter_by(cassa_id = 1).all()
    labels = [vers.data for vers in versamenti]
    data = [vers.totale_fiscale for vers in versamenti]
    #labels = ["Red", "Blue", "Yellow", "Green", "Purple", "Orange"]
    #data = [12, 19, 3, 5, 2, 3]
    return render_template('admin/report1.html', labels=labels, data=data)