import flask
from flask import Flask
from datetime import date


Liste_formulaires_organisation = ["Formulaire_gouvernance","Formulaire_processus_procedures", "Formulaire_roles_responsabilites",
                    "Formulaire_outillage", "Formulaire_conduite_du_changement"]

Liste_formulaires_techniques = ["Formulaire_gestion_systemes", "Formulaire_applications", "Formulaire_securite", "Formulaire_support",
                                "Formulaire_outils_collaboratif"]


app = Flask(__name__)


@app.route('/')
def home():
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

    return flask.redirect(flask.url_for("pourcentage_organisation",id_entreprise=last_id+1))

@app.route('/<id_entreprise>/pourcentage_organisation')
def pourcentage_organisation(id_entreprise):
    from database import cursor,cnxn
    if(cursor.execute('''SELECT * FROM Pourcentage_organisation WHERE Id_entreprise=?''', id_entreprise).fetchone() is None):
        insert_query = '''INSERT INTO Pourcentage_organisation(Id_entreprise) VALUES (?);'''
        cursor.execute(insert_query, id_entreprise)
        cnxn.commit()
    pourcentages = cursor.execute('''SELECT P_gouvernance, P_processus_procedures, P_roles_responsabilites, P_outillage, P_conduite_du_changement FROM Pourcentage_organisation 
    WHERE  Id_entreprise = ?''', id_entreprise).fetchone()

    total = 0
    for k in range(len(pourcentages)):
        total += pourcentages[k]

    return flask.render_template("pourcentage_organisation.html.jinja2", id_entreprise = id_entreprise, pourcentages=pourcentages, total=total)

@app.route('/<id_entreprise>/add_pourcentage_organisation', methods=['POST'])
def add_pourcentage_organisation(id_entreprise):
    from database import cursor, cnxn
    p_gouvernance = flask.request.form["p_gouvernance"]
    p_processus_procedures = flask.request.form["p_processus_procedures"]
    p_roles_responsabilites = flask.request.form["p_roles_responsabilites"]
    p_outillage = flask.request.form["p_outillage"]
    p_conduite_du_changement = flask.request.form["p_conduite_du_changement"]

    cursor.execute('''UPDATE Pourcentage_organisation SET P_gouvernance=?, P_processus_procedures=?, P_roles_responsabilites=?, P_outillage=?, P_conduite_du_changement=?
                WHERE Id_entreprise = ? ''', p_gouvernance, p_processus_procedures,p_roles_responsabilites,p_outillage,p_conduite_du_changement, id_entreprise)
    cnxn.commit()

    return flask.redirect(flask.url_for("pourcentage_technique",id_entreprise=id_entreprise))

@app.route('/<id_entreprise>/pourcentage_technique')
def pourcentage_technique(id_entreprise):
    from database import cursor,cnxn
    if(cursor.execute('''SELECT * FROM Pourcentage_technique WHERE Id_entreprise=?''', id_entreprise).fetchone() is None):
        insert_query = '''INSERT INTO Pourcentage_technique(Id_entreprise) VALUES (?);'''
        cursor.execute(insert_query, id_entreprise)
        cnxn.commit()
    pourcentages = cursor.execute('''SELECT P_gestion_systemes, P_applications, P_securite, P_support, P_outils_collaboratif FROM Pourcentage_technique 
    WHERE  Id_entreprise = ?''', id_entreprise).fetchone()

    total = 0
    for k in range(len(pourcentages)):
        total += pourcentages[k]

    return flask.render_template("pourcentage_technique.html.jinja2", id_entreprise = id_entreprise, pourcentages=pourcentages, total=total)

@app.route('/<id_entreprise>/add_pourcentage_technique', methods=['POST'])
def add_pourcentage_technique(id_entreprise):
    from database import cursor, cnxn
    p_gestion_systemes = flask.request.form["p_gestion_systemes"]
    p_applications = flask.request.form["p_applications"]
    p_securite = flask.request.form["p_securite"]
    p_support = flask.request.form["p_support"]
    p_outils_collaboratif = flask.request.form["p_outils_collaboratif"]

    cursor.execute('''UPDATE Pourcentage_technique SET P_gestion_systemes=?, P_applications=?, P_securite=?, P_support=?, P_outils_collaboratif=?
                WHERE Id_entreprise = ? ''', p_gestion_systemes, p_applications,p_securite,p_support,p_outils_collaboratif, id_entreprise)
    cnxn.commit()

    return flask.redirect(flask.url_for("page_formulaire",id_entreprise=id_entreprise))

@app.route('/<id_entreprise>/page_formulaire')
def page_formulaire(id_entreprise):
    from database import cursor, cnxn

    organisation_existe = cursor.execute('''SELECT Id_entreprise FROM Score_organisation WHERE Id_entreprise = ?''', id_entreprise).fetchone()!=None

    technique_existe = cursor.execute('''SELECT Id_entreprise FROM Score_technique WHERE Id_entreprise = ?''', id_entreprise).fetchone()!=None

    score_total_existe = cursor.execute('''SELECT Id_entreprise FROM Score_total WHERE Id_entreprise = ?''', id_entreprise).fetchone()!=None

    if(organisation_existe and technique_existe):

        score_organisation = cursor.execute('''SELECT Score FROM Score_organisation WHERE Id_entreprise = ?''', id_entreprise).fetchone()[0]
        score_technique = cursor.execute('''SELECT Score FROM Score_technique WHERE Id_entreprise = ?''', id_entreprise).fetchone()[0]
        ajd = date.today()
        score_total = round((score_technique + score_organisation)/2,2)

        if (cursor.execute('''SELECT * FROM Score_total WHERE Id_entreprise = ?''', id_entreprise).fetchone() != None):
            cursor.execute('''UPDATE Score_total SET Score = ? WHERE Id_entreprise = ? ''', score_total, id_entreprise)
            cnxn.commit()
        else:
            insert_query = '''INSERT INTO Score_total(Id_entreprise, Score, Date)
                                            VALUES (?,?,?);'''
            values = (id_entreprise, score_total, str(ajd))
            cursor.execute(insert_query, values)
            cnxn.commit()
        return flask.render_template("page_formulaire.html.jinja2", id_entreprise = id_entreprise, score_technique = score_technique,
                                     score_organisation =score_organisation, score_total = score_total)


    elif(organisation_existe):
        score_organisation = cursor.execute('''SELECT Score FROM Score_organisation WHERE Id_entreprise = ?''', id_entreprise).fetchone()[0]
        return flask.render_template("page_formulaire.html.jinja2", id_entreprise = id_entreprise, score_organisation=score_organisation)

    elif(technique_existe):
        score_technique = cursor.execute('''SELECT Score FROM Score_technique WHERE Id_entreprise = ?''', id_entreprise).fetchone()[0]
        return flask.render_template("page_formulaire.html.jinja2", id_entreprise = id_entreprise, score_technique=score_technique)

    else :
        return flask.render_template("page_formulaire.html.jinja2", id_entreprise=id_entreprise)





#GOUVERNANCE

@app.route('/<id_entreprise>/page_formulaire/formulaire_gouvernance')
def formulaire_gouvernance(id_entreprise):

    from database import cursor, cnxn

    if(cursor.execute('''SELECT * FROM Question_gouvernance WHERE  Id_entreprise = ?''', id_entreprise).fetchone() == None):
        insert_query = '''INSERT INTO Question_gouvernance(Id_entreprise) VALUES (?);'''
        cursor.execute(insert_query, id_entreprise)
        cnxn.commit()

    questions = cursor.execute('''SELECT Question1, Question2, Question3, Question4, Question5, Question6 FROM Question_gouvernance 
    WHERE  Id_entreprise = ?''', id_entreprise).fetchone()

    if(cursor.execute('''SELECT * FROM Formulaire_gouvernance WHERE  Id_entreprise = ?''', id_entreprise).fetchone() != None):
        scores = cursor.execute('''SELECT Score1, Score2, Score3, Score4, Score5, Score6 FROM Formulaire_gouvernance 
        WHERE  Id_entreprise = ?''', id_entreprise).fetchone()
        return flask.render_template("formulaire_gouvernance.html.jinja2", id_entreprise=id_entreprise, scores=scores,
                                     questions=questions)

    return flask.render_template("formulaire_gouvernance.html.jinja2", id_entreprise=id_entreprise, questions = questions)

@app.route('/<id_entreprise>/page_formulaire/add_gouvernance', methods=["POST"])
def add_gouvernance(id_entreprise):

    s1 = int(flask.request.form["s1"])
    s2 = int(flask.request.form["s2"])
    s3 = int(flask.request.form["s3"])
    s4 = int(flask.request.form["s4"])
    s5 = int(flask.request.form["s5"])
    s6 = int(flask.request.form["s6"])

    from database import cursor, cnxn

    if (cursor.execute('''SELECT * FROM Formulaire_gouvernance WHERE  Id_entreprise = ?''', id_entreprise).fetchone() != None):
        cursor.execute('''UPDATE Formulaire_gouvernance SET Score1=?, Score2=?, Score3=?, Score4=?, Score5=?, Score6=?
             WHERE Id_entreprise = ? ''', s1, s2, s3, s4, s5, s6, id_entreprise)
        cnxn.commit()

    else:
        insert_query = '''INSERT INTO Formulaire_gouvernance(Id_entreprise, Score1, Score2, Score3, Score4, Score5, Score6)
                            VALUES (?,?,?,?,?,?,?);'''

        values = (id_entreprise, s1, s2, s3, s4, s5, s6)

        cursor.execute(insert_query, values)
        cnxn.commit()

    return flask.redirect(flask.url_for("formulaire_processus_procedures",id_entreprise=id_entreprise))

@app.route('/<id_entreprise>/page_formulaire/formulaire_gouvernance/modifier_questions_gouvernance', methods=["POST"])
def modifier_questions_gouvernance(id_entreprise):
    from database import cursor, cnxn
    q1 = flask.request.form['q1']
    q2 = flask.request.form['q2']
    q3 = flask.request.form['q3']
    q4 = flask.request.form['q4']
    q5 = flask.request.form['q5']
    q6 = flask.request.form['q6']

    cursor.execute('''UPDATE Question_gouvernance SET Question1=?, Question2=?, Question3=?, Question4=?, Question5=?, Question6=?
     WHERE Id_entreprise = ? ''', q1, q2, q3, q4, q5, q6, id_entreprise)
    cnxn.commit()

    return flask.redirect(flask.url_for("formulaire_gouvernance", id_entreprise=id_entreprise))



#PROCESSUS ET PROCEDURES

@app.route('/<id_entreprise>/page_formulaire/formulaire_processus_procedures')
def formulaire_processus_procedures(id_entreprise):
    from database import cursor, cnxn

    if cursor.execute('''SELECT * FROM Question_processus_procedures WHERE  Id_entreprise = ?''',id_entreprise).fetchone() is None:
        insert_query = '''INSERT INTO Question_processus_procedures(Id_entreprise) VALUES (?);'''
        cursor.execute(insert_query, id_entreprise)
        cnxn.commit()

    questions = cursor.execute('''SELECT Question1, Question2, Question3, Question4, Question5, Question6 FROM Question_processus_procedures 
        WHERE  Id_entreprise = ?''', id_entreprise).fetchone()

    if (cursor.execute('''SELECT * FROM Formulaire_processus_procedures WHERE  Id_entreprise = ?''', id_entreprise).fetchone() != None):
        scores = cursor.execute('''SELECT Score1, Score2, Score3, Score4, Score5, Score6 FROM Formulaire_processus_procedures
            WHERE  Id_entreprise = ?''', id_entreprise).fetchone()
        return flask.render_template("formulaire_processus_procedures.html.jinja2", id_entreprise=id_entreprise, scores=scores,
                                     questions=questions)

    return flask.render_template("formulaire_processus_procedures.html.jinja2", id_entreprise=id_entreprise, questions = questions)

@app.route('/<id_entreprise>/page_formulaire/add_processus_procedures', methods=["POST"])
def add_processus_procedures(id_entreprise):
    s1 = int(flask.request.form["s1"])
    s2 = int(flask.request.form["s2"])
    s3 = int(flask.request.form["s3"])
    s4 = int(flask.request.form["s4"])
    s5 = int(flask.request.form["s5"])
    s6 = int(flask.request.form["s6"])

    from database import cursor, cnxn

    if (cursor.execute('''SELECT * FROM Formulaire_processus_procedures WHERE  Id_entreprise = ?''', id_entreprise).fetchone() != None):
        cursor.execute('''UPDATE Formulaire_processus_procedures SET Score1=?, Score2=?, Score3=?, Score4=?, Score5=?, Score6=?
             WHERE Id_entreprise = ? ''', s1, s2, s3, s4, s5, s6, id_entreprise)
        cnxn.commit()

    else:
        insert_query = '''INSERT INTO Formulaire_processus_procedures(Id_entreprise, Score1, Score2, Score3, Score4, Score5, Score6)
                               VALUES (?,?,?,?,?,?,?);'''

        values = (id_entreprise, s1, s2, s3, s4, s5, s6)

        cursor.execute(insert_query, values)
        cnxn.commit()

    return flask.redirect(flask.url_for("formulaire_roles_responsabilites",id_entreprise=id_entreprise))

@app.route('/<id_entreprise>/page_formulaire/formulaire_processus_procedures/modifier_questions_processus_procedures', methods=["POST"])
def modifier_questions_processus_procedures(id_entreprise):
    from database import cursor, cnxn
    q1 = flask.request.form['q1']
    q2 = flask.request.form['q2']
    q3 = flask.request.form['q3']
    q4 = flask.request.form['q4']
    q5 = flask.request.form['q5']
    q6 = flask.request.form['q6']

    cursor.execute('''UPDATE Question_processus_procedures SET Question1=?, Question2=?, Question3=?, Question4=?, Question5=?, Question6=?
     WHERE Id_entreprise = ? ''', q1, q2, q3, q4, q5, q6, id_entreprise)
    cnxn.commit()

    return flask.redirect(flask.url_for("formulaire_processus_procedures", id_entreprise=id_entreprise))



#ROLES ET RESPONSABILITES

@app.route('/<id_entreprise>/page_formulaire/formulaire_roles_responsabilites')
def formulaire_roles_responsabilites(id_entreprise):
    from database import cursor, cnxn

    if (cursor.execute('''SELECT * FROM Question_roles_responsabilites WHERE  Id_entreprise = ?''',
                       id_entreprise).fetchone() == None):
        insert_query = '''INSERT INTO Question_roles_responsabilites(Id_entreprise) VALUES (?);'''
        cursor.execute(insert_query, id_entreprise)
        cnxn.commit()

    questions = cursor.execute('''SELECT Question1, Question2, Question3, Question4, Question5, Question6 FROM Question_roles_responsabilites 
        WHERE  Id_entreprise = ?''', id_entreprise).fetchone()

    if (cursor.execute('''SELECT * FROM Formulaire_roles_responsabilites WHERE  Id_entreprise = ?''', id_entreprise).fetchone() != None):
        scores = cursor.execute('''SELECT Score1, Score2, Score3, Score4, Score5, Score6 FROM Formulaire_roles_responsabilites
            WHERE  Id_entreprise = ?''', id_entreprise).fetchone()
        return flask.render_template("formulaire_roles_responsabilites.html.jinja2", id_entreprise=id_entreprise, scores=scores,
                                     questions=questions)

    return flask.render_template("formulaire_roles_responsabilites.html.jinja2", id_entreprise=id_entreprise, questions = questions)

@app.route('/<id_entreprise>/page_formulaire/add_roles_responsabilites', methods=["POST"])
def add_roles_responsabilites(id_entreprise):
    s1 = int(flask.request.form["s1"])
    s2 = int(flask.request.form["s2"])
    s3 = int(flask.request.form["s3"])
    s4 = int(flask.request.form["s4"])
    s5 = int(flask.request.form["s5"])
    s6 = int(flask.request.form["s6"])

    from database import cursor, cnxn

    if (cursor.execute('''SELECT * FROM Formulaire_roles_responsabilites WHERE  Id_entreprise = ?''', id_entreprise).fetchone() != None):
        cursor.execute('''UPDATE Formulaire_roles_responsabilites SET Score1=?, Score2=?, Score3=?, Score4=?, Score5=?, Score6=?
             WHERE Id_entreprise = ? ''', s1, s2, s3, s4, s5, s6, id_entreprise)
        cnxn.commit()

    else:
        insert_query = '''INSERT INTO Formulaire_roles_responsabilites(Id_entreprise, Score1, Score2, Score3, Score4, Score5, Score6)
                               VALUES (?,?,?,?,?,?,?);'''

        values = (id_entreprise, s1, s2, s3, s4, s5, s6)

        cursor.execute(insert_query, values)
        cnxn.commit()

    return flask.redirect(flask.url_for("formulaire_outillage", id_entreprise=id_entreprise))

@app.route('/<id_entreprise>/page_formulaire/formulaire_roles_responsabilites/modifier_questions_roles_responsabilites', methods=["POST"])
def modifier_questions_roles_responsabilites(id_entreprise):
    from database import cursor, cnxn
    q1 = flask.request.form['q1']
    q2 = flask.request.form['q2']
    q3 = flask.request.form['q3']
    q4 = flask.request.form['q4']
    q5 = flask.request.form['q5']
    q6 = flask.request.form['q6']

    cursor.execute('''UPDATE Question_roles_responsabilites SET Question1=?, Question2=?, Question3=?, Question4=?, Question5=?, Question6=?
     WHERE Id_entreprise = ? ''', q1, q2, q3, q4, q5, q6, id_entreprise)
    cnxn.commit()

    return flask.redirect(flask.url_for("formulaire_roles_responsabilites", id_entreprise=id_entreprise))



#OUTILLAGE

@app.route('/<id_entreprise>/page_formulaire/formulaire_outillage')
def formulaire_outillage(id_entreprise):
    from database import cursor, cnxn

    if (cursor.execute('''SELECT * FROM Question_outillage WHERE  Id_entreprise = ?''', id_entreprise).fetchone() == None):
        insert_query = '''INSERT INTO Question_outillage(Id_entreprise) VALUES (?);'''
        cursor.execute(insert_query, id_entreprise)
        cnxn.commit()

    questions = cursor.execute('''SELECT Question1, Question2, Question3, Question4, Question5, Question6 FROM Question_outillage
        WHERE  Id_entreprise = ?''', id_entreprise).fetchone()

    if (cursor.execute('''SELECT * FROM Formulaire_outillage WHERE  Id_entreprise = ?''', id_entreprise).fetchone() != None):
        scores = cursor.execute('''SELECT Score1, Score2, Score3, Score4, Score5, Score6 FROM Formulaire_outillage
            WHERE  Id_entreprise = ?''', id_entreprise).fetchone()
        return flask.render_template("formulaire_outillage.html.jinja2", id_entreprise=id_entreprise, scores=scores, questions=questions)

    return flask.render_template("formulaire_outillage.html.jinja2", id_entreprise=id_entreprise, questions = questions)

@app.route('/<id_entreprise>/page_formulaire/add_outillage', methods=["POST"])
def add_outillage(id_entreprise):
    s1 = int(flask.request.form["s1"])
    s2 = int(flask.request.form["s2"])
    s3 = int(flask.request.form["s3"])
    s4 = int(flask.request.form["s4"])
    s5 = int(flask.request.form["s5"])
    s6 = int(flask.request.form["s6"])

    from database import cursor, cnxn

    if (cursor.execute('''SELECT * FROM Formulaire_outillage WHERE  Id_entreprise = ?''', id_entreprise).fetchone() != None):
        cursor.execute('''UPDATE Formulaire_outillage SET Score1=?, Score2=?, Score3=?, Score4=?, Score5=?, Score6=?
             WHERE Id_entreprise = ? ''', s1, s2, s3, s4, s5, s6, id_entreprise)
        cnxn.commit()

    else:
        insert_query = '''INSERT INTO Formulaire_outillage(Id_entreprise, Score1, Score2, Score3, Score4, Score5, Score6)
                               VALUES (?,?,?,?,?,?,?);'''

        values = (id_entreprise, s1, s2, s3, s4, s5, s6)
        cursor.execute(insert_query, values)
        cnxn.commit()

    return flask.redirect(flask.url_for("formulaire_conduite_du_changement", id_entreprise=id_entreprise))

@app.route('/<id_entreprise>/page_formulaire/formulaire_outillage/modifier_questions_outillage', methods=["POST"])
def modifier_questions_outillage(id_entreprise):
    from database import cursor, cnxn
    q1 = flask.request.form['q1']
    q2 = flask.request.form['q2']
    q3 = flask.request.form['q3']
    q4 = flask.request.form['q4']
    q5 = flask.request.form['q5']
    q6 = flask.request.form['q6']

    cursor.execute('''UPDATE Question_outillage SET Question1=?, Question2=?, Question3=?, Question4=?, Question5=?, Question6=?
     WHERE Id_entreprise = ? ''', q1, q2, q3, q4, q5, q6, id_entreprise)
    cnxn.commit()

    return flask.redirect(flask.url_for("formulaire_outillage", id_entreprise=id_entreprise))



#CONDUITE DU CHANGEMENT

@app.route('/<id_entreprise>/page_formulaire/formulaire_conduite_du_changement')
def formulaire_conduite_du_changement(id_entreprise):
    from database import cursor, cnxn

    if (cursor.execute('''SELECT * FROM Question_conduite_du_changement WHERE  Id_entreprise = ?''', id_entreprise).fetchone() == None):
        insert_query = '''INSERT INTO Question_conduite_du_changement(Id_entreprise) VALUES (?);'''
        cursor.execute(insert_query, id_entreprise)
        cnxn.commit()

    questions = cursor.execute('''SELECT Question1, Question2, Question3, Question4, Question5, Question6 FROM Question_conduite_du_changement 
        WHERE  Id_entreprise = ?''', id_entreprise).fetchone()

    if (cursor.execute('''SELECT * FROM Formulaire_conduite_du_changement WHERE  Id_entreprise = ?''', id_entreprise).fetchone() != None):
        scores = cursor.execute('''SELECT Score1, Score2, Score3, Score4, Score5, Score6 FROM Formulaire_conduite_du_changement
            WHERE  Id_entreprise = ?''', id_entreprise).fetchone()
        return flask.render_template("formulaire_conduite_du_changement.html.jinja2", id_entreprise=id_entreprise, scores=scores, questions=questions)

    return flask.render_template("formulaire_conduite_du_changement.html.jinja2", id_entreprise=id_entreprise, questions = questions)

@app.route('/<id_entreprise>/page_formulaire/add_conduite_du_changement', methods=["POST"])
def add_conduite_du_changement(id_entreprise):
    s1 = int(flask.request.form["s1"])
    s2 = int(flask.request.form["s2"])
    s3 = int(flask.request.form["s3"])
    s4 = int(flask.request.form["s4"])
    s5 = int(flask.request.form["s5"])
    s6 = int(flask.request.form["s6"])

    from database import cursor, cnxn

    if (cursor.execute('''SELECT * FROM Formulaire_conduite_du_changement WHERE  Id_entreprise = ?''', id_entreprise).fetchone() != None):
        cursor.execute('''UPDATE Formulaire_conduite_du_changement SET Score1=?, Score2=?, Score3=?, Score4=?, Score5=?, Score6=?
             WHERE Id_entreprise = ? ''', s1, s2, s3, s4, s5, s6, id_entreprise)
        cnxn.commit()

    else:
        insert_query = '''INSERT INTO Formulaire_conduite_du_changement(Id_entreprise, Score1, Score2, Score3, Score4, Score5, Score6)
                               VALUES (?,?,?,?,?,?,?);'''

        values = (id_entreprise, s1, s2, s3, s4, s5, s6)

        cursor.execute(insert_query, values)
        cnxn.commit()

    return flask.redirect(flask.url_for("add_score_organisation", id_entreprise=id_entreprise))

@app.route('/<id_entreprise>/page_formulaire/formulaire_conduite_du_changement/modifier_questions_conduite_du_changement', methods=["POST"])
def modifier_questions_conduite_du_changement(id_entreprise):
    from database import cursor, cnxn
    q1 = flask.request.form['q1']
    q2 = flask.request.form['q2']
    q3 = flask.request.form['q3']
    q4 = flask.request.form['q4']
    q5 = flask.request.form['q5']
    q6 = flask.request.form['q6']

    cursor.execute('''UPDATE Question_conduite_du_changement SET Question1=?, Question2=?, Question3=?, Question4=?, Question5=?, Question6=?
     WHERE Id_entreprise = ? ''', q1, q2, q3, q4, q5, q6, id_entreprise)
    cnxn.commit()

    return flask.redirect(flask.url_for("formulaire_conduite_du_changement", id_entreprise=id_entreprise))



@app.route('/<id_entreprise>/add_score_organisation')
def add_score_organisation(id_entreprise):
    from database import cursor, cnxn

    pourcentages = cursor.execute('''SELECT P_gouvernance, P_processus_procedures, P_roles_responsabilites, P_outillage, P_conduite_du_changement FROM Pourcentage_organisation 
    WHERE  Id_entreprise = ?''', id_entreprise).fetchone()

    score_gouvernance = 0
    for question in cursor.execute('''SELECT Score1, Score2, Score3, Score4, Score5, Score6 FROM Formulaire_gouvernance
            WHERE Id_entreprise = ?''', id_entreprise).fetchone():
        score_gouvernance += question
    score_gouvernance = score_gouvernance * pourcentages[0] / 60

    score_processus_procedures = 0
    for question in cursor.execute('''SELECT Score1, Score2, Score3, Score4, Score5, Score6 FROM Formulaire_processus_procedures
            WHERE Id_entreprise = ?''', id_entreprise).fetchone():
        score_processus_procedures += question
    score_processus_procedures = score_processus_procedures * pourcentages[1] / 60

    score_roles_responsabilites = 0
    for question in cursor.execute('''SELECT Score1, Score2, Score3, Score4, Score5, Score6 FROM Formulaire_roles_responsabilites
            WHERE Id_entreprise = ?''', id_entreprise).fetchone():
        score_roles_responsabilites += question
    score_roles_responsabilites = score_roles_responsabilites * pourcentages[2] / 60

    score_outillage = 0
    for question in cursor.execute('''SELECT Score1, Score2, Score3, Score4, Score5, Score6 FROM Formulaire_outillage
                    WHERE Id_entreprise = ?''', id_entreprise).fetchone():
        score_outillage += question
    score_outillage = score_outillage * pourcentages[3] / 60

    score_conduite_du_changement = 0
    for question in cursor.execute('''SELECT Score1, Score2, Score3, Score4, Score5, Score6 FROM Formulaire_conduite_du_changement
                    WHERE Id_entreprise = ?''', id_entreprise).fetchone():
        score_conduite_du_changement += question
    score_conduite_du_changement = score_conduite_du_changement * pourcentages[4] / 60

    score_organisation = round(
        score_conduite_du_changement + score_outillage + score_roles_responsabilites + score_gouvernance + score_processus_procedures,
        2)

    if(cursor.execute('''SELECT * FROM Score_organisation WHERE Id_entreprise = ?''', id_entreprise).fetchone() != None):
        cursor.execute('''UPDATE Score_organisation SET Score = ? WHERE Id_entreprise = ? ''', score_organisation, id_entreprise)
        cnxn.commit()

    else:
        insert_query_organisation = '''INSERT INTO Score_organisation(Id_entreprise, Score)
                                                VALUES (?,?);'''

        values_organisation = (id_entreprise, score_organisation)

        cursor.execute(insert_query_organisation, values_organisation)
        cnxn.commit()

    return flask.redirect(flask.url_for("page_formulaire",id_entreprise = id_entreprise))



#GESTIONS DES SYSTEMES

@app.route('/<id_entreprise>/page_formulaire/formulaire_gestion_systemes')
def formulaire_gestion_systemes(id_entreprise):
    from database import cursor, cnxn

    if (cursor.execute('''SELECT * FROM Question_gestion_systemes WHERE  Id_entreprise = ?''', id_entreprise).fetchone() == None):
        insert_query = '''INSERT INTO Question_gestion_systemes(Id_entreprise) VALUES (?);'''
        cursor.execute(insert_query, id_entreprise)
        cnxn.commit()

    questions = cursor.execute('''SELECT Question1, Question2, Question3, Question4, Question5, Question6 FROM Question_gestion_systemes
        WHERE  Id_entreprise = ?''', id_entreprise).fetchone()

    if (cursor.execute('''SELECT * FROM Formulaire_gestion_systemes WHERE  Id_entreprise = ?''', id_entreprise).fetchone() != None):
        scores = cursor.execute('''SELECT Score1, Score2, Score3, Score4, Score5, Score6 FROM Formulaire_gestion_systemes 
            WHERE  Id_entreprise = ?''', id_entreprise).fetchone()
        return flask.render_template("formulaire_gestion_systemes.html.jinja2", id_entreprise=id_entreprise, scores=scores, questions=questions)

    return flask.render_template("formulaire_gestion_systemes.html.jinja2", id_entreprise=id_entreprise, questions = questions)

@app.route('/<id_entreprise>/page_formulaire/add_gestion_systemes', methods=["POST"])
def add_gestion_systemes(id_entreprise):
    s1 = int(flask.request.form["s1"])
    s2 = int(flask.request.form["s2"])
    s3 = int(flask.request.form["s3"])
    s4 = int(flask.request.form["s4"])
    s5 = int(flask.request.form["s5"])
    s6 = int(flask.request.form["s6"])

    from database import cursor, cnxn

    if (cursor.execute('''SELECT * FROM Formulaire_gestion_systemes WHERE  Id_entreprise = ?''', id_entreprise).fetchone() != None):
        cursor.execute('''UPDATE Formulaire_gestion_systemes SET Score1=?, Score2=?, Score3=?, Score4=?, Score5=?, Score6=?
             WHERE Id_entreprise = ? ''', s1, s2, s3, s4, s5, s6, id_entreprise)
        cnxn.commit()

    else:
        insert_query = '''INSERT INTO Formulaire_gestion_systemes(Id_entreprise, Score1, Score2, Score3, Score4, Score5, Score6)
                                  VALUES (?,?,?,?,?,?,?);'''

        values = (id_entreprise, s1, s2, s3, s4, s5, s6)

        cursor.execute(insert_query, values)
        cnxn.commit()

    return flask.redirect(flask.url_for("formulaire_applications", id_entreprise=id_entreprise))

@app.route('/<id_entreprise>/page_formulaire/formulaire_gestion_systemes/modifier_questions_gestion_systemes', methods=["POST"])
def modifier_questions_gestion_systemes(id_entreprise):
    from database import cursor, cnxn
    q1 = flask.request.form['q1']
    q2 = flask.request.form['q2']
    q3 = flask.request.form['q3']
    q4 = flask.request.form['q4']
    q5 = flask.request.form['q5']
    q6 = flask.request.form['q6']

    cursor.execute('''UPDATE Question_gestion_systemes SET Question1=?, Question2=?, Question3=?, Question4=?, Question5=?, Question6=?
     WHERE Id_entreprise = ? ''', q1, q2, q3, q4, q5, q6, id_entreprise)
    cnxn.commit()

    return flask.redirect(flask.url_for("formulaire_gestion_systemes", id_entreprise=id_entreprise))



#APPLICATIONS

@app.route('/<id_entreprise>/page_formulaire/formulaire_applications')
def formulaire_applications(id_entreprise):
    from database import cursor, cnxn

    if (cursor.execute('''SELECT * FROM Question_applications WHERE  Id_entreprise = ?''', id_entreprise).fetchone() == None):
        insert_query = '''INSERT INTO Question_applications(Id_entreprise) VALUES (?);'''
        cursor.execute(insert_query, id_entreprise)
        cnxn.commit()

    questions = cursor.execute('''SELECT Question1, Question2, Question3, Question4, Question5, Question6 FROM Question_applications 
        WHERE  Id_entreprise = ?''', id_entreprise).fetchone()

    if (cursor.execute('''SELECT * FROM Formulaire_applications WHERE  Id_entreprise = ?''', id_entreprise).fetchone() != None):
        scores = cursor.execute('''SELECT Score1, Score2, Score3, Score4, Score5, Score6 FROM Formulaire_applications 
            WHERE  Id_entreprise = ?''', id_entreprise).fetchone()
        return flask.render_template("formulaire_applications.html.jinja2", id_entreprise=id_entreprise, scores=scores, questions=questions)

    return flask.render_template("formulaire_applications.html.jinja2", id_entreprise=id_entreprise, questions = questions)

@app.route('/<id_entreprise>/page_formulaire/add_applications', methods=["POST"])
def add_applications(id_entreprise):
    s1 = int(flask.request.form["s1"])
    s2 = int(flask.request.form["s2"])
    s3 = int(flask.request.form["s3"])
    s4 = int(flask.request.form["s4"])
    s5 = int(flask.request.form["s5"])
    s6 = int(flask.request.form["s6"])

    from database import cursor, cnxn

    if (cursor.execute('''SELECT * FROM Formulaire_applications WHERE  Id_entreprise = ?''', id_entreprise).fetchone() != None):
        cursor.execute('''UPDATE Formulaire_applications SET Score1=?, Score2=?, Score3=?, Score4=?, Score5=?, Score6=?
             WHERE Id_entreprise = ? ''', s1, s2, s3, s4, s5, s6, id_entreprise)
        cnxn.commit()

    else:
        insert_query = '''INSERT INTO Formulaire_applications(Id_entreprise, Score1, Score2, Score3, Score4, Score5, Score6)
                                  VALUES (?,?,?,?,?,?,?);'''

        values = (id_entreprise, s1, s2, s3, s4, s5, s6)

        cursor.execute(insert_query, values)
        cnxn.commit()

    return flask.redirect(flask.url_for("formulaire_securite", id_entreprise=id_entreprise))

@app.route('/<id_entreprise>/page_formulaire/formulaire_applications/modifier_questions_applications', methods=["POST"])
def modifier_questions_applications(id_entreprise):
    from database import cursor, cnxn
    q1 = flask.request.form['q1']
    q2 = flask.request.form['q2']
    q3 = flask.request.form['q3']
    q4 = flask.request.form['q4']
    q5 = flask.request.form['q5']
    q6 = flask.request.form['q6']

    cursor.execute('''UPDATE Question_applications SET Question1=?, Question2=?, Question3=?, Question4=?, Question5=?, Question6=?
     WHERE Id_entreprise = ? ''', q1, q2, q3, q4, q5, q6, id_entreprise)
    cnxn.commit()

    return flask.redirect(flask.url_for("formulaire_applications", id_entreprise=id_entreprise))



#SECURITE

@app.route('/<id_entreprise>/page_formulaire/formulaire_securite')
def formulaire_securite(id_entreprise):
    from database import cursor, cnxn

    if (cursor.execute('''SELECT * FROM Question_securite WHERE  Id_entreprise = ?''', id_entreprise).fetchone() == None):
        insert_query = '''INSERT INTO Question_securite(Id_entreprise) VALUES (?);'''
        cursor.execute(insert_query, id_entreprise)
        cnxn.commit()

    questions = cursor.execute('''SELECT Question1, Question2, Question3, Question4, Question5, Question6 FROM Question_securite 
        WHERE  Id_entreprise = ?''', id_entreprise).fetchone()

    if (cursor.execute('''SELECT * FROM Formulaire_securite WHERE  Id_entreprise = ?''', id_entreprise).fetchone() != None):
        scores = cursor.execute('''SELECT Score1, Score2, Score3, Score4, Score5, Score6 FROM Formulaire_securite 
            WHERE  Id_entreprise = ?''', id_entreprise).fetchone()
        return flask.render_template("formulaire_securite.html.jinja2", id_entreprise=id_entreprise, scores=scores, questions=questions)

    return flask.render_template("formulaire_securite.html.jinja2", id_entreprise=id_entreprise, questions=questions)

@app.route('/<id_entreprise>/page_formulaire/add_securite', methods=["POST"])
def add_securite(id_entreprise):
    s1 = int(flask.request.form["s1"])
    s2 = int(flask.request.form["s2"])
    s3 = int(flask.request.form["s3"])
    s4 = int(flask.request.form["s4"])
    s5 = int(flask.request.form["s5"])
    s6 = int(flask.request.form["s6"])

    from database import cursor, cnxn

    if (cursor.execute('''SELECT * FROM Formulaire_securite WHERE  Id_entreprise = ?''', id_entreprise).fetchone() != None):
        cursor.execute('''UPDATE Formulaire_securite SET Score1=?, Score2=?, Score3=?, Score4=?, Score5=?, Score6=?
             WHERE Id_entreprise = ? ''', s1, s2, s3, s4, s5, s6, id_entreprise)
        cnxn.commit()

    else:
        insert_query = '''INSERT INTO Formulaire_securite(Id_entreprise, Score1, Score2, Score3, Score4, Score5, Score6)
                                  VALUES (?,?,?,?,?,?,?);'''

        values = (id_entreprise, s1, s2, s3, s4, s5, s6)
        cursor.execute(insert_query, values)
        cnxn.commit()

    return flask.redirect(flask.url_for("formulaire_support", id_entreprise=id_entreprise))

@app.route('/<id_entreprise>/page_formulaire/formulaire_securite/modifier_questions_securite', methods=["POST"])
def modifier_questions_securite(id_entreprise):
    from database import cursor, cnxn
    q1 = flask.request.form['q1']
    q2 = flask.request.form['q2']
    q3 = flask.request.form['q3']
    q4 = flask.request.form['q4']
    q5 = flask.request.form['q5']
    q6 = flask.request.form['q6']

    cursor.execute('''UPDATE Question_securite SET Question1=?, Question2=?, Question3=?, Question4=?, Question5=?, Question6=?
     WHERE Id_entreprise = ? ''', q1, q2, q3, q4, q5, q6, id_entreprise)
    cnxn.commit()

    return flask.redirect(flask.url_for("formulaire_securite", id_entreprise=id_entreprise))



#SUPPORT

@app.route('/<id_entreprise>/page_formulaire/formulaire_support')
def formulaire_support(id_entreprise):
    from database import cursor, cnxn

    if (cursor.execute('''SELECT * FROM Question_support WHERE  Id_entreprise = ?''', id_entreprise).fetchone() == None):
        insert_query = '''INSERT INTO Question_support(Id_entreprise) VALUES (?);'''
        cursor.execute(insert_query, id_entreprise)
        cnxn.commit()

    questions = cursor.execute('''SELECT Question1, Question2, Question3, Question4, Question5, Question6 FROM Question_support 
        WHERE  Id_entreprise = ?''', id_entreprise).fetchone()

    if (cursor.execute('''SELECT * FROM Formulaire_support WHERE  Id_entreprise = ?''', id_entreprise).fetchone() != None):
        scores = cursor.execute('''SELECT Score1, Score2, Score3, Score4, Score5, Score6 FROM Formulaire_support
            WHERE  Id_entreprise = ?''', id_entreprise).fetchone()
        return flask.render_template("formulaire_support.html.jinja2", id_entreprise=id_entreprise, scores=scores, questions=questions)

    return flask.render_template("formulaire_support.html.jinja2", id_entreprise=id_entreprise, questions=questions)

@app.route('/<id_entreprise>/page_formulaire/add_support', methods=["POST"])
def add_support(id_entreprise):
    s1 = int(flask.request.form["s1"])
    s2 = int(flask.request.form["s2"])
    s3 = int(flask.request.form["s3"])
    s4 = int(flask.request.form["s4"])
    s5 = int(flask.request.form["s5"])
    s6 = int(flask.request.form["s6"])

    from database import cursor, cnxn

    if (cursor.execute('''SELECT * FROM Formulaire_support WHERE  Id_entreprise = ?''', id_entreprise).fetchone() != None):
        cursor.execute('''UPDATE Formulaire_support SET Score1=?, Score2=?, Score3=?, Score4=?, Score5=?, Score6=?
             WHERE Id_entreprise = ? ''', s1, s2, s3, s4, s5, s6, id_entreprise)
        cnxn.commit()

    else:
        insert_query = '''INSERT INTO Formulaire_support(Id_entreprise, Score1, Score2, Score3, Score4, Score5, Score6)
                                  VALUES (?,?,?,?,?,?,?);'''

        values = (id_entreprise, s1, s2, s3, s4, s5, s6)

        cursor.execute(insert_query, values)
        cnxn.commit()

    return flask.redirect(flask.url_for("formulaire_outils_collaboratif", id_entreprise=id_entreprise))

@app.route('/<id_entreprise>/page_formulaire/formulaire_support/modifier_questions_support', methods=["POST"])
def modifier_questions_support(id_entreprise):
    from database import cursor, cnxn
    q1 = flask.request.form['q1']
    q2 = flask.request.form['q2']
    q3 = flask.request.form['q3']
    q4 = flask.request.form['q4']
    q5 = flask.request.form['q5']
    q6 = flask.request.form['q6']

    cursor.execute('''UPDATE Question_support SET Question1=?, Question2=?, Question3=?, Question4=?, Question5=?, Question6=?
     WHERE Id_entreprise = ? ''', q1, q2, q3, q4, q5, q6, id_entreprise)
    cnxn.commit()

    return flask.redirect(flask.url_for("formulaire_support", id_entreprise=id_entreprise))



#OUTILS COLLABORATIF

@app.route('/<id_entreprise>/page_formulaire/formulaire_outils_collaboratif')
def formulaire_outils_collaboratif(id_entreprise):
    from database import cursor, cnxn

    if (cursor.execute('''SELECT * FROM Question_outils_collaboratif WHERE  Id_entreprise = ?''', id_entreprise).fetchone() == None):
        insert_query = '''INSERT INTO Question_outils_collaboratif(Id_entreprise) VALUES (?);'''
        cursor.execute(insert_query, id_entreprise)
        cnxn.commit()

    questions = cursor.execute('''SELECT Question1, Question2, Question3, Question4, Question5, Question6 FROM Question_outils_collaboratif 
        WHERE  Id_entreprise = ?''', id_entreprise).fetchone()

    if (cursor.execute('''SELECT * FROM Formulaire_outils_collaboratif WHERE  Id_entreprise = ?''', id_entreprise).fetchone() != None):
        scores = cursor.execute('''SELECT Score1, Score2, Score3, Score4, Score5, Score6 FROM Formulaire_outils_collaboratif 
            WHERE  Id_entreprise = ?''', id_entreprise).fetchone()
        return flask.render_template("formulaire_outils_collaboratif.html.jinja2", id_entreprise=id_entreprise, scores=scores, questions=questions)

    return flask.render_template("formulaire_outils_collaboratif.html.jinja2", id_entreprise=id_entreprise, questions=questions)

@app.route('/<id_entreprise>/page_formulaire/add_outils_collaboratif', methods=["POST"])
def add_outils_collaboratif(id_entreprise):
    s1 = int(flask.request.form["s1"])
    s2 = int(flask.request.form["s2"])
    s3 = int(flask.request.form["s3"])
    s4 = int(flask.request.form["s4"])
    s5 = int(flask.request.form["s5"])
    s6 = int(flask.request.form["s6"])

    from database import cursor, cnxn

    if (cursor.execute('''SELECT * FROM Formulaire_outils_collaboratif WHERE  Id_entreprise = ?''', id_entreprise).fetchone() != None):
        cursor.execute('''UPDATE Formulaire_outils_collaboratif SET Score1=?, Score2=?, Score3=?, Score4=?, Score5=?, Score6=?
             WHERE Id_entreprise = ? ''', s1, s2, s3, s4, s5, s6, id_entreprise)
        cnxn.commit()

    else:
        insert_query = '''INSERT INTO Formulaire_outils_collaboratif(Id_entreprise, Score1, Score2, Score3, Score4, Score5, Score6)
                              VALUES (?,?,?,?,?,?,?);'''

        values = (id_entreprise, s1, s2, s3, s4, s5, s6)

        cursor.execute(insert_query, values)
        cnxn.commit()

    return flask.redirect(flask.url_for("add_score_technique", id_entreprise=id_entreprise))

@app.route('/<id_entreprise>/page_formulaire/formulaire_outils_collaboratif/modifier_questions_outils_collaboratif', methods=["POST"])
def modifier_questions_outils_collaboratif(id_entreprise):
    from database import cursor, cnxn
    q1 = flask.request.form['q1']
    q2 = flask.request.form['q2']
    q3 = flask.request.form['q3']
    q4 = flask.request.form['q4']
    q5 = flask.request.form['q5']
    q6 = flask.request.form['q6']

    cursor.execute('''UPDATE Question_outils_collaboratif SET Question1=?, Question2=?, Question3=?, Question4=?, Question5=?, Question6=?
     WHERE Id_entreprise = ? ''', q1, q2, q3, q4, q5, q6, id_entreprise)
    cnxn.commit()

    return flask.redirect(flask.url_for("formulaire_outils_collaboratif", id_entreprise=id_entreprise))


@app.route('/<id_entreprise>/add_score_technique')
def add_score_technique(id_entreprise):
    from database import cursor, cnxn

    pourcentages = cursor.execute('''SELECT P_gestion_systemes, P_applications, P_securite, P_support, P_outils_collaboratif FROM Pourcentage_technique 
       WHERE  Id_entreprise = ?''', id_entreprise).fetchone()

    score_gestion_systemes = 0
    for question in cursor.execute('''SELECT Score1, Score2, Score3, Score4, Score5, Score6 FROM Formulaire_gestion_systemes
                   WHERE Id_entreprise = ?''', id_entreprise).fetchone():
        score_gestion_systemes += question
    score_gestion_systemes = score_gestion_systemes * pourcentages[0] / 60

    score_applications = 0
    for question in cursor.execute('''SELECT Score1, Score2, Score3, Score4, Score5, Score6 FROM Formulaire_applications
                   WHERE Id_entreprise = ?''', id_entreprise).fetchone():
        score_applications += question
    score_applications = score_applications * pourcentages[1] / 60

    score_securite = 0
    for question in cursor.execute('''SELECT Score1, Score2, Score3, Score4, Score5, Score6 FROM Formulaire_securite
                   WHERE Id_entreprise = ?''', id_entreprise).fetchone():
        score_securite += question
    score_securite = score_securite * pourcentages[2] / 60

    score_support = 0
    for question in cursor.execute('''SELECT Score1, Score2, Score3, Score4, Score5, Score6 FROM Formulaire_support
                           WHERE Id_entreprise = ?''', id_entreprise).fetchone():
        score_support += question
    score_support = score_support * pourcentages[3] / 60

    score_outils_collaboratif = 0
    for question in cursor.execute('''SELECT Score1, Score2, Score3, Score4, Score5, Score6 FROM Formulaire_outils_collaboratif
                           WHERE Id_entreprise = ?''', id_entreprise).fetchone():
        score_outils_collaboratif += question
    score_outils_collaboratif = score_outils_collaboratif * pourcentages[4] / 60

    score_technique = round(
        score_gestion_systemes + score_applications + score_securite + score_support + score_outils_collaboratif, 2)

    if (cursor.execute('''SELECT * FROM Score_technique WHERE Id_entreprise = ?''', id_entreprise).fetchone() != None):
        cursor.execute('''UPDATE Score_technique SET Score = ? WHERE Id_entreprise = ? ''', score_technique, id_entreprise)
        cnxn.commit()

    else:
        insert_query_technique = '''INSERT INTO Score_technique(Id_entreprise, Score)
                                                       VALUES (?,?);'''

        values_technique = (id_entreprise, score_technique)

        cursor.execute(insert_query_technique, values_technique)
        cnxn.commit()

    return flask.redirect(flask.url_for("page_formulaire", id_entreprise=id_entreprise))



@app.route('/<id_entreprise>/delete_formulaire')
def delete_formulaire(id_entreprise):
    from database import cursor, cnxn

    entrepris = 'Entreprise'

    str = 'delete from '+ entrepris+' where ID = ? '

    cursor.execute(''+str+'', id_entreprise)
    cnxn.commit()

    return flask.redirect(flask.url_for("comparaison", id_entreprise = id_entreprise))

@app.route('/formulaires_non_finis')
def formulaires_non_finis():

    L = []
    l=[]
    from database import cursor

    for row in cursor.execute('''SELECT ID, Nom FROM Entreprise'''):
        l += [row]

    for row in l :
        if cursor.execute('''SELECT Id_entreprise FROM Formulaire_gouvernance where Id_entreprise = ?''', row[0]).fetchone() == None \
                and cursor.execute('''SELECT Id_entreprise FROM Formulaire_gestion_systemes where Id_entreprise = ?''', row[0]).fetchone() == None:

            L+=[[row[0], row[1], 'page_formulaire']]

        # ORGANISATION COMMENCEE MAIS PAS FINIE

        elif (cursor.execute('''SELECT Id_entreprise FROM Score_organisation where Id_entreprise = ?''', row[0]).fetchone() == None
                and cursor.execute('''SELECT Id_entreprise FROM Formulaire_gestion_systemes where Id_entreprise = ?''', row[0]).fetchone() == None):
            i = 0
            str = 'SELECT Id_entreprise From '+ 'Formulaire_gouvernance' + ' WHERE Id_entreprise = ?'

            while i<len(Liste_formulaires_organisation) and cursor.execute(''+str+'', row[0]).fetchone() != None:
                i+=1
                str = 'SELECT Id_entreprise From '+ Liste_formulaires_organisation[i] + ' WHERE Id_entreprise = ?'

            L += [[row[0], row[1], Liste_formulaires_organisation[i]]]


        elif (cursor.execute('''SELECT Id_entreprise FROM Score_organisation where Id_entreprise = ?''', row[0]).fetchone() == None
              and cursor.execute('''SELECT Id_entreprise FROM Score_technique where Id_entreprise = ?''', row[0]).fetchone() != None):
            i = 0
            str = 'SELECT Id_entreprise From ' + 'Formulaire_gouvernance' + ' WHERE Id_entreprise = ?'

            while i < len(Liste_formulaires_organisation) and cursor.execute('' + str + '', row[0]).fetchone() != None:
                i += 1
                str = 'SELECT Id_entreprise From ' + Liste_formulaires_organisation[i] + ' WHERE Id_entreprise = ?'

            L += [[row[0], row[1], Liste_formulaires_organisation[i]]]

        # TECHNIQUE COMMENCEE MAIS PAS FINIE

        elif cursor.execute('''SELECT Id_entreprise FROM Score_technique where Id_entreprise = ?''', row[0]).fetchone() == None \
                and cursor.execute('''SELECT Id_entreprise FROM Formulaire_gouvernance where Id_entreprise = ?''', row[0]).fetchone() == None:
            i = 0
            str = 'SELECT Id_entreprise From '+ 'Formulaire_gestion_systemes' + ' WHERE Id_entreprise = ?'
            while i<len(Liste_formulaires_techniques) and cursor.execute(''+str+'', row[0]).fetchone() != None:
                i+=1
                str = 'SELECT Id_entreprise From '+ Liste_formulaires_techniques[i] + ' WHERE Id_entreprise = ?'
            L += [[row[0], row[1], Liste_formulaires_techniques[i]]]

        elif cursor.execute('''SELECT Id_entreprise FROM Score_technique where Id_entreprise = ?''', row[0]).fetchone() == None \
                and cursor.execute('''SELECT Id_entreprise FROM Score_organisation where Id_entreprise = ?''', row[0]).fetchone() != None:
            i = 0
            str = 'SELECT Id_entreprise From '+ 'Formulaire_gestion_systemes' + ' WHERE Id_entreprise = ?'
            while i<len(Liste_formulaires_techniques) and cursor.execute(''+str+'', row[0]).fetchone() != None:
                i+=1
                str = 'SELECT Id_entreprise From '+ Liste_formulaires_techniques[i] + ' WHERE Id_entreprise = ?'
            L += [[row[0], row[1], Liste_formulaires_techniques[i]]]


    return flask.render_template("formulaires_non_finis.html.jinja2", L = L)

@app.route('/comparaison')
def comparaison():
    from database import cursor
    entreprise_liste = []
    for row in cursor.execute('''SELECT ID, Nom, Score_organisation.Score, Score_technique.Score, Score_total.Score, Date
        FROM Entreprise,Score_organisation, Score_technique, Score_total
        WHERE Score_organisation.Id_entreprise = Entreprise.ID AND Score_technique.Id_entreprise = Entreprise.ID AND Score_total.Id_entreprise = Entreprise.ID
        ORDER BY ID'''):
        entreprise_liste += [[row[0], row[1], row[2], row[3], row[4], row[5]]]

    if (entreprise_liste != [[]]):
        return flask.render_template("comparaison.html.jinja2", entreprise_liste=entreprise_liste)
    else:
        return flask.render_template("comparaison.html.jinja2")

@app.route('/<id_entreprise>/reponses_formulaire')
def reponses_formulaire(id_entreprise):
    return flask.render_template("reponses_formulaire.html.jinja2", id_entreprise = id_entreprise)




if __name__ == '__main__':
    app.run(debug=True)
