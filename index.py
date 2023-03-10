import json
import string
from flask import Flask, render_template, request, redirect, url_for
import random
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import uuid

app = Flask(__name__)
app.secret_key = str(uuid.uuid4())

diseases = {
    "A": {"COI": 75, "HC": 80, "Time": 2},
    "B": {"COI": 65, "HC": 65, "Time": 1},
    "C": {"COI": 110, "HC": 60, "Time": 2},
    "D": {"COI": 95, "HC": 70, "Time": 2},
    "E": {"COI": 65, "HC": 50, "Time": 2},
    "F": {"COI": 200, "HC": 220, "Time": 3},
    "G": {"COI": 55, "HC": 20, "Time": 1},
    "H": {"COI": 25, "HC": 10, "Time": 1},
    "I": {"COI": 35, "HC": 40, "Time": 1},
    "J": {"COI": 70, "HC": 30, "Time": 2},
    "K": {"COI": 25, "HC": 25, "Time": 1},
    "L": {"COI": 40, "HC": 25, "Time": 1},
}



class LocalVariables:
     def __init__(self, cev_s1, year_s1, quarter_s1, options_selected_s1, alloted_diseases_s1, checkups_s1, cev_s2, year_s2, quarter_s2, options_selected_s2, alloted_diseases_s2, checkups_s2, deductible, details):
        self.cev_s1 = cev_s1
        self.year_s1 = year_s1
        self.quarter_s1 = quarter_s1
        self.options_selected_s1 = options_selected_s1
        self.alloted_diseases_s1 = alloted_diseases_s1
        self.checkups_s1 = checkups_s1
        self.cev_s2 = cev_s2
        self.year_s2 = year_s2
        self.quarter_s2 = quarter_s2
        self.options_selected_s2 = options_selected_s2
        self.alloted_diseases_s2 = alloted_diseases_s2
        self.checkups_s2 = checkups_s2
        self.deductible = deductible
        self.details = details

  
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        currentUser = LocalVariables(cev_s1 = 10000,year_s1 = 1,quarter_s1 = 1,options_selected_s1 = [],alloted_diseases_s1 = [],checkups_s1 = [],cev_s2 = 10000,year_s2 = 1,quarter_s2 = 1,options_selected_s2 = [],alloted_diseases_s2 = [],checkups_s2 = [],deductible = 75,details = {}) 
        currentUser.details["age"] = request.form["age"]
        currentUser.details["gender"] = request.form["gender"]
        currentUser.details["year"] = request.form["year"]
        currentUser.details["course"] = request.form["course"]
        return redirect(url_for("s1_ins", data=json.dumps(currentUser.__dict__)))
    return render_template("index.html")


@app.route("/s1_ins", methods=["GET", "POST"])
def s1_ins():
    myuuid = request.args['data']
    x = json.loads(myuuid)
    currentUser = LocalVariables(**x)
    if request.method == "POST":
        return redirect(url_for("s1_game", data=json.dumps(currentUser.__dict__)))
    return render_template("s1_ins.html")


@app.route("/s1_game", methods=["GET", "POST"])
def s1_game():
    myuuid = request.args['data']
    x = json.loads(myuuid)
    currentUser = LocalVariables(**x)
    
    random_disease = chr(random.randint(ord("A"), ord("L")))
    currentUser.alloted_diseases_s1.append(random_disease)
    if request.method == "POST":
        currentUser.options_selected_s1.append(request.form["options"])
        currentUser.cev_s1 -= int(request.form["options"])
        currentUser.cev_s1 += 3000

        if currentUser.quarter_s1 == 2:
            currentUser.cev_s1 -= int(request.form["checkup"])
            currentUser.checkups_s1.append(int(request.form["checkup"]))

        if currentUser.quarter_s1 == 4:
            currentUser.year_s1 += 1
            currentUser.quarter_s1 = 1
        else:
            currentUser.quarter_s1 += 1
        
        if currentUser.year_s1 == 4:
            return redirect(url_for("s2_ins", data=json.dumps(currentUser.__dict__)))

        return redirect(url_for("s1_game", data=json.dumps(currentUser.__dict__)))

    return render_template(
        "s1_game.html",
        cev=currentUser.cev_s1,
        year=currentUser.year_s1,
        quarter=currentUser.quarter_s1,
        random_disease=random_disease,
        coi=diseases[random_disease]["COI"],
        coh=diseases[random_disease]["HC"],
        time=diseases[random_disease]["Time"],
    )


@app.route("/s2_ins", methods=["GET", "POST"])
def s2_ins():
    myuuid = request.args['data']
    x = json.loads(myuuid)
    currentUser = LocalVariables(**x)
    if request.method == "POST":
        return redirect(url_for("s2_game", data=json.dumps(currentUser.__dict__)))
    return render_template("s2_ins.html")


@app.route("/s2_game", methods=["GET", "POST"])
def s2_game():
    myuuid = request.args['data']
    x = json.loads(myuuid)
    currentUser = LocalVariables(**x)
    
    random_disease = chr(random.randint(ord("A"), ord("L")))
    currentUser.alloted_diseases_s2.append(random_disease)

    if request.method == "POST":
        currentUser.options_selected_s2.append(request.form["options"])
        os = int(request.form["options"])
        if currentUser.quarter_s2 == 2:
            os += int(request.form["checkup"])
            currentUser.checkups_s2.append(int(request.form["checkup"]))
        if currentUser.deductible >= os:
            currentUser.cev_s2 -= os
            currentUser.deductible -= os
        else:
            currentUser.cev_s2 -= currentUser.deductible
            currentUser.cev_s2 -= 0.2 * (os - currentUser.deductible)
            currentUser.deductible = 0
        currentUser.cev_s2 += 2500

        if currentUser.quarter_s2 == 4:
            currentUser.year_s2 += 1
            currentUser.quarter_s2 = 1
            currentUser.deductible = 75
        else:
            currentUser.quarter_s2 += 1
        if currentUser.year_s2 == 4:
            return redirect(url_for("thank", data=json.dumps(currentUser.__dict__)))
        return redirect(url_for("s2_game", data=json.dumps(currentUser.__dict__)))

    return render_template(
        "s2_game.html",
        cev=currentUser.cev_s2,
        year=currentUser.year_s2,
        quarter=currentUser.quarter_s2,
        random_disease=random_disease,
        coi=diseases[random_disease]["COI"],
        coh=diseases[random_disease]["HC"],
        time=diseases[random_disease]["Time"],
        deductible=currentUser.deductible,
    )


@app.route("/thank", methods=["GET", "POST"])
def thank():
    myuuid = request.args['data']
    x = json.loads(myuuid)
    currentUser = LocalVariables(**x)
    try:
        app = firebase_admin.get_app()
    except ValueError as e:
        cred = credentials.Certificate('moral-hazard-game-firebase-adminsdk-1g1hk-0a4993c229.json')
        firebase_admin.initialize_app(cred)
    db = firestore.client()
    doc_ref = db.collection("tutorial").document(''.join(random.choices(string.ascii_letters, k=15)))
    doc_ref.set({
        "Age": currentUser.details["age"],
                "Gender": currentUser.details["gender"],
                "Year": currentUser.details["year"],
                "Course": currentUser.details["course"],
                "S1 diseases": currentUser.alloted_diseases_s1,
                "S1 options": currentUser.options_selected_s1,
                "S1 checkups": currentUser.checkups_s1,
                "S1 final CEV": currentUser.cev_s1,
                "S2 diseases": currentUser.alloted_diseases_s2,
                "S2 options": currentUser.options_selected_s2,
                "S2 checkups": currentUser.checkups_s2,
                "S2 final CEV": currentUser.cev_s2,
    })
    return render_template("thank.html")
