import sys  # sys нужен для передачи argv в QApplication
import requests
import json
from os import mkdir, listdir, remove
from PyQt5 import QtWidgets, QtGui
import app_design  # design file
from PIL import Image


class MinioError(Exception):
    pass


class wormchan_app(QtWidgets.QMainWindow, app_design.Ui_MainWindow):
    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super().__init__()
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна
        self.username = None
        self.password = None
        self.token = None
        self.pics = None
        self.pic_index = self.load_index() if self.load_index() != None else 0
        self.progressBar.setValue(self.pic_index)
        self.current_pic = "./cache/nothing.jpg"

        self.submit_data.clicked.connect(self.login)

        self.submit_data.clicked.connect(self.switch_to_register)

        self.send_data.clicked.connect(self.register_user)

        self.rescan_btn.clicked.connect(self.rescan)
        self.previous_btn.clicked.connect(self.prev_img)
        self.next_btn.clicked.connect(self.next_img)

        self.save_btn.clicked.connect(self.save)
        self.pepe_btn.clicked.connect(lambda a: self.save(pepe=True))

        self.scrape_menu_btn.clicked.connect(self.switch_to_scrape)
        self.return_btn.clicked.connect(self.switch_to_images)

        self.cache_index.clicked.connect(self.save_index)

    def switch_to_login(self):
        self.app_pages.setCurrentIndex(0)

    def switch_to_images(self):
        self.app_pages.setCurrentIndex(1)

    def switch_to_scrape(self):
        self.app_pages.setCurrentIndex(2)

    def switch_to_register(self):
        self.app_pages.setCurrentIndex(3)

    def login(self):
        if not self.username:
            self.username = self.login_input.text()
            self.password = self.password_input.text()
        data = {'grant_type': 'password',
                'username': self.username,
                'password': self.password}
        headers = {
            'Authorization': 'Basic Og==',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json, text/plain, */*',
            'X-Requested-With': 'XMLHttpRequest',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty'
        }
        response = requests.post('http://127.0.0.1:8000/token', headers=headers, data=data)
        self.token = response.json().get("access_token")
        self.pics = self.get_cached_pic_names()
        if not self.pics:
            self.rescan()
            self.pics = self.get_cached_pic_names()
        self.progressBar.setMaximum(len(self.pics))
        self.current_pic = self.get_image()[0]
        self.image = QtGui.QPixmap(self.current_pic)
        self.image_view.setPixmap(self.image)
        self.switch_to_images()  # switch page

    def register_user(self):
        username = self.username.text()
        password = self.password_input.text()
        email = self.email.text()
        nickname = self.nickname.text()
        if username and password and email:
            data = {"username": username,
                    "password": password,
                    "email": email,
                    "full_name": nickname}
            headers = {
                'Authorization': 'Basic Og==',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json, text/plain, */*',
                'X-Requested-With': 'XMLHttpRequest',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Dest': 'empty'
            }
            response = requests.post('http://127.0.0.1:8000/create_user', headers=headers, data=data)
            if response.status_code == 200:
                if response.json().get("response") == f"user {username} has been successfully created":
                    self.switch_to_login()  # switch page

    def re_login(self):
        data = {'grant_type': 'password',
                'username': self.username,
                'password': self.password}
        headers = {
            'Authorization': 'Basic Og==',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json, text/plain, */*',
            'X-Requested-With': 'XMLHttpRequest',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty'
        }
        response = requests.post('http://127.0.0.1:8000/token', headers=headers, data=data)
        self.token = response.json().get("access_token")

    def rescan(self):
        headers = {'accept': 'application/json',
                   'Authorization': f"Bearer {self.token}"}
        response = requests.get('http://127.0.0.1:8000/get_mem_names/', headers=headers)
        if response.status_code == 200:
            with open("./cache/piclist.json", "w") as cache:
                data = response.json()
                data["index"] = 0
                json.dump(data, cache)

    def get_image(self):
        if self.pics == []:
            return
        else:
            headers = {
                'Authorization': f"Bearer {self.token}",
                'accept': 'application/json',
                'Content-Type': 'application/json',
            }
            params = {'index': str(self.pic_index)}
            data = json.dumps({"files": self.pics})
            response = requests.post('http://127.0.0.1:8000/get_mem/', headers=headers, params=params, data=data)
            if response.status_code == 200:
                with open(f"./cache/{self.pics[self.pic_index]}", "wb") as current_pic:
                    current_pic.write(response.content)
                    binary = response.content
                img = Image.open(f"./cache/{self.pics[self.pic_index]}")
                img = img.resize((919, 809), Image.ANTIALIAS)
                img.save(f"./cache/{self.pics[self.pic_index]}")
                return f"./cache/{self.pics[self.pic_index]}", binary
            elif response.status_code == 401:
                self.re_login()
                index, binary = self.get_image()
                return index, binary
            else:
                raise MinioError(f"minio error on image retrieval, status code {response.status_code}")

    def get_cached_pic_names(self):
        try:
            with open("./cache/piclist.json", "r") as data:
                return json.load(data)["pics"]
        except FileNotFoundError:
            None

    def save(self, pepe=False):
        if not pepe:
            with open(f"./saved_pics/{self.pics[self.pic_index]}", "wb") as current_pic:
                current_pic.write(self.get_image()[1])
            return f"./saved_pics/{self.pics[self.pic_index]}"
        else:
            with open(f"./pepes/{self.pics[self.pic_index]}", "wb") as current_pic:
                current_pic.write(self.get_image()[1])
            return f"./pepes/{self.pics[self.pic_index]}"

    def prev_img(self):
        if self.pic_index > 0:
            self.pic_index -= 1
        self.progressBar.setValue(self.pic_index)
        try:
            remove(self.current_pic)
        except FileNotFoundError:
            pass
        self.current_pic = self.get_image()[0]
        self.image = QtGui.QPixmap(self.current_pic)
        self.image = QtGui.QPixmap(self.get_image()[0])
        self.image_view.setPixmap(self.image)

    def next_img(self):
        if self.pic_index < len(self.pics):
            self.pic_index += 1
        self.progressBar.setValue(self.pic_index)
        try:
            remove(self.current_pic)
        except FileNotFoundError:
            pass
        self.current_pic = self.get_image()[0]
        self.image = QtGui.QPixmap(self.current_pic)
        self.image_view.setPixmap(self.image)

    def save_index(self):
        with open("./cache/piclist.json", "r") as cache:
            data = json.load(cache)
            data["index"] = self.pic_index
        with open("./cache/piclist.json", "w") as cache:
            json.dump(data, cache)

    def load_index(self):
        try:
            with open("./cache/piclist.json", "r") as data:
                return json.load(data)["index"]
        except FileNotFoundError:
            None


if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    wormchan = wormchan_app()
    wormchan.show()
    sys.exit(app.exec_())
