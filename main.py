from flask import Flask, render_template, session, redirect, url_for, request, send_file
from mongohelper import checkLogin, doRegister,usernameExists
import PyPDF2
import random

app = Flask(__name__)
app.secret_key = "mykey1234"
@app.route('/')
def hello():
    if 'username' in session:
        username = session['username']
        print("logged in as ", username)
        return redirect(url_for("dashboard"))
    return render_template("index.html")

@app.route('/team/')
def team():
    return render_template("team.html")

@app.route('/login/', methods=["GET", "POST"])
def login():
    error=''
    if 'username' in session:
        return redirect(url_for("dashboard"))
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']
        results = checkLogin(u, p)
        if(results):
            session['username'] = u
            return redirect(url_for("dashboard"))
        else:
            error = "Invalid username or password"
    return render_template("login.html", error=error)

@app.route("/register/", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        n = request.form["name"]
        u = request.form["username"]
        e = request.form["email"]
        p = request.form["password"]
        if(len(n) == 0 or len(u) == 0 or len(e) == 0 or len(p) == 0):
            return render_template("register.html", error="No field should be empty")
        elif((not e[0] >= "A" and not e[1] <= "Z") or (not e[0] >= "a" and not e[1] <= "z")):
            return render_template("register.html", error="email should start with a letter")
        elif("gmail" not in e and "yahoo" not in e and "outlook" not in e):
            return render_template("register.html", error="You should have a gmail, yahoo or outlook account")
        elif(len(p) < 6 or len(p) > 18):
            return render_template("register.html", error="password must be 6-18 characters long")
        elif(u[0] >= '1' and u[0] <= '9'):
            return render_template("register.html", error="username should start with and _ or a-z or A-Z")
        elif(usernameExists(u)):
            return render_template("register.html", error="username already exists")
        session["username"] = u
        doRegister(n, u, e ,p)
        return redirect(url_for("dashboard"))
    return render_template("register.html")
@app.route('/about/')
def about():
    return render_template("about.html")

@app.route('/pdfupload/', methods = ['POST', 'GET'])
def pdfupload():
    if request.method == 'POST':
        f = request.files['file']
        filename = "/"+f.filename
        if f:
            pdfreader = PyPDF2.PdfFileReader(f)
            contents = ""
            for i in range(int(pdfreader.numPages)):
                contents += str(pdfreader.getPage(i).extractText())
            print(contents)
            return render_template("editpdf.html", filecontents = contents)
        else:
            return 'file not provided'

@app.route('/pdfuploadformerge/', methods = ['POST', 'GET'])
def pdfuploadformerge():
    if request.method == 'POST':
        f1 = request.files['file1']
        f2 = request.files['file2']
        if f1 and f2:
            pdfmerger = PyPDF2.PdfFileMerger()
            pdfmerger.append(f1)
            pdfmerger.append(f2)
            with open("merged.pdf", 'wb') as f:
                pdfmerger.write(f)
            try:
                return send_file('pdify.pdf',
                                 attachment_filename='pdify.pdf')
            except Exception as e:
                return str(e)
        else:
            return 'file(s) not provided'

@app.route('/pdfuploadforrotate/', methods = ['POST', 'GET'])
def pdfuploadforrotate():
    if request.method == 'POST':
        f = request.files['file']
        rotation = request.form.get('rotation_angle')
        if rotation == 'left':
            rotation = 270
        elif rotation == 'right':
            rotation = 90
        else:
            rotation = 180
        if f:
            pdfreader = PyPDF2.PdfFileReader(f)
            pdfwriter = PyPDF2.PdfFileWriter()
            for page in range(pdfreader.numPages):
                pageObj = pdfreader.getPage(page)
                pageObj.rotateClockwise(rotation)

                # adding rotated page object to pdf writer
                pdfwriter.addPage(pageObj)
            with open("pdify.pdf", 'wb') as f:
                pdfwriter.write(f)
            try:
                return send_file('pdify.pdf',
                                 attachment_filename='pdify.pdf')
            except Exception as e:
                return str(e)
        else:
            return 'file(s) not provided'

@app.route('/logout/')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/dashboard/')
def dashboard():
    if 'username' not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html")

if __name__=="__main__":
    app.run(debug=True)
