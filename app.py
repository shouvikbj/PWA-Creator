from flask import (
    Flask,
    render_template,
    redirect,
    request,
    url_for,
    session,
    flash,
    jsonify,
    make_response,
)
import json
import os
import uuid
import resizer
import datetime as dt

app = Flask(__name__, static_url_path='')
app.secret_key = "thisisasecretkey"

APP_ROOT = os.path.dirname(os.path.abspath(__file__))


@app.route("/signup", methods=["POST"])
def signup():
    json_file = open(f"{APP_ROOT}/db/login.json", "r")
    users = json.load(json_file)
    json_file.close()
    uid = str(uuid.uuid4())
    email = request.form.get("email")
    password = request.form.get("password")
    filename = ""
    file = request.files.get("file")
    for key,value in users.items():
        if(value["email"]==email):
            flash("Email already in use!", "info")
            return redirect(url_for('login'))
    if(file):
        filename = file.filename
        target = f"{APP_ROOT}/static/dps"
        destination = "/".join([target, filename])
        file.save(destination)
    details = {
        uid: {
            "email": str(email),
            "password": str(password),
            "dp": str(filename)
        }
    }
    users.update(details)
    json_file = open(f"{APP_ROOT}/db/login.json", "w")
    json_file.seek(0)
    json.dump(users, json_file, indent=2)
    json_file.close()
    os.makedirs(f"{APP_ROOT}/static/folders/{email}")
    json_file = open(f"{APP_ROOT}/db/mode.json", "r")
    modes = json.load(json_file)
    json_file.close()
    default_mode = {
        email: "light"
    }
    modes.update(default_mode)
    json_file = open(f"{APP_ROOT}/db/mode.json", "r")
    json_file.seek(0)
    json.dump(modes, json_file, indent=2)
    json_file.close()
    flash("Account successfully created!", "info")
    return redirect(url_for('login'))


@app.route("/login", methods=["POST","GET"])
def login():
    if(request.method == "GET"):
        return render_template("login.html")
    else:
        email = request.form.get("email")
        password = request.form.get("password")
        json_file = open(f"{APP_ROOT}/db/login.json", "r")
        users = json.load(json_file)
        json_file.close()
        for key,user in users.items():
            if((user["email"]==email) and (user["password"]==password)):
                resp = make_response(redirect(url_for('index')))
                resp.set_cookie('pwauname', email, max_age=60*60*24*365*2)
                return resp
        flash("Wrong credentials! Try again.", "danger")
        return redirect(url_for('login'))

@app.route("/")
def index():
    if(request.cookies.get('pwauname')):
        email = request.cookies.get('pwauname')
        json_file = open(f"{APP_ROOT}/db/login.json", "r")
        users = json.load(json_file)
        json_file.close()
        user = {}
        for key,value in users.items():
            if(value["email"]==str(email)):
                user = value
        json_file = open(f"{APP_ROOT}/db/data.json", "r")
        data = json.load(json_file)
        json_file.close()
        datas = []
        for key,value in data.items():
            if(value["email"]==str(email)):
                datas.append(value)
        datas.reverse()
        mode = "light"
        json_file = open(f"{APP_ROOT}/db/mode.json", "r")
        modes = json.load(json_file)
        json_file.close()
        for key,value in modes.items():
            mode = modes[str(email)]
        return render_template("index.html", user=user, datas=datas, mode=mode)
    else:
        return redirect(url_for('login'))


@app.route("/upload", methods=["POST"])
def upload():
    if(request.cookies.get("pwauname")):
        email = str(request.cookies.get("pwauname"))
        projectName = request.form.get("project_name")
        projectImage = request.files.get("project_image")
        projectImageName = ""
        json_file = open(f"{APP_ROOT}/db/data.json", "r")
        data = json.load(json_file)
        json_file.close()
        for key,value in data.items():
            if((value["email"]==email) and (value["projectName"]==projectName)):
                flash("Project already exists!")
                return redirect(url_for("index"))
        if(projectImage):
            os.makedirs(f"{APP_ROOT}/static/folders/{email}/{projectName}")
            projectImageName = projectImage.filename
            target = f"{APP_ROOT}/static/folders/{email}/{projectName}"
            destination = "/".join([target, projectImageName])
            projectImage.save(destination)
        else:
            flash("No image provided!")
            return redirect(url_for("index"))

        json_file = open(f"{APP_ROOT}/db/data.json", "r")
        data = json.load(json_file)
        json_file.close()
        newDataId = str(uuid.uuid4())
        curDate = dt.datetime.now()
        day = curDate.strftime("%d-%m-%Y")
        newData = {
            newDataId: {
                "email": email,
                "projectName": str(projectName),
                "date": str(day),
                # "projectImage": str(projectImageName),
                "48": "logo48.png",
                "72": "logo72.png",
                "96": "logo96.png",
                "144": "logo144.png",
                "196": "logo196.png",
                "512": "logo512.png",
                "app": "app.js",
                "serviceWorker": "serviceWorker.js",
                "manifest": "manifest.json"
            }
        }
        data.update(newData)
        json_file = open(f"{APP_ROOT}/db/data.json", "w")
        json_file.seek(0)
        json.dump(data, json_file, indent=2)
        json_file.close()
        resizer.resize(48,48,email,projectName,projectImageName)
        resizer.resize(72,72,email,projectName,projectImageName)
        resizer.resize(96,96,email,projectName,projectImageName)
        resizer.resize(144,144,email,projectName,projectImageName)
        resizer.resize(196,196,email,projectName,projectImageName)
        resizer.resize(512,512,email,projectName,projectImageName)
        os.remove(
            f"{APP_ROOT}/static/folders/{email}/{projectName}/{projectImageName}"
        )

        data = {
                    "manifest_version": 2,
                    "name": f"{projectName}",
                    "short_name": f"{projectName}",
                    "start_url": "/",
                    "display": "standalone",
                    "background_color": "#FFFFFF",
                    "theme_color": "#FFFFFF",
                    "orientation": "portrait",
                    "icons": [
                        {
                            "src": "./logo48.png",
                            "type": "image/png",
                            "sizes": "48x48"
                        },
                        {
                            "src": "./logo72.png",
                            "type": "image/png",
                            "sizes": "72x72"
                        },
                        {
                            "src": "./logo96.png",
                            "type": "image/png",
                            "sizes": "96x96"
                        },
                        {
                            "src": "./logo144.png",
                            "type": "image/png",
                            "sizes": "144x144"
                        },
                        {
                            "src": "./logo196.png",
                            "type": "image/png",
                            "sizes": "196x196"
                        },
                        {
                            "src": "./logo512.png",
                            "type": "image/png",
                            "sizes": "512x512"
                        }
                    ],
                    "scope": "/"
                }

        json_file = open(f"{APP_ROOT}/static/folders/{email}/{projectName}/manifest.json", "w")
        json_file.seek(0)
        json.dump(data, json_file, indent=2)
        json_file.close()
        
        flash(f"{projectName} created!")
        return redirect(url_for('index'))
    else:
        return redirect(url_for('login'))


@app.route("/project/<email>/<project>")
def viewProject(email,project):
    if(request.cookies.get("pwauname")):
        json_file = open(f"{APP_ROOT}/db/login.json", "r")
        users = json.load(json_file)
        json_file.close()
        user = {}
        for key,value in users.items():
            if(value["email"]==str(email)):
                user = value
        json_file = open(f"{APP_ROOT}/db/data.json", "r")
        data = json.load(json_file)
        json_file.close()
        datas = []
        for key,value in data.items():
            if(
                value["email"]==str(email) and 
                value["projectName"]==str(project)
            ):
                datas.append(value)
        mode = "light"
        json_file = open(f"{APP_ROOT}/db/mode.json", "r")
        modes = json.load(json_file)
        json_file.close()
        for key,value in modes.items():
            mode = modes[str(email)]
        return render_template("view.html", user=user, datas=datas, mode=mode)
    else:
        return redirect(url_for("login"))


@app.route("/info")
def info():
    if(request.cookies.get("pwauname")):
        email = request.cookies.get("pwauname")
        json_file = open(f"{APP_ROOT}/db/login.json", "r")
        users = json.load(json_file)
        json_file.close()
        user = {}
        for key,value in users.items():
            if(value["email"]==str(email)):
                user = value
        mode = "light"
        json_file = open(f"{APP_ROOT}/db/mode.json", "r")
        modes = json.load(json_file)
        json_file.close()
        for key,value in modes.items():
            mode = modes[str(email)]
        return render_template("info.html", user=user, mode=mode)
    else:
        return redirect(url_for("login"))


@app.route("/changeMode/light")
def enableLightMode():
    if(request.cookies.get("pwauname")):
        email = request.cookies.get("pwauname")
        json_file = open(f"{APP_ROOT}/db/mode.json", "r")
        modes = json.load(json_file)
        json_file.close()
        for key,value in modes.items():
            modes[email] = "light"
        json_file = open(f"{APP_ROOT}/db/mode.json", "w")
        json_file.seek(0)
        json.dump(modes, json_file, indent=2)
        json_file.close()
        return jsonify({"msg": "Done"})
    else:
        return redirect(url_for("login"))


@app.route("/changeMode/dark")
def enableDarkMode():
    if(request.cookies.get("pwauname")):
        email = request.cookies.get("pwauname")
        json_file = open(f"{APP_ROOT}/db/mode.json", "r")
        modes = json.load(json_file)
        json_file.close()
        for key,value in modes.items():
            modes[email] = "dark"
        json_file = open(f"{APP_ROOT}/db/mode.json", "w")
        json_file.seek(0)
        json.dump(modes, json_file, indent=2)
        json_file.close()
        return jsonify({"msg": "Done"})
    else:
        return redirect(url_for("login"))


@app.route("/logout")
def logout():
    resp = make_response(redirect(url_for('login')))
    resp.set_cookie('pwauname', expires=0)
    return resp


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=3000)
