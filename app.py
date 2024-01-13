import time

start = time.monotonic()

# Startup Start

import random
import datetime
from flask import *
import flask_login
import sys

from infrastructure.account_management import AccountManager, Account
from superstructure.make_profile import make_profile
from superstructure.mail_manager import MailManager
from infrastructure.sessionmanager import SessionManager

from superstructure.status_detector import shutdown_event

from superstructure.properties import Properties, _Properties
from superstructure.secrets import Secrets, _Secrets

SessionManager.load()

import os

_Properties.load_properties()
_Secrets.load_secrets()
print(Properties.properties)

Account.salt = Secrets.get("HASH_SALT")
account_manager = AccountManager(
    Secrets.get("DATA_KEY").encode("utf8"),
    Secrets.get("HASH_SALT"),
)

mail_manager = MailManager(Secrets.get("MAIL_ADDRESS"), Secrets.get("MAIL_PASSWORD"))

app = Flask(__name__, template_folder="public/documents", static_folder="public")
app.secret_key = Secrets.get("APP_KEY")

comingson = 'Trup <a href="/comingson">#Comingson</a>'

password_characters = Properties.get("PASSWORD_CHARACTERS")

login_manager = flask_login.LoginManager()

login_manager.init_app(app)

from functools import wraps

# Startup end


def login_aborted(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        if flask_login.current_user.is_authenticated:
            return abort(418)
        return func(*args, **kwargs)

    return decorator


@app.route("/favicon.ico", methods=["GET"])
def favicon():
    return send_file("trup-icon-64.ico")


@app.route("/favicon.png", methods=["GET"])
def favpng():
    return send_file("trup-icon.png")


def addframe(html: str, title=None, subtitle=None, page="other"):
    if flask_login.current_user.is_authenticated:
        username = flask_login.current_user.account.username
        profilephoto = "/profile-photo"
        loginredirect = "/account"
    else:
        profilephoto = "/profile-photo"
        username = "Login"
        loginredirect = "/login"
        if random.randint(0, 10000) == 1 or (
            datetime.datetime.now().month == 2 and datetime.datetime.now().day == 6
        ):
            profilephoto = "/trup-nft"
            loginredirect = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

    frame = render_template(
        "frame.html",
        title="TRUP" if title == None else "TRUP - " + title,
        subtitle=subtitle,
        page=page,
        profilephoto=profilephoto,
        username=username,
        loginredirect=loginredirect,
        # ishomecurrent="<span class='sr-only'>(current)</span>" if onhome else "",
        # isstorecurrent="<span class='sr-only'>(current)</span>" if onlibrary else "",
        # islibrarycurrent="<span class='sr-only'>(current)</span>" if onhome else "",
        # iscommunitycurrent="<span class='sr-only'>(current)</span>"
        # if oncommunity
        # else "",
    )
    html = html.replace("\r\n", "\n")
    if len(html.split("\n#head-end\n")) == 1:
        frame = frame.replace("$head", "")
        frame = frame.replace("$body", html)
    else:
        frame = frame.replace("$head", html.split("\n#head-end\n")[0])
        frame = frame.replace("$body", html.split("\n#head-end\n")[1])

    return frame


class User(flask_login.UserMixin):
    pass


@login_manager.user_loader
def user_loader(email):
    account = account_manager.get_account_by_email(email)
    if account is None:
        return
    user = User()
    user.id = email
    user.account = account
    return user


@login_manager.request_loader
def request_loader(request):
    email = request.form.get("email")
    if email is None:
        return
    account = account_manager.get_account_by_email(email)
    if account is None:
        return
    user = User()
    user.id = email
    user.account = account
    return user


@app.errorhandler(Exception)
def error(ex):
    if isinstance(ex, Exception):
        raise ex
    ex = str(ex)
    return addframe(
        f"<h1>{ex.split(':')[0]}</h1><p>{ex.removeprefix(ex.split(':')[0]+':')}</p><p>I'm putting <a href=\"/\">home</a> here in case you want to go.</p>",
    )


@app.route("/", methods=["GET"])
def index():
    return addframe(render_template("index.html"), page="home")


@app.route("/profile-photo", methods=["GET"])
def profile_photo():
    return profile_photo_resized(64)


@app.route("/profile-photo-<int:scale>", methods=["GET"])
def profile_photo_resized(scale: int):
    if scale > 1024:
        return "Why are you pushing your limits?"
    if scale < 32:
        return "Too small, isn't it?"
    if scale not in [32, 40, 64, 128, 256, 512, 1024]:
        return f"Sorry sir we don't have {scale}. I can give you {random.choice([32, 40, 64, 128, 256, 512, 1024])}, take it or leave it!"
    if flask_login.current_user.is_authenticated:
        return send_file(
            make_profile(
                flask_login.current_user.account.username.replace("@", "_").replace(
                    ".", "-"
                ),
                scale,
                int(scale / 8),
            ),
            mimetype="image/png",
        )
    else:
        return send_file(
            f"data/uploads/profile_photos/trup-sunglasses-nft-{scale}.png",
            mimetype="image/jpg",
        )


@app.route("/rick-photo", methods=["GET"])
def rick_photo():
    return send_file(
        "data/uploads/profile_photos/rick-roll-pp.png", mimetype="image/png"
    )


@app.route("/page/<path:path>", methods=["GET"])
def html(path):
    return addframe(render_template(path + ".html"))


@login_aborted
def loginpage(redirect):
    return addframe(render_template("login.html", redirect=redirect))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return loginpage(request.args.get("redirect"))

    data = request.form["email"]
    if "@" in data and "." in data:
        email = data
        account = account_manager.get_account_by_email(email)
    else:
        username = data
        account = account_manager.get_account_by_username(username)
        email = account.email
    if account is None:
        return "account not found"
    user = User()
    user.id = email
    user.account = account
    if account.check_password(request.form["password"], account_manager.salt):
        user = User()
        user.id = email
        user.account = account
        flask_login.login_user(user)
        if request.args.get("redirect") != None:
            return redirect(request.args.get("redirect"))
        return redirect("/")

    return "Password is wrong or account not found"


@app.route("/signup", methods=["GET", "POST"])
@login_aborted
def signup():
    if request.method == "GET":
        return addframe(render_template("signup.html"))

    name = request.form["name"]
    username = request.form["username"]
    if "@" in username:
        return "Sorry, username cannot contain @ character"
    email = request.form["email"]
    password = request.form["password"]

    if account_manager.username_exists(username):
        return "Username exists"

    if account_manager.email_exists(email):
        return "Email exists"

    accountid = account_manager.add_account(
        Account(username, name, email, password, False)
    )

    if request.args.get("redirect") != None:
        return redirect(request.args.get("redirect"))

    message = "You signed up successfully, now you can login."
    return redirect(f"/login?message={message}&status=success")


@app.route("/logout")
@flask_login.login_required
def logout():
    flask_login.logout_user()
    return "Logged out"


@app.route("/library", methods=["GET"])
@flask_login.login_required
def library():
    return addframe(render_template("library.html"), page="library")


@app.route("/store", methods=["GET"])
def store():
    return addframe(comingson, page="store")


@app.route("/community", methods=["GET"])
def community():
    return addframe(comingson, page="community")


@app.route("/comingson", methods=["GET"])
def coming_son():
    if flask_login.current_user.is_authenticated:
        return addframe(
            """<pre>
<label title="I love it! But I wrote TRUP with Python ¬_¬">C#<br/></label>
<code>
<span class="line">28467&nbsp;&nbsp;</span>
<span class="comment">// That\'s why you signed up: (aka "the secret")</span><br>
<span class="line">28468&nbsp;&nbsp;</span>
<span class="ID">private protected string</span> Comingson = <span class="string">"Comin Soon"</span>;<br>
<span class="line">28469&nbsp;&nbsp;</span><br>
<span class="line">28470&nbsp;&nbsp;</span>
<span class="comment">// Made by:</span><br>
<span class="line">28471&nbsp;&nbsp;</span>
<span class="comment">// ████████╗██████╗ ██╗   ██╗██████╗ </span><br>
<span class="line">28472&nbsp;&nbsp;</span>
<span class="comment">// ╚══██╔══╝██╔══██╗██║   ██║██╔══██╗</span><br>
<span class="line">28473&nbsp;&nbsp;</span>
<span class="comment">//    ██║   ██████╔╝██║   ██║██████╔╝</span><br>
<span class="line">28474&nbsp;&nbsp;</span>
<span class="comment">//    ██║   ██╔══██╗██║   ██║██╔═══╝ </span><br>
<span class="line">28475&nbsp;&nbsp;</span>
<span class="comment">//    ██║   ██║  ██║╚██████╔╝██║     </span><br>
<span class="line">28476&nbsp;&nbsp;</span>
<span class="comment">//    ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═╝     </span><br>
<span class="line">28477&nbsp;&nbsp;</span>
<span class="comment">// ¯\_( ͡° ͜ʖ ͡°)_/¯</span>
</code>
</pre>""".replace(
                "\n", ""
            ),
            page="community",
        )
    return addframe(
        'Plese <a href="/login?redirect=/comingson">login</a> to view definition of <a href="https://www.microsoft.com/en-us/comingsoon">Comingson</a>.',
        page="community",
    )


@app.route("/update-account", methods=["POST"])
@flask_login.login_required
def update_account():
    if None in [
        request.form.get("name"),
        request.form.get("username"),
        request.form.get("email"),
        request.form.get("old_password"),
    ]:
        return abort(422)  # TODO: Look which error must be returned
    name = request.form.get("name")
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("old_password")
    if not account_manager.get_account_by_id(
        flask_login.current_user.account.id
    ).check_password(password):
        return abort(403)
    account = account_manager.get_account_by_id(flask_login.current_user.account.id)
    account.name = name
    account.username = username
    # account.email = email
    res = account_manager.update_account(account)
    if res == 1:
        return "Username already in use"
    if res == 2:
        return "Email already in use (And it is a bug, report it, (be fast (be faster and faster)))"
    if res == 4:
        flask_login.current_user.account = account
        return redirect("/account")
    return "What the heck is this? A REALLY UNKNOWN ERROR OCCURED!"


@app.route("/account", methods=["GET"])
@flask_login.login_required
def account():
    return addframe(
        render_template(
            "account.html",
            name=flask_login.current_user.account.name,
            username=flask_login.current_user.account.username,
            email=flask_login.current_user.account.email,
        )
    )


@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    if request.method == "GET":
        if not flask_login.current_user.is_authenticated:
            return abort(422)
        account = account_manager.get_account_by_id(flask_login.current_user.account.id)
    lang = "tr"
    session_id = SessionManager.add_session(account.id, "reset-password")
    mail_manager.add_queue(
        account.email,
        "Şifre Sıfırlama",
        render_template(f"mails/{lang}/password_reset.html", session_id=session_id),
    )
    return f"Şifre sıfırlama işleminizle ilgili bilgi \"{account.email[0]}...@{account.email.split('@')[-1]}\" e-postanıza en kısa zamanda gönderilecektir. ({(len(mail_manager.queue)*mail_manager.wait_time)/60} dakika içinde gelmesi planlanmaktadır)"


def _reset_password(user_id):
    account = account_manager.get_account_by_id(user_id)
    password = "".join(
        [
            password_characters[
                int.from_bytes(os.urandom(1), "big") % len(password_characters)
            ]
            for _ in range(10)
        ]
    )
    account.password = account_manager.hash_password(password)
    account_manager.update_account(account)
    lang = "tr"
    mail_manager.add_queue(
        account.email,
        "Şifre Sıfırlama",
        render_template(f"mails/{lang}/password_resetted.html", new_password=password),
    )
    return f"Şifreniz sıfırlanmıştır, yeni şifreniz e-postanıza gönderilecektir. ({(len(mail_manager.queue)*mail_manager.wait_time)/60} dakika içinde gelmesi planlanmaktadır)"


@app.route("/api/complete-session/<sessionid>", methods=["GET"])
def complete_session(sessionid):
    session = SessionManager.get_session(sessionid)
    if session is None:
        return "Removed or non-created session (Maybe it was too old?)"
    if session[1] == "reset-password":
        _reset_password(session[0])
        SessionManager.remove_session(sessionid)
        return "Şifreniz sıfırlanmış, yeni şifreniz e-postanıza gönderilmiştir."
    else:
        SessionManager.remove_session(sessionid)
        raise ValueError(f"Corrupted Session: {session}")


@app.route("/search")
def search():
    if "q" in request.args.keys() and request.args["q"].replace(" ", "") != "":
        return addframe(render_template("search.html", query=request.args["q"]))
    return redirect("/")


mail_manager.start()

print(f"Server started in {time.monotonic() - start} seconds")


@shutdown_event
def shutdown_server(signal):
    print("Shutting server down")
    return
    func = request.environ.get("werkzeug.server.shutdown")
    if func is None:
        raise RuntimeError("Not running with the Werkzeug Server")
    func()


app.run(host="localhost", port=5000, debug=True)
