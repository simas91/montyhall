from flask import Flask, render_template, request, session
import secrets
import random
from database import insert, getData

from werkzeug.utils import redirect

app = Flask(__name__)
app.secret_key = secrets.token_urlsafe(16)
app.config["TEMPLATES_AUTO_RELOAD"] = True


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/result", methods=["POST", "GET"])
def again():
    return render_template("play.html")

# starts the game
@app.route("/play", methods=["GET", "POST"])
def play():
    if request.method == "POST" and request.form.get('choice'):

        playerChosenDoors = int(request.form.get('choice'))

        # door number which is available to switch
        switchNumber = 0

        # gets random to put money behind the doors
        rng = random.randint(0, 2)

        allAvailableDoors = [0, 1, 2]
        allAvailableDoors.remove(playerChosenDoors)

        # check which doors to reveal
        if rng == playerChosenDoors:
            tempRng = random.randint(0, 1)
            switchNumber = allAvailableDoors[tempRng] + 1
            del allAvailableDoors[tempRng]
        elif rng == allAvailableDoors[0]:
            switchNumber = allAvailableDoors[0] + 1
            del allAvailableDoors[0]
        else:
            switchNumber = allAvailableDoors[1] + 1
            del allAvailableDoors[1]

        # disables radio button on revealed doors
        number = allAvailableDoors[0]
        button = ["", "", ""]
        button[number] = "disabled"

        # reveals the goat
        list = ["/static/question.png", "/static/question.png", "/static/question.png"]
        list[number] = "/static/goat.jpg"

        # remembers users checked radio button
        checked = ["", "", ""]
        checked[playerChosenDoors] = "checked"

        # saves session data
        session["originalChoice"] = playerChosenDoors
        session["rng"] = rng

        return render_template("playRound2.html", source=list, button=button, checked=checked,
                               chosenNumber=playerChosenDoors+1, switchNumber=switchNumber)

    else:
        return render_template("play.html")

# 2nd stage, reveals one of the doors, final round inserts data into mySQL
@app.route("/playRound2", methods=["POST", "GET"])
def result():
    if request.method == "POST" and request.form.get('choice'):


        playerChosenDoors = int(request.form['choice'])

        # reveals the doors
        list = ["/static/goat.jpg", "/static/goat.jpg", "/static/goat.jpg"]
        list[session.get("rng", None)] = "/static/money.png"


        text = ""
        winText = "Congratulations! You got lucky this time!"
        loseText = "You've LOST! Should have switched when you had a chance!"
        winTextSwitch = "You've won by switching!"
        loseTextSwitch = "sorry, sometimes luck is more important than math!"

        originalChoice = session.get("originalChoice", None)
        luckyNumber = session.get("rng", None)

        switch = True

        # result number to put into mySQL
        dataNumber = 0

        if playerChosenDoors == originalChoice:
            switch = False

        # check the winning number vs chosen number
        if playerChosenDoors == luckyNumber:
            if switch:
                text = winTextSwitch
                dataNumber = 1
            else:
                text = winText
                dataNumber = 2
        else:
            if switch:
                text = loseTextSwitch
                dataNumber = 3
            else:
                text = loseText
                dataNumber = 4

        # inserts result into mySQL
        insert(dataNumber)

        return render_template("result.html", source=list, text=text)

    else:
        return redirect("/play")

# gets results from mySQL
@app.route("/results")
def history():

    # temp data for storing results
    one = 0;
    two = 0;
    three = 0;
    four = 0;

    # temp data for storing percentage
    onePercent = 0;
    twoPercent = 0;
    threePercent = 0;
    fourPercent = 0;

    # gets result number from mySQL
    myresult = getData()

    # gets all result numbers and stores into local var
    for i in myresult:
        result = int(i[0])
        if result == 1:
            one = one + 1
        elif result == 2:
            two = two + 1
        elif result == 3:
            three = three + 1
        elif result == 4:
            four = four + 1

    rows = len(myresult)

    # calculates percentages
    if one != 0:
        onePercent = f"{100 / rows * one:,.2f}"
    if two != 0:
        twoPercent = f"{100 / rows * two:,.2f}"
    if three != 0:
        threePercent = f"{100 / rows * three:,.2f}"
    if four != 0:
        fourPercent = f"{100 / rows * four:,.2f}"

    results = [one, two, three, four]
    percentages = [onePercent, twoPercent, threePercent, fourPercent]
    conditions = ["Won by switching", "Won by not switching", "Lost by switching", "Lost by not switching"]

    return render_template("results.html", conditions=conditions, results=results, percentages=percentages)

# automated test, takes int and switch statement
@app.route("/automate", methods=["POST", "GET"])
def calculate():
    if request.method == "POST" and request.form.get("amount"):

        # stores test outcome
        wonSwitch = 0
        wonNoSwitch = 0
        lostSwitch = 0
        lostNoSwitch = 0

        switch = True
        if request.form.get("switch") == "no":
            switch = False

        usersTestCount = int(request.form.get("amount"))

        # run rng test
        count = 0;
        while count < usersTestCount:
            playerChoice = random.randint(0, 2)
            moneyNumber = random.randint(0, 2)
            count = count + 1
            if playerChoice == moneyNumber:
                if switch:
                    lostSwitch = lostSwitch + 1
                else:
                    wonNoSwitch = wonNoSwitch + 1
            else:
                if switch:
                    wonSwitch = wonSwitch + 1
                else:
                    lostNoSwitch = lostNoSwitch + 1

        # calculate percentage
        onePercent = 0;
        twoPercent = 0;
        threePercent = 0;
        fourPercent = 0;

        percentages = []

        if wonSwitch != 0:
            onePercent = f"{100 / usersTestCount * wonSwitch:,.2f}%"
            percentages.append(onePercent)
        if wonNoSwitch != 0:
            twoPercent = f"{100 / usersTestCount * wonNoSwitch:,.2f}%"
            percentages.append(twoPercent)
        if lostSwitch != 0:
            threePercent = f"{100 / usersTestCount * lostSwitch:,.2f}%"
            percentages.append(threePercent)
        if lostNoSwitch != 0:
            fourPercent = f"{100 / usersTestCount * lostNoSwitch:,.2f}%"
            percentages.append(fourPercent)

        # adds outcome for html
        list = []
        conditions = []

        if switch:
            list.append(wonSwitch)
            list.append(lostSwitch)
            conditions.append("Won by switching")
            conditions.append("Lost by switching")
        else:
            list.append(wonNoSwitch)
            list.append(lostNoSwitch)
            conditions.append("Won by not switching")
            conditions.append("Lost by not switching")

        return render_template("test.html", conditions=conditions, results=list, percentages=percentages)

    else:
        return render_template("automate.html")


if __name__ == '__main__':
    app.run()
