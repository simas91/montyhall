import mysql.connector


def insert(value):
    mydb = mysql.connector.connect(
        host="localhost",
        user="simas",
        passwd="witby",
        database="results"
    )
    mycursor = mydb.cursor()

    sql = "INSERT INTO history VALUES (%s)"
    mycursor.execute(sql, (value,))

    mydb.commit()
    mydb.close()
    return


def getData():
    mydb = mysql.connector.connect(
        host="localhost",
        user="simas",
        passwd="witby",
        database="results"
    )
    mycursor = mydb.cursor()

    mycursor.execute("SELECT * FROM history")

    myresult = mycursor.fetchall()
    mydb.close()

    return myresult
