import base64
import random
import string
import uuid
import time
from io import BytesIO
from captcha.image import ImageCaptcha


class Captcha:

    def __init__(self) -> None:
        self.captchas = {}

    def generate_captcha(self):
        captcha = ImageCaptcha()

        captcha_text = ''.join(random.choice(
            string.ascii_letters) for _ in range(4))

        image_stream = BytesIO()
        captcha.write(captcha_text, image_stream, format='PNG')
        image_stream.seek(0)
        image_base64 = base64.b64encode(image_stream.read()).decode('utf-8')

        image_id = str(uuid.uuid4())

        self.captchas[image_id] = {"text": captcha_text, "time": time.time()}

        self.clean()

        return {"id": image_id, "image": image_base64}

    def clean(self):
        t = time.time()

        try:
            for key in self.captchas.keys():
                if t - self.captchas[key]["time"] > 300:
                    del self.captchas[key]
        except RuntimeError:
            return
