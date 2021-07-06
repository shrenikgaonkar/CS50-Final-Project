from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from cs50 import SQL
import os

app = Flask(__name__)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///employee.db")

@app.route("/")
def index():
    if not session.get("user_id"):
        return redirect("/login")

    temp = db.execute("SELECT first_name,surname FROM user_info WHERE person_id=?",session["user_id"])
    username = temp[0]['first_name'] + " " + temp[0]['surname']

    profile_pic_name='static/documents/profile_pic/'+str(session["user_id"])+'.jpg'
    document_status=db.execute("SELECT * FROM user_documents WHERE person_id=?",session["user_id"])

    page="dashboard"

    projects=db.execute("SELECT * FROM projects_user WHERE person_id=?",session["user_id"])

    completed_projects=0

    incomplete_projects=list()

    for project in projects:
        if project["status"]=="completed":
            completed_projects += 1

        elif project["status"]=="pending":
            temp_project=dict()
            temp_project["project_id"]=project["project_id"]
            temp_project["completion_date"]=project["completion_date"]
            incomplete_projects.append(temp_project)

    for project in incomplete_projects:
        project["project_name"]=db.execute("SELECT name FROM projects WHERE id=?",project["project_id"])[0]["name"]


    project_month=dict()

    for i in range(1,13):
        project_month[i]=0

    for project in projects:
        date=project["starting_date"].split("-")
        for i in range(len(date)):
            date[i]=int(date[i])

        if date[0]==2021:
            project_month[date[1]] += 1

    return render_template("index.html", username=username, page=page, dp = profile_pic_name, document_status=document_status[0], total=completed_projects+len(incomplete_projects), completed=completed_projects, incomplete=len(incomplete_projects), incomplete_projects=incomplete_projects, project_month=project_month)


@app.route("/login", methods=["GET", "POST"])
def login():

    session.clear()

    if request.method == "POST":
        username=request.form.get("username")
        password=request.form.get("password")

        row_username=db.execute("SELECT * FROM users WHERE username=?",username)

        if len(row_username)!=1:
            apology="username doesn't exist"
            return render_template("login.html",error=apology)

        correct_password=db.execute("SELECT password FROM users WHERE username=?",username)[0]["password"]

        if password != correct_password:
            apology="The password is incorrect"
            return render_template("login.html",error=apology)

        session["user_id"] = db.execute("SELECT id FROM users WHERE username=?",username)[0]["id"]

        return redirect("/")

    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    session["user_id"] = None
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        first_name=request.form.get("first-name")
        surname=request.form.get("last-name")
        email=request.form.get("email")
        username=request.form.get("username")
        password=request.form.get("password")
        confirmation=request.form.get("confirmation")


        if not first_name:
            apology="Please enter First name"
            return render_template("register.html",error=apology)

        if not surname:
            apology="Please enter Last name"
            return render_template("register.html",error=apology)

        if not email:
            apology="Please enter a valid email-id"
            return render_template("register.html",error=apology)

        if not username:
            apology="Please enter a username"
            return render_template("register.html",error=apology)

        elif not password:
            apology="Please enter a password"
            return render_template("register.html",error=apology)

        elif len(password)<8:
            apology="Please enter atleast 8 character password"
            return render_template("register.html",error=apology)

        elif not confirmation:
            apology="Please enter the password again"
            return render_template("register.html",error=apology)

        elif not confirmation==password:
            apology="Please enter the same password again"
            return render_template("register.html",error=apology)

        try:
            result = db.execute("INSERT INTO users (username, password) VALUES (:username, :password)", username=username, password=password)

        except:
            apology="username is unavailable"
            return render_template("register.html",error=apology)


        session["user_id"]=db.execute("SELECT id FROM users WHERE username=?",username)[0]["id"]

        db.execute("INSERT INTO user_info (person_id, first_name, surname, email) VALUES (?, ?, ?, ?)",int(session["user_id"]), first_name, surname, email)
        db.execute("INSERT INTO user_documents (person_id, profile_pic, pancard, adhaar) VALUES (?, ?, ?, ?)", int(session["user_id"]), "NO", "NO", "NO")

        return redirect("/edit_profile")

    else:
        return render_template("register.html")



@app.route("/edit_profile", methods=["GET","POST"])
def edit_profile():

    if not session.get("user_id"):
        return redirect("/login")

    temp = db.execute("SELECT first_name,surname FROM user_info WHERE person_id=?",session["user_id"])
    currentuser = temp[0]['first_name'] + " " + temp[0]['surname']

    profile_pic_name='static/documents/profile_pic/'+str(session["user_id"])+'.jpg'

    document_status=db.execute("SELECT * FROM user_documents WHERE person_id=?",session["user_id"])

    temp=db.execute("SELECT * FROM user_info WHERE person_id=?",session["user_id"])

    temp_first_name=temp[0]["first_name"]
    if temp_first_name is None:
        temp_first_name=""

    temp_surname=temp[0]["surname"]
    if temp_surname is None:
        temp_surname=""

    temp_email=temp[0]["email"]
    if temp_email is None:
        temp_email=""

    temp_contact=temp[0]["contact"]
    if temp_contact is None:
        temp_contact=""

    temp_gender=temp[0]["gender"]
    if temp_gender is None:
        temp_gender=""

    temp_dob=temp[0]["dob"]
    if temp_dob is None:
        temp_dob=""

    temp_joining_date=temp[0]["joining_date"]
    if temp_joining_date is None:
        temp_joining_date=""

    apology=""
    if not session.get("user_id"):
        return redirect("/login")

    username = db.execute("SELECT username FROM users WHERE id=?",session.get("user_id"))


    if request.method == "POST":


        first_name=request.form.get("first_name")
        surname=request.form.get("surname")
        email=request.form.get("email")
        contact=request.form.get("contact")
        dob=request.form.get("dob")
        joining_date=request.form.get("joining_date")
        gender=request.form.get("gender")

        print(first_name, surname, email, contact, dob, joining_date, gender)

        if not first_name:
            apology="please enter your first name"
            return render_template("edit_profile.html", dp = profile_pic_name, error=apology, first_name=temp_first_name, surname=temp_surname, email=temp_email, contact=temp_contact, gender=temp_gender, dob=temp_dob, joining_date=temp_joining_date, username=currentuser, document_status=document_status[0], profile_pic_name=profile_pic_name)

        if not surname:
            apology="please enter your surname"
            return render_template("edit_profile.html", dp = profile_pic_name, error=apology, first_name=temp_first_name, surname=temp_surname, email=temp_email, contact=temp_contact, gender=temp_gender, dob=temp_dob, joining_date=temp_joining_date, username=currentuser, document_status=document_status[0], profile_pic_name=profile_pic_name)

        if not email:
            apology="please enter email-id"
            return render_template("edit_profile.html", dp = profile_pic_name, error=apology, first_name=temp_first_name, surname=temp_surname, email=temp_email, contact=temp_contact, gender=temp_gender, dob=temp_dob, joining_date=temp_joining_date, username=currentuser, document_status=document_status[0], profile_pic_name=profile_pic_name)

        if not contact:
            apology="please enter a contact number"
            return render_template("edit_profile.html", dp = profile_pic_name, error=apology, first_name=temp_first_name, surname=temp_surname, email=temp_email, contact=temp_contact, gender=temp_gender, dob=temp_dob, joining_date=temp_joining_date, username=currentuser, document_status=document_status[0], profile_pic_name=profile_pic_name)

        if not dob:
            apology="enter a valid birth date"
            return render_template("/edit_profile.html", dp = profile_pic_name, error=apology, first_name=temp_first_name, surname=temp_surname, email=temp_email, contact=temp_contact, gender=temp_gender, dob=temp_dob, joining_date=temp_joining_date, username=currentuser, document_status=document_status[0], profile_pic_name=profile_pic_name)

        if not joining_date:
            apology="enter a valid joining date"
            return render_template("/edit_profile.html", dp = profile_pic_name, error=apology, first_name=temp_first_name, surname=temp_surname, email=temp_email, contact=temp_contact, gender=temp_gender, dob=temp_dob, joining_date=temp_joining_date, username=currentuser, document_status=document_status[0], profile_pic_name=profile_pic_name)

        if dob > joining_date:
            apology="Joining date Can not be before Date of birth"
            return render_template("/edit_profile.html", dp = profile_pic_name, error=apology, first_name=temp_first_name, surname=temp_surname, email=temp_email, contact=temp_contact, gender=temp_gender, dob=temp_dob, joining_date=temp_joining_date, username=currentuser, document_status=document_status[0], profile_pic_name=profile_pic_name)

        try:
            db.execute("UPDATE user_info SET email=?, contact=?, gender=?, dob=?, joining_date=?, first_name=?, surname=? WHERE person_id=?", email, contact, gender, dob, joining_date, first_name, surname, session["user_id"])

        except:
            print("error in adding to database")
            print(email, contact, gender, dob, joining_date, session["user_id"])

        return redirect("/")



    else:
        return render_template("edit_profile.html", dp = profile_pic_name, username=currentuser,error=apology, first_name=temp_first_name, surname=temp_surname, email=temp_email, contact=temp_contact, gender=temp_gender, dob=temp_dob, joining_date=temp_joining_date, document_status=document_status[0], profile_pic_name=profile_pic_name)






@app.route("/projects", methods = ["GET","POST"])
def projects():

    if not session.get("user_id"):
        return redirect("/login")

    temp = db.execute("SELECT first_name,surname FROM user_info WHERE person_id=?",session["user_id"])
    currentuser = temp[0]['first_name'] + " " + temp[0]['surname']

    profile_pic_name='static/documents/profile_pic/'+str(session["user_id"])+'.jpg'
    document_status=db.execute("SELECT * FROM user_documents WHERE person_id=?",session["user_id"])

    page = "projects"

    # TO-DO: Take 5 projects from database and save them to rows
    # TO-DO: Make Post Requests from projects for next 5 rows

    project_items=db.execute("SELECT * FROM projects_user WHERE person_id=?", session["user_id"])

    project_ids=list()

    for item in project_items:
        project_ids.append(item["project_id"])

    project_names=list()

    for project_id in project_ids:
        project_name=db.execute("SELECT name FROM projects WHERE id=?",project_id)[0]["name"]
        project_names.append(project_name)


    print(project_ids)
    print(project_names)
    project_length = len(project_items)
    pages = [0,int(project_length/5) + 1]

    for index in range(project_length):
        project_name=project_names[index]
        project_items[index]["project_name"]=project_name


    if request.method == "POST":

        pageno = int(request.form.get("page"))
        if project_length <= 5* (pageno+1):
            counter = project_length
        else :
            counter = 5
        pages[0] = pageno
        return render_template("projects.html", dp = profile_pic_name, document_status=document_status[0], username=currentuser,pages = pages, page = page, rows=project_items[5* (pageno):5* (pageno) + counter], pending="pending")
    else :

        if project_length <= 5:
            counter = project_length
        else :
            counter = 5

        return render_template("projects.html", dp = profile_pic_name, document_status=document_status[0], username=currentuser, pages=pages, page = page, rows=project_items[0:counter], pending="pending")




@app.route("/add_project", methods=["GET", "POST"])
def add_project():

    if not session.get("user_id"):
        return redirect("/login")

    temp = db.execute("SELECT first_name,surname FROM user_info WHERE person_id=?",session["user_id"])
    currentuser = temp[0]['first_name'] + " " + temp[0]['surname']

    profile_pic_name='static/documents/profile_pic/'+str(session["user_id"])+'.jpg'
    document_status=db.execute("SELECT * FROM user_documents WHERE person_id=?",session["user_id"])

    page = "projects"

    apology=""

    if request.method == "POST":
        project_name=request.form.get("project_name")
        starting_date=request.form.get("starting_date")
        completion_date=request.form.get("completion_date")
        status=request.form.get("status")
        role=request.form.get("role")
        description=request.form.get("description")

        if not project_name:
            apology="Enter project name"
            return render_template("add_project.html", dp = profile_pic_name, document_status=document_status[0], username=currentuser, page = page, apology=apology)

        if not starting_date:
            apology="Enter starting date"
            return render_template("add_project.html", dp = profile_pic_name, document_status=document_status[0], username=currentuser, page = page, apology=apology)

        if not completion_date:
            apology="Enter completion date"
            return render_template("add_project.html", dp = profile_pic_name, document_status=document_status[0], username=currentuser, page = page, apology=apology)

        if not status:
            apology="Enter status"
            return render_template("add_project.html", dp = profile_pic_name, document_status=document_status[0], username=currentuser, page = page, apology=apology)

        if not role:
            apology="Enter role"
            return render_template("add_project.html", dp = profile_pic_name, document_status=document_status[0], username=currentuser, page = page, apology=apology)

        if not description:
            apology="Enter description"
            return render_template("add_project.html", dp = profile_pic_name, document_status=document_status[0], username=currentuser, page = page, apology=apology)

        print(type(starting_date))

        if starting_date > completion_date:
            apology="Completion Date can not be before starting date"
            return render_template("add_project.html", dp = profile_pic_name, document_status=document_status[0], username=currentuser, page = page, apology=apology)

        temp_project_names=db.execute("SELECT name FROM projects")

        project_names=list()

        for item in temp_project_names:
            project_names.append(item["name"])


        if project_name not in project_names:
            db.execute("INSERT INTO projects (name) VALUES (?)",project_name)

        project_id=int(db.execute("SELECT id FROM projects WHERE name=?",project_name)[0]["id"])

        db.execute("INSERT INTO projects_user (project_id, person_id, starting_date, completion_date, status, role, description) VALUES (?, ?, ?, ?, ?, ?, ?)", project_id, session["user_id"], starting_date, completion_date, status, role, description)

        return redirect("/projects")


    else:
        return render_template("add_project.html", dp = profile_pic_name, document_status=document_status[0], username=currentuser, page = page, apology=apology)




@app.route("/profile", methods=["GET", "POST"])
def profile():

    if not session.get("user_id"):
        return redirect("/login")

    temp = db.execute("SELECT first_name,surname FROM user_info WHERE person_id=?",session["user_id"])
    currentuser = temp[0]['first_name'] + " " + temp[0]['surname']

    profile_pic_name='static/documents/profile_pic/'+str(session["user_id"])+'.jpg'
    document_status=db.execute("SELECT * FROM user_documents WHERE person_id=?",session["user_id"])

    profile_pic_name='static/documents/profile_pic/'+str(session["user_id"])+'.jpg'
    pancard_name='static/documents/pancard/'+str(session["user_id"])+'.pdf'
    adhaar_name='/static/documents/adhaar/'+str(session["user_id"])+'.pdf'

    document_status=db.execute("SELECT * FROM user_documents WHERE person_id=?",session["user_id"])

    if request.method == "POST":
        return redirect("/edit_profile")

    else:
        data=db.execute("SELECT * FROM user_info WHERE person_id=?",session["user_id"])
        return render_template("profile.html", dp = profile_pic_name, username=currentuser, data=data[0], document_status=document_status[0], profile_pic_name=profile_pic_name, adhaar_name=adhaar_name, pancard_name=pancard_name)





@app.route("/add_profile_pic", methods=["POST"])
def add_profile_pic():

    if not session.get("user_id"):
        return redirect("/login")

    profile_pic=request.files["profile_pic"]
    if profile_pic.filename =="":
        return "No file selected for profile picture"

    if profile_pic.filename.split('.')[-1] not in ['png', 'jpg', 'jpeg']:
        return "Please select JPEG, PNG, JPG type of file only for profile picture"

    profile_pic.save(os.path.join("static/documents/profile_pic", str(session["user_id"])+'.jpg'))

    db.execute("UPDATE user_documents SET profile_pic =? WHERE person_id=?", "YES", session["user_id"])

    return redirect("/profile")

@app.route("/delete_profile_pic", methods=["POST"])
def delete_profile_pic():

    if not session.get("user_id"):
        return redirect("/login")

    db.execute("UPDATE user_documents SET profile_pic =? WHERE person_id=?", "NO", session["user_id"])

    return redirect("/profile")

@app.route("/add_pancard", methods=["POST"])
def add_pancard():

    print("Done")

    if not session.get("user_id"):
        return redirect("/login")

    pancard=request.files["pancard"]

    if pancard.filename == "":
        return "Please enter a file to upload for pancard"

    if pancard.filename.split('.')[-1] != 'pdf':
        return "Please enter a pdf file for pancard"

    pancard.save(os.path.join("static/documents/pancard", str(session["user_id"])+'.pdf'))

    db.execute("UPDATE user_documents SET pancard =? WHERE person_id=?", "YES", session["user_id"])

    return redirect("/profile")


@app.route("/add_adhaar", methods=["POST"])
def add_adhaar():

    print("Done")

    if not session.get("user_id"):
        return redirect("/login")

    adhaar=request.files["adhaar"]

    if adhaar.filename == "":
        return "Please enter a file to upload for adhaar"

    if adhaar.filename.split('.')[-1] != 'pdf':
        return "Please enter a pdf file for adhaar"

    adhaar.save(os.path.join("static/documents/adhaar", str(session["user_id"])+'.pdf'))

    db.execute("UPDATE user_documents SET adhaar =? WHERE person_id=?", "YES", session["user_id"])

    return redirect("/profile")


@app.route("/mark_project_complete", methods=["POST"])
def mark_project_complete():

    if not session.get("user_id"):
        return redirect("/login")

    project_id=request.form.get("project_id")
    role=request.form.get("role")

    db.execute("UPDATE projects_user SET status=? WHERE project_id=? AND person_id=? AND role=?", "completed", project_id, session["user_id"], role)

    return redirect("/projects")

@app.route("/delete_project", methods=["POST"])
def delete_project():

    if not session.get("user_id"):
        return redirect("/login")

    project_id=request.form.get("project_id")
    role=request.form.get("role")

    db.execute("DELETE FROM projects_user WHERE project_id=? AND person_id=? AND role=?", project_id, session["user_id"], role)

    return redirect("/projects")