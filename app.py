from flask import Flask, render_template, request
import pyodbc
app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        id_number = request.form['id_number']

        server = "aup-cdsdb.forest.usf.edu"
        user = "akankshakottakota"
        password ="BlueBerry567*"
        database = "CDS" 
        conn = pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';DATABASE='+database+' ;Trusted_Connection=yes'+';UID='+user+';PWD='+ password)
        cursor = conn.cursor()
        cursor.execute("SELECT semester,course,url,valid FROM submission_detail WHERE student_id = ?", id_number)
        rows = cursor.fetchall()
        conn.close()
    
        if not rows:
                message = "No submissions yet"
                return render_template('viewresults.html', message=message)
        else:
            return render_template('viewresults.html', rows=rows)
    else:
        return render_template('checksubmission.html')