from flask import Flask, render_template, request, redirect, url_for
from circle import Circle
from captcha_generate import Captcha
from database import Database
import base64
import time
import qrcode
from io import BytesIO
from captcha.image import ImageCaptcha

api_key = ""
entity = ""


app = Flask(__name__)
circle = Circle(api_key, entity)
captcha = Captcha()
database = Database(DB_NAME='postgres',
                    DB_USER='postgres',
                    DB_PASSWORD='',
                    DB_HOST='127.0.0.1',
                    DB_PORT='5432')
database.create_table()
user_ids = {}


def get_username(id):
    username = database.get_data(id)
    if username == None or username == "":
        return "Anonymous"
    else:
        return username


def build_leaderboard(users):
    users.reverse()
    leaderboard = []
    if len(users) < 23:
        length = len(users)
    else:
        length = 23
    for i in range(3, length):
        leaderboard.append(f'''<div id="ickn3f" class="text-main-content">
            <span id="i8rkg">#{i + 1} - <b>{get_username(users[i]["id"])}</b> <span draggable="true" id="ipko4q">({users[i]["balance"]} USD)</span><b draggable="true"> </b></span>
    </div>''')

    podium = f'''<div class="gjs-grid-column feature-item" id="iikag">
          <h3 class="gjs-heading" id="igbhh">1rst place - {get_username(users[0]["id"])}</h3>
          <div class="text-main-content" id="iwdqq"><span id="ic4nh">Amount donated: {users[0]["balance"]} USD</span></div>
        </div>
        <div id="ilpi3" class="gjs-grid-column feature-item">
          <h3 id="in9ef" class="gjs-heading">2nd place - {get_username(users[1]["id"])}</h3>
          <div id="i8isa" class="text-main-content">Amount donated: {users[1]["balance"]} USD</div>
        </div>
        <div id="idv32l" class="gjs-grid-column feature-item">
          <h3 id="ieu6p6" class="gjs-heading">3rd place - {get_username(users[2]["id"])}</h3>
          <div id="izqkf7" class="text-main-content"><span id="iwu1u">Amount donated: {users[2]["balance"]} USD</span></div>
        </div>'''

    return {"podium": podium, "leaderboard": "".join(leaderboard)}


def generate_qr(address):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(address)
    qr.make(fit=True)

    qr_img = qr.make_image(fill_color="black", back_color="white")

    image_buffer = BytesIO()
    qr_img.save(image_buffer, format="PNG")

    return base64.b64encode(image_buffer.getvalue()).decode('utf-8')


@app.route('/')
def main():
    leaderboard = build_leaderboard(circle.get_ranking())
    return render_template('index.html', podium=leaderboard["podium"], leaderboard=leaderboard["leaderboard"], total=circle.get_total())


@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", info="404 page not found.", error="404")


@app.errorhandler(500)
def server_error(e):
    return render_template("error.html", info="There has been an error on our end.", error="500")


@app.route('/donate', methods=["GET", "POST"])
def donate():
    if request.method == "GET":
        c = captcha.generate_captcha()
        return render_template("donate.html", captcha=c["image"], id=c["id"])
    else:
        if captcha.captchas[request.form.get("id")]["text"].lower() == request.form.get("text").lower():
            id = circle.create_wallet()

            database.insert_data(id, request.form.get("username"))
            address = circle.get_address(id)
            return render_template("result.html", address=address, qr=generate_qr(address))
        else:
            return render_template("error.html", error="Captcha Wrong!", info="Please try again.")


if __name__ == "__main__":
    app.run(host="192.168.0.46", port=80, threaded=True)
