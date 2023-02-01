from flask import Flask, render_template, request, redirect
import random
from pymongo import MongoClient
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import string
from decouple import config
app = Flask(__name__)


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

cev_s1 = 10000
year_s1 = 1
quarter_s1 = 1
options_selected_s1 = []
alloted_diseases_s1 = []
checkups_s1 = []

cev_s2 = 10000
year_s2 = 1
quarter_s2 = 1
options_selected_s2 = []
alloted_diseases_s2 = []
checkups_s2 = []
deductible = 75
details = {}


@app.route("/", methods=["GET", "POST"])
def home():
    global details
    if request.method == "POST":
        details["age"] = request.form["age"]
        details["gender"] = request.form["gender"]
        details["year"] = request.form["year"]
        details["course"] = request.form["course"]
        print(details)
        return redirect("/s1_ins")
    return render_template("index.html")


@app.route("/s1_ins", methods=["GET", "POST"])
def s1_ins():
    if request.method == "POST":
        return redirect("/s1_game")
    return render_template("s1_ins.html")


@app.route("/s1_game", methods=["GET", "POST"])
def s1_game():
    global cev_s1
    global year_s1
    global quarter_s1
    global options_selected_s1
    global alloted_diseases_s1
    global checkups_s1

    random_disease = chr(random.randint(ord("A"), ord("L")))
    alloted_diseases_s1.append(random_disease)
    if request.method == "POST":
        print(request.form["options"])
        options_selected_s1.append(request.form["options"])
        cev_s1 -= int(request.form["options"])
        cev_s1 += 3000

        if quarter_s1 == 2:
            print(request.form["checkup"])
            cev_s1 -= int(request.form["checkup"])
            checkups_s1.append(int(request.form["checkup"]))

        if quarter_s1 == 4:
            year_s1 += 1
            quarter_s1 = 1
        else:
            quarter_s1 += 1

        if year_s1 == 2:
            return redirect("/s2_ins")

        return redirect("/s1_game")

    return render_template(
        "s1_game.html",
        cev=cev_s1,
        year=year_s1,
        quarter=quarter_s1,
        random_disease=random_disease,
        coi=diseases[random_disease]["COI"],
        coh=diseases[random_disease]["HC"],
        time=diseases[random_disease]["Time"],
    )


@app.route("/s2_ins", methods=["GET", "POST"])
def s2_ins():
    if request.method == "POST":
        return redirect("/s2_game")
    return render_template("s2_ins.html")


@app.route("/s2_game", methods=["GET", "POST"])
def s2_game():
    global cev_s2
    global year_s2
    global quarter_s2
    global options_selected_s2
    global alloted_diseases_s2
    global checkups_s2
    global deductible
    random_disease = chr(random.randint(ord("A"), ord("L")))
    alloted_diseases_s2.append(random_disease)

    if request.method == "POST":
        print(request.form["options"])
        options_selected_s2.append(request.form["options"])
        os = int(request.form["options"])
        if quarter_s2 == 2:
            print(request.form["checkup"])
            os += int(request.form["checkup"])
            checkups_s2.append(int(request.form["checkup"]))
        if deductible >= os:
            cev_s2 -= os
            deductible -= os
        else:
            cev_s2 -= deductible
            cev_s2 -= 0.2 * (os - deductible)
            deductible = 0
        cev_s2 += 2500

        if quarter_s2 == 4:
            year_s2 += 1
            quarter_s2 = 1
            deductible = 75
        else:
            quarter_s2 += 1
    
        if year_s2 == 2:
            return redirect("/thank")
        return redirect("/s2_game")

    return render_template(
        "s2_game.html",
        cev=cev_s2,
        year=year_s2,
        quarter=quarter_s2,
        random_disease=random_disease,
        coi=diseases[random_disease]["COI"],
        coh=diseases[random_disease]["HC"],
        time=diseases[random_disease]["Time"],
        deductible=deductible,
    )


@app.route("/thank", methods=["GET", "POST"])
def thank():
    global details
    cred = credentials.Certificate('moral-hazard-game-firebase-adminsdk-1g1hk-0a4993c229.json')
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    doc_ref = db.collection("tutorial").document(''.join(random.choices(string.ascii_letters, k=15)))
    doc_ref.set({
        "Age": details["age"],
                "Gender": details["gender"],
                "Year": details["year"],
                "Course": details["course"],
                "S1 diseases": [
                    alloted_diseases_s1[i]
                    for i in range(len(alloted_diseases_s1))
                    if i % 2 == 0
                ],
                "S1 options": options_selected_s1,
                "S1 checkups": checkups_s1,
                "S1 final CEV": cev_s1,
                "S2 diseases": [
                    alloted_diseases_s2[i]
                    for i in range(len(alloted_diseases_s2))
                    if i % 2 == 0
                ],
                "S2 options": options_selected_s2,
                "S2 checkups": checkups_s2,
                "S2 final CEV": cev_s2,
    })
    # client = MongoClient(
    #     "mongodb+srv://gopal:gopal%40123@cluster0.2hulrxt.mongodb.net/HDBLookUp?retryWrites=true&w=majority&ssl=true&ssl_cert_reqs=CERT_NONE"
    # )
    # client = MongoClient(config('MONGODB_URI'))
    # db = client["HE3604"]
    # return render_template("thank.html")
    # db["Tut 3"].insert_many(
    #     [
    #         {
    #             "Age": details["age"],
    #             "Gender": details["gender"],
    #             "Year": details["year"],
    #             "Course": details["course"],
    #             "S1 diseases": [
    #                 alloted_diseases_s1[i]
    #                 for i in range(len(alloted_diseases_s1))
    #                 if i % 2 == 0
    #             ],
    #             "S1 options": options_selected_s1,
    #             "S1 checkups": checkups_s1,
    #             "S1 final CEV": cev_s1,
    #             "S2 diseases": [
    #                 alloted_diseases_s2[i]
    #                 for i in range(len(alloted_diseases_s2))
    #                 if i % 2 == 0
    #             ],
    #             "S2 options": options_selected_s2,
    #             "S2 checkups": checkups_s2,
    #             "S2 final CEV": cev_s2,
    #         }
    #     ]
    # )

    return render_template("thank.html", details = details)


# if __name__ == "__main__":
#     app.run(debug=True)