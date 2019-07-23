import flask
from flask import Flask
from datetime import date



app = Flask(__name__)


@app.route('/')
def home():
    from database import cursor
    entreprise_liste = []
    for row in cursor.execute('''SELECT ID, Nom, Score_organisation.Score, Score_technique.Score, Score_total.Score
    FROM Entreprise,Score_organisation, Score_technique, Score_total
    WHERE Score_organisation.Id_entreprise = Entreprise.ID AND Score_technique.Id_entreprise = Entreprise.ID AND Score_total.Id_entreprise = Entreprise.ID
    ORDER BY ID'''):
        entreprise_liste += [[row[0], row[1], row[2], row[3], row[4]]]
        print(entreprise_liste)
    if(entreprise_liste != [[]]):
        return flask.render_template("home.html.jinja2", entreprise_liste=entreprise_liste)
    else:
        return flask.render_template("home.html.jinja2")

@app.route('/new_entreprise')
def new_entreprise():
    return flask.render_template("new_entreprise.html.jinja2")

@app.route('/add_entreprise', methods=["POST"])
def add_entreprise():
    nom = flask.request.form["Nom"]
    secteur = flask.request.form["Secteur"]
    nombre_employes = flask.request.form["Nombre_employes"]

    from database import cnxn, cursor
    if(cursor.execute('''SELECT COUNT(*) FROM Entreprise''').fetchone()[0]==0):
        last_id=0
    else:
        last_id = (cursor.execute('''SELECT MAX(ID) FROM Entreprise''').fetchone())[0]

    insert_query = '''INSERT INTO Entreprise (ID, Nom, Secteur, Nombre_employes)
                    VALUES (?,?,?,?);'''
    values = (last_id+1, nom, secteur, nombre_employes)
    cursor.execute(insert_query, values)
    cnxn.commit()

    return flask.redirect(flask.url_for("page_formulaire",id_entreprise=last_id+1))

@app.route('/<id_entreprise>/page_formulaire')
def page_formulaire(id_entreprise):
    from database import cursor, cnxn

    organisation_existe = cursor.execute('''SELECT Question1 FROM Formulaire_gouvernance WHERE Id_entreprise = ?''', id_entreprise).fetchone()!=None

    technique_existe = cursor.execute('''SELECT Question1 FROM Formulaire_gestion_systemes WHERE Id_entreprise = ?''', id_entreprise).fetchone()!=None


    if(organisation_existe):

        score_gouvernance = 0
        for question in cursor.execute('''SELECT Question1, Question2, Question3, Question4, Question5,Question6 FROM Formulaire_gouvernance
        WHERE Id_entreprise = ?''', id_entreprise).fetchone():
            score_gouvernance += question
        score_gouvernance = score_gouvernance * 15 / 60

        score_processus_procedures = 0
        for question in cursor.execute('''SELECT Question1, Question2, Question3, Question4, Question5,Question6 FROM Formulaire_processus_procedures
        WHERE Id_entreprise = ?''', id_entreprise).fetchone():
            score_processus_procedures += question
        score_processus_procedures = score_processus_procedures * 30 / 60

        score_roles_responsabilites = 0
        for question in cursor.execute('''SELECT Question1, Question2, Question3, Question4, Question5,Question6 FROM Formulaire_roles_responsabilites
        WHERE Id_entreprise = ?''', id_entreprise).fetchone():
            score_roles_responsabilites += question
        score_roles_responsabilites = score_roles_responsabilites * 15 / 60

        score_outillage = 0
        for question in cursor.execute('''SELECT Question1, Question2, Question3, Question4, Question5,Question6 FROM Formulaire_outillage
                WHERE Id_entreprise = ?''', id_entreprise).fetchone():
            score_outillage += question
        score_outillage = score_outillage * 20 / 60

        score_conduite_du_changement = 0
        for question in cursor.execute('''SELECT Question1, Question2, Question3, Question4, Question5,Question6 FROM Formulaire_conduite_du_changement
                WHERE Id_entreprise = ?''', id_entreprise).fetchone():
            score_conduite_du_changement += question
        score_conduite_du_changement = score_conduite_du_changement * 20 / 60

        score_organisation = round(score_conduite_du_changement + score_outillage + score_roles_responsabilites + score_gouvernance + score_processus_procedures,2)

    if(technique_existe):

        score_gestion_systemes = 0
        for question in cursor.execute('''SELECT Question1, Question2, Question3, Question4, Question5,Question6 FROM Formulaire_gestion_systemes
               WHERE Id_entreprise = ?''', id_entreprise).fetchone():
            score_gestion_systemes += question
        score_gestion_systemes = score_gestion_systemes * 30 / 60

        score_applications = 0
        for question in cursor.execute('''SELECT Question1, Question2, Question3, Question4, Question5,Question6 FROM Formulaire_applications
               WHERE Id_entreprise = ?''', id_entreprise).fetchone():
            score_applications += question
        score_applications = score_applications * 30 / 60

        score_securite = 0
        for question in cursor.execute('''SELECT Question1, Question2, Question3, Question4, Question5,Question6 FROM Formulaire_securite
               WHERE Id_entreprise = ?''', id_entreprise).fetchone():
            score_securite += question
        score_securite = score_securite * 20 / 60

        score_support = 0
        for question in cursor.execute('''SELECT Question1, Question2, Question3, Question4, Question5,Question6 FROM Formulaire_support
                       WHERE Id_entreprise = ?''', id_entreprise).fetchone():
            score_support += question
        score_support = score_support * 10 / 60

        score_outils_collaboratif = 0
        for question in cursor.execute('''SELECT Question1, Question2, Question3, Question4, Question5,Question6 FROM Formulaire_outils_collaboratif
                       WHERE Id_entreprise = ?''', id_entreprise).fetchone():
            score_outils_collaboratif += question
        score_outils_collaboratif = score_outils_collaboratif * 10 / 60

        score_technique = round(
            score_gestion_systemes + score_applications + score_securite + score_support + score_outils_collaboratif, 2)

    if(organisation_existe and technique_existe):
        insert_query_organisation = '''INSERT INTO Score_organisation(Id_entreprise, Score)
                                        VALUES (?,?);'''

        values_organisation = (id_entreprise, score_organisation)

        cursor.execute(insert_query_organisation, values_organisation)
        cnxn.commit()

        insert_query_technique = '''INSERT INTO Score_technique(Id_entreprise, Score)
                                               VALUES (?,?);'''

        values_technique = (id_entreprise, score_technique)

        cursor.execute(insert_query_technique, values_technique)
        cnxn.commit()

        score_total = round((score_technique + score_organisation)/2,2)
        insert_query = '''INSERT INTO Score_total(Id_entreprise, Score, Date)
                                        VALUES (?,?,?);'''
        ajd = date.today()

        values = (id_entreprise, score_total, str(ajd))
        cursor.execute(insert_query, values)
        cnxn.commit()
        return flask.render_template("page_formulaire.html.jinja2", id_entreprise = id_entreprise, score_technique = score_technique,
                                     score_organisation =score_organisation, score_total = score_total)

    elif(organisation_existe):
        return flask.render_template("page_formulaire.html.jinja2", id_entreprise = id_entreprise, score_organisation=score_organisation)

    elif(technique_existe):
        return flask.render_template("page_formulaire.html.jinja2", id_entreprise = id_entreprise, score_technique=score_technique)

    else :
        return flask.render_template("page_formulaire.html.jinja2", id_entreprise=id_entreprise)

@app.route('/<id_entreprise>/reponses_formulaire')
def reponses_formulaire(id_entreprise):
    return flask.render_template("reponses_formulaire.html.jinja2", id_entreprise = id_entreprise)



@app.route('/<id_entreprise>/page_formulaire/formulaire_gouvernance')
def formulaire_gouvernance(id_entreprise):
    return flask.render_template("formulaire_gouvernance.html.jinja2", id_entreprise=id_entreprise)

@app.route('/<id_entreprise>/page_formulaire/add_gouvernance', methods=["POST"])
def add_gouvernance(id_entreprise):

    q1 = int(flask.request.form["q1"])
    q2 = int(flask.request.form["q2"])
    q3 = int(flask.request.form["q3"])
    q4 = int(flask.request.form["q4"])
    q5 = int(flask.request.form["q5"])
    q6 = int(flask.request.form["q6"])


    from database import cursor, cnxn

    insert_query = '''INSERT INTO Formulaire_gouvernance(Id_entreprise, question1, question2, question3, question4, question5, question6)
                        VALUES (?,?,?,?,?,?,?);'''

    values = (id_entreprise, q1, q2, q3, q4, q5, q6)

    cursor.execute(insert_query, values)
    cnxn.commit()

    return flask.redirect(flask.url_for("formulaire_processus_procedures",id_entreprise=id_entreprise))

@app.route('/<id_entreprise>/page_formulaire/formulaire_processus_procedures')
def formulaire_processus_procedures(id_entreprise):
    return flask.render_template("formulaire_processus_procedures.html.jinja2", id_entreprise=id_entreprise)

@app.route('/<id_entreprise>/page_formulaire/add_processus_procedures', methods=["POST"])
def add_processus_procedures(id_entreprise):

    q1 = int(flask.request.form["q1"])
    q2 = int(flask.request.form["q2"])
    q3 = int(flask.request.form["q3"])
    q4 = int(flask.request.form["q4"])
    q5 = int(flask.request.form["q5"])
    q6 = int(flask.request.form["q6"])


    from database import cursor, cnxn

    insert_query = '''INSERT INTO Formulaire_processus_procedures(Id_entreprise, question1, question2, question3, question4, question5, question6)
                        VALUES (?,?,?,?,?,?,?);'''

    values = (id_entreprise, q1, q2, q3, q4, q5, q6)

    cursor.execute(insert_query, values)
    cnxn.commit()

    return flask.redirect(flask.url_for("formulaire_roles_responsabilites",id_entreprise=id_entreprise))

@app.route('/<id_entreprise>/page_formulaire/formulaire_roles_responsabilites')
def formulaire_roles_responsabilites(id_entreprise):
    return flask.render_template("formulaire_roles_responsabilites.html.jinja2", id_entreprise=id_entreprise)

@app.route('/<id_entreprise>/page_formulaire/add_roles_responsabilites', methods=["POST"])
def add_roles_responsabilites(id_entreprise):

    q1 = int(flask.request.form["q1"])
    q2 = int(flask.request.form["q2"])
    q3 = int(flask.request.form["q3"])
    q4 = int(flask.request.form["q4"])
    q5 = int(flask.request.form["q5"])
    q6 = int(flask.request.form["q6"])


    from database import cursor, cnxn


    insert_query = '''INSERT INTO Formulaire_roles_responsabilites(Id_entreprise, question1, question2, question3, question4, question5, question6)
                        VALUES (?,?,?,?,?,?,?);'''

    values = (id_entreprise, q1, q2, q3, q4, q5, q6)

    cursor.execute(insert_query, values)
    cnxn.commit()

    return flask.redirect(flask.url_for("formulaire_outillage", id_entreprise=id_entreprise))

@app.route('/<id_entreprise>/page_formulaire/formulaire_outillage')
def formulaire_outillage(id_entreprise):
    return flask.render_template("formulaire_outillage.html.jinja2", id_entreprise=id_entreprise)

@app.route('/<id_entreprise>/page_formulaire/add_outillage', methods=["POST"])
def add_outillage(id_entreprise):

    q1 = int(flask.request.form["q1"])
    q2 = int(flask.request.form["q2"])
    q3 = int(flask.request.form["q3"])
    q4 = int(flask.request.form["q4"])
    q5 = int(flask.request.form["q5"])
    q6 = int(flask.request.form["q6"])


    from database import cursor, cnxn


    insert_query = '''INSERT INTO Formulaire_outillage(Id_entreprise, question1, question2, question3, question4, question5, question6)
                        VALUES (?,?,?,?,?,?,?);'''
    ajd = date.today()

    values = (id_entreprise, q1, q2, q3, q4, q5, q6)

    cursor.execute(insert_query, values)
    cnxn.commit()

    return flask.redirect(flask.url_for("formulaire_conduite_du_changement", id_entreprise=id_entreprise))

@app.route('/<id_entreprise>/page_formulaire/formulaire_conduite_du_changement')
def formulaire_conduite_du_changement(id_entreprise):
    return flask.render_template("formulaire_conduite_du_changement.html.jinja2", id_entreprise=id_entreprise)

@app.route('/<id_entreprise>/page_formulaire/add_conduite_du_changement', methods=["POST"])
def add_conduite_du_changement(id_entreprise):

    q1 = int(flask.request.form["q1"])
    q2 = int(flask.request.form["q2"])
    q3 = int(flask.request.form["q3"])
    q4 = int(flask.request.form["q4"])
    q5 = int(flask.request.form["q5"])
    q6 = int(flask.request.form["q6"])


    from database import cursor, cnxn


    insert_query = '''INSERT INTO Formulaire_conduite_du_changement(Id_entreprise, question1, question2, question3, question4, question5, question6)
                        VALUES (?,?,?,?,?,?,?);'''

    values = (id_entreprise, q1, q2, q3, q4, q5, q6)

    cursor.execute(insert_query, values)
    cnxn.commit()

    return flask.redirect(flask.url_for("page_formulaire", id_entreprise=id_entreprise))




@app.route('/<id_entreprise>/page_formulaire/formulaire_gestion_systemes')
def formulaire_gestion_systemes(id_entreprise):
    return flask.render_template("formulaire_gestion_systemes.html.jinja2", id_entreprise=id_entreprise)

@app.route('/<id_entreprise>/page_formulaire/add_gestion_systemes', methods=["POST"])
def add_gestion_systemes(id_entreprise):

    q1 = int(flask.request.form["q1"])
    q2 = int(flask.request.form["q2"])
    q3 = int(flask.request.form["q3"])
    q4 = int(flask.request.form["q4"])
    q5 = int(flask.request.form["q5"])
    q6 = int(flask.request.form["q6"])


    from database import cursor, cnxn


    insert_query = '''INSERT INTO Formulaire_gestion_systemes(Id_entreprise, question1, question2, question3, question4, question5, question6)
                        VALUES (?,?,?,?,?,?,?);'''

    values = (id_entreprise, q1, q2, q3, q4, q5, q6)

    cursor.execute(insert_query, values)
    cnxn.commit()

    return flask.redirect(flask.url_for("formulaire_applications", id_entreprise=id_entreprise))

@app.route('/<id_entreprise>/page_formulaire/formulaire_applications')
def formulaire_applications(id_entreprise):
    return flask.render_template("formulaire_applications.html.jinja2", id_entreprise=id_entreprise)

@app.route('/<id_entreprise>/page_formulaire/add_applications', methods=["POST"])
def add_applications(id_entreprise):

    q1 = int(flask.request.form["q1"])
    q2 = int(flask.request.form["q2"])
    q3 = int(flask.request.form["q3"])
    q4 = int(flask.request.form["q4"])
    q5 = int(flask.request.form["q5"])
    q6 = int(flask.request.form["q6"])


    from database import cursor, cnxn


    insert_query = '''INSERT INTO Formulaire_applications(Id_entreprise, question1, question2, question3, question4, question5, question6)
                        VALUES (?,?,?,?,?,?,?);'''

    values = (id_entreprise, q1, q2, q3, q4, q5, q6)

    cursor.execute(insert_query, values)
    cnxn.commit()

    return flask.redirect(flask.url_for("formulaire_securite", id_entreprise=id_entreprise))

@app.route('/<id_entreprise>/page_formulaire/formulaire_securite')
def formulaire_securite(id_entreprise):
    return flask.render_template("formulaire_securite.html.jinja2", id_entreprise=id_entreprise)

@app.route('/<id_entreprise>/page_formulaire/add_securite', methods=["POST"])
def add_securite(id_entreprise):

    q1 = int(flask.request.form["q1"])
    q2 = int(flask.request.form["q2"])
    q3 = int(flask.request.form["q3"])
    q4 = int(flask.request.form["q4"])
    q5 = int(flask.request.form["q5"])
    q6 = int(flask.request.form["q6"])


    from database import cursor, cnxn


    insert_query = '''INSERT INTO Formulaire_securite(Id_entreprise, question1, question2, question3, question4, question5, question6)
                        VALUES (?,?,?,?,?,?,?);'''

    values = (id_entreprise, q1, q2, q3, q4, q5, q6)

    cursor.execute(insert_query, values)
    cnxn.commit()

    return flask.redirect(flask.url_for("formulaire_support", id_entreprise=id_entreprise))

@app.route('/<id_entreprise>/page_formulaire/formulaire_support')
def formulaire_support(id_entreprise):
    return flask.render_template("formulaire_support.html.jinja2", id_entreprise=id_entreprise)

@app.route('/<id_entreprise>/page_formulaire/add_support', methods=["POST"])
def add_support(id_entreprise):

    q1 = int(flask.request.form["q1"])
    q2 = int(flask.request.form["q2"])
    q3 = int(flask.request.form["q3"])
    q4 = int(flask.request.form["q4"])
    q5 = int(flask.request.form["q5"])
    q6 = int(flask.request.form["q6"])


    from database import cursor, cnxn


    insert_query = '''INSERT INTO Formulaire_support(Id_entreprise, question1, question2, question3, question4, question5, question6)
                        VALUES (?,?,?,?,?,?,?);'''

    values = (id_entreprise, q1, q2, q3, q4, q5, q6)

    cursor.execute(insert_query, values)
    cnxn.commit()

    return flask.redirect(flask.url_for("formulaire_outils_collaboratif", id_entreprise=id_entreprise))

@app.route('/<id_entreprise>/page_formulaire/formulaire_outils_collaboratif')
def formulaire_outils_collaboratif(id_entreprise):
    return flask.render_template("formulaire_outils_collaboratif.html.jinja2", id_entreprise=id_entreprise)

@app.route('/<id_entreprise>/page_formulaire/add_outils_collaboratif', methods=["POST"])
def add_outils_collaboratif(id_entreprise):

    q1 = int(flask.request.form["q1"])
    q2 = int(flask.request.form["q2"])
    q3 = int(flask.request.form["q3"])
    q4 = int(flask.request.form["q4"])
    q5 = int(flask.request.form["q5"])
    q6 = int(flask.request.form["q6"])


    from database import cursor, cnxn


    insert_query = '''INSERT INTO Formulaire_outils_collaboratif(Id_entreprise, question1, question2, question3, question4, question5, question6)
                        VALUES (?,?,?,?,?,?,?);'''

    values = (id_entreprise, q1, q2, q3, q4, q5, q6)

    cursor.execute(insert_query, values)
    cnxn.commit()

    return flask.redirect(flask.url_for("page_formulaire", id_entreprise=id_entreprise))




if __name__ == '__main__':
    app.run()
