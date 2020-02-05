
def is_admin(user):
    for role in user.roles:
        if role.name == 'Amministratore':
            return True
    return False


def is_cassiere(user):
    for role in user.roles:
        if role.name == 'Cassiere':
            return True
    return False


def is_responsabile_negozio(user):
    for role in user.roles:
        if role.name == 'Responsabile negozio':
            return True
    return False

def is_operator(user):
    for role in user.roles:
        if role.name == 'Commesso':
            return True
    return False
