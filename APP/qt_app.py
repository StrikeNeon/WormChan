import os
import requests
import json
from zipfile import ZipFile
from simplejson.errors import JSONDecodeError
from os import mkdir, remove, listdir
from os.path import basename
from PyQt5 import QtWidgets, QtWebSockets, QtGui
from PyQt5.QtCore import (
    QObject,
    pyqtSignal,
    QUrl,
)
import app_design  # design file
from PIL import Image
from loguru import logger


class MinioError(Exception):
    pass


class scrape_socket(QObject):
    finished = pyqtSignal()
    task_ready = pyqtSignal()

    def __init__(self, token, username, boards):
        super().__init__()

        self.client = QtWebSockets.QWebSocket(
            "", QtWebSockets.QWebSocketProtocol.Version13, None
        )
        self.token = token
        self.boards = boards
        self.username = username
        self.task_status = None
        self.client.error.connect(self.error)
        self.client.binaryMessageReceived.connect(self.onbinmsgreceived)
        self.client.textMessageReceived.connect(self.ontextmsgreceived)

    def start(self):
        url = QUrl(f"ws://127.0.0.1:8000/eat_mems/?token={self.token}")
        self.client.open(url)

        if self.task_status == "failed":
            self.close()

    def onbinmsgreceived(self, message):
        decoded_message = json.loads(bytes(message).decode("utf-8"))
        logger.debug(decoded_message)
        if decoded_message.get("status"):
            logger.info(f"task status: {self.status}")
            self.task_status = decoded_message.get("status")
        else:
            self.task_status = "failed"
        logger.debug("client: sending boards")
        self.client.sendBinaryMessage(json.dumps({"boards": self.boards}).encode("utf-8"))
        logger.debug({"boards": self.boards})

    def ontextmsgreceived(self, message):
        logger.debug(message)
        if message == "SUCCESS":
            self.close()
            self.task_ready.emit()
            self.finished.emit()

    def error(self, error_code):
        logger.debug(f"error code: {error_code}")
        logger.debug(self.client.errorString())

    def close(self):
        self.client.close()


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
        try:
            mkdir("cache")
            mkdir("saved_pics")
            mkdir("pepes")
        except FileExistsError:
            pass
        self.pic_index = self.load_index() if self.load_index() is not None else 0
        self.progressBar.setValue(self.pic_index)
        self.current_pic = "./cache/nothing.jpg"
        self.submit_data.clicked.connect(self.login)

        self.register_btn.clicked.connect(self.switch_to_register)

        self.send_data.clicked.connect(self.register_user)
        self.return_btn_register.clicked.connect(self.switch_to_login)

        self.rescan_btn.clicked.connect(self.rescan)
        self.previous_btn.clicked.connect(self.prev_img)
        self.next_btn.clicked.connect(self.next_img)

        self.save_btn.clicked.connect(self.save)
        self.pepe_btn.clicked.connect(lambda a: self.save(pepe=True))

        self.scrape_menu_btn.clicked.connect(self.switch_to_scrape)
        self.return_btn.clicked.connect(self.switch_to_images)

        self.remember_boards_btn.clicked.connect(self.remember_boards)
        self.scrape_command_btn.clicked.connect(self.scrape_ws)
        self.purge_unsaved_btn.clicked.connect(self.purge_unsaved)

        self.send_saved_btn.clicked.connect(self.send_saved)
        self.get_saved_btn.clicked.connect(self.get_saved)
        self.purge_saved_btn.clicked.connect(self.purge_saved)

        self.send_pepes_btn.clicked.connect(self.send_pepes)
        self.get_pepes_btn.clicked.connect(self.get_pepes)
        self.purge_pepes_btn.clicked.connect(self.purge_pepes)

    def set_states(self):
        return {
            "asp": self.asp_checkbox.isChecked(),
            "vm": self.vm_checkbox.isChecked(),
            "b": self.b_checkbox.isChecked(),
            "x": self.x_checkbox.isChecked(),
            "vrpg": self.vrpg_checkbox.isChecked(),
            "vip": self.vip_checkbox.isChecked(),
            "lgbt": self.lgbt_checkbox.isChecked(),
            "biz": self.biz_checkbox.isChecked(),
            "co": self.co_checkbox.isChecked(),
            "an": self.an_checkbox.isChecked(),
            "int": self.int_checkbox.isChecked(),
            "fit": self.fit_checkbox.isChecked(),
            "mlp": self.mlp_checkbox.isChecked(),
            "p": self.p_checkbox.isChecked(),
            "ck": self.ck_checkbox.isChecked(),
            "tvr": self.tvr_checkbox.isChecked(),
            "his": self.his_checkbox.isChecked(),
            "tv": self.tv_checkbox.isChecked(),
            "a": self.a_checkbox.isChecked(),
            "qst": self.qst_checkbox.isChecked(),
            "news": self.news_checkbox.isChecked(),
            "tg": self.tg_checkbox.isChecked(),
            "wsr": self.wsr_checkbox.isChecked(),
            "o": self.o_checkbox.isChecked(),
            "gd": self.gd_checkbox.isChecked(),
            "diy": self.diy_checkbox.isChecked(),
            "jp": self.jp_checkbox.isChecked(),
            "v": self.v_checkbox.isChecked(),
            "sp": self.sp_checkbox.isChecked(),
            "s4s": self.s4s_checkbox.isChecked(),
            "fa": self.fa_checkbox.isChecked(),
            "mu": self.mu_checkbox.isChecked(),
            "m": self.m_checkbox.isChecked(),
            "out": self.out_checkbox.isChecked(),
            "vmg": self.vmg_checkbox.isChecked(),
            "g": self.g_checkbox.isChecked(),
            "lit": self.lit_checkbox.isChecked(),
            "n": self.n_checkbox.isChecked(),
            "vr": self.vr_checkbox.isChecked(),
            "cgi": self.cgi_checkbox.isChecked(),
            "vst": self.vst_checkbox.isChecked(),
        }

    def closeEvent(self, event):
        logger.info("exiting")
        self.save_index()
        event.accept()  # let the window close

    def switch_to_login(self):
        self.app_pages.setCurrentIndex(0)

    def switch_to_images(self):
        self.app_pages.setCurrentIndex(1)

    def switch_to_scrape(self):
        self.app_pages.setCurrentIndex(2)

    def switch_to_register(self):
        self.app_pages.setCurrentIndex(3)

    def login(self):
        self.username = self.login_input.text()
        self.password = self.password_input.text()
        data = {
            "grant_type": "password",
            "username": self.username,
            "password": self.password,
        }
        headers = {
            "Authorization": "Basic Og==",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json, text/plain, */*",
            "X-Requested-With": "XMLHttpRequest",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
        }
        response = requests.post(
            "http://127.0.0.1:8000/token", headers=headers, data=data
        )
        logger.debug(f"{response.status_code}")
        if response.status_code == 401:
            logger.error("access denied")
            return
        if response.status_code == 404:
            logger.critical("error loggin in, 404, contact the admin and tell him to unblomck port)")
            return
        try:
            self.token = response.json().get("access_token")
            self.pics = self.get_cached_pic_names()
            if not self.pics:
                self.rescan()
                self.pics = self.get_cached_pic_names()
            self.progressBar.setMaximum(len(self.pics))
            try:
                self.current_pic = self.get_image()[0]
                self.image = QtGui.QPixmap(self.current_pic)
                self.image_view.setPixmap(self.image)
                self.switch_to_images()  # switch page
            except Exception as ex:
                logger.error(ex)
                self.current_pic = "./cache/nothing.jpg"
                self.image = QtGui.QPixmap(self.current_pic)
                self.image_view.setPixmap(self.image)
                self.switch_to_images()  # switch page
        except JSONDecodeError:
            logger.error("no access token recieved")
            return

    def register_user(self):
        username = self.username_field.text()
        password = self.password_field.text()
        email = self.email_field.text()
        nickname = self.nickname_field.text()
        if username and password and email:
            data = {
                "username": username,
                "password": password,
                "email": email,
                "full_name": nickname,
            }
            headers = {
                "Authorization": "Basic Og==",
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json, text/plain, */*",
                "X-Requested-With": "XMLHttpRequest",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Dest": "empty",
            }
            response = requests.post(
                "http://127.0.0.1:8000/users/create_user", headers=headers, data=data
            )
            if response.status_code == 200:
                self.switch_to_login()  # switch page

    def re_login(self):
        data = {
            "grant_type": "password",
            "username": self.username,
            "password": self.password,
        }
        headers = {
            "Authorization": "Basic Og==",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json, text/plain, */*",
            "X-Requested-With": "XMLHttpRequest",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
        }
        response = requests.post(
            "http://127.0.0.1:8000/token", headers=headers, data=data
        )
        self.token = response.json().get("access_token")

    def rescan(self):
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {self.token}",
        }
        response = requests.get("http://127.0.0.1:8000/get_mem_names/", headers=headers)
        if response.status_code == 200:
            with open("./cache/piclist.json", "w") as cache:
                data = response.json()
                data["index"] = 0
                json.dump(data, cache)
                self.pic_index = 0
                try:
                    self.current_pic = self.get_image()[0]
                    return 0
                except TypeError:
                    self.current_pic = "./cache/nothing.jpg"
        elif response.status_code == 401:
            if self.re_login():
                return self.rescan()
            else:
                return 401

    def get_image(self):
        if self.pics == []:
            return
        else:
            headers = {
                "Authorization": f"Bearer {self.token}",
                "accept": "application/json",
                "Content-Type": "application/json",
            }
            params = {"index": self.pic_index}
            data = json.dumps({"files": self.pics})
            try:
                response = requests.post(
                    "http://127.0.0.1:8000/get_mem/",
                    headers=headers,
                    params=params,
                    data=data,
                )
                if response.status_code == 200:
                    with open(f"./cache/{self.pics[self.pic_index]}", "wb") as current_pic:
                        current_pic.write(response.content)
                        binary = response.content
                    try:
                        img = Image.open(f"./cache/{self.pics[self.pic_index]}")
                    except Image.UnidentifiedImageError:
                        img = Image.open("./cache/nothing.jpg")
                    img = img.resize(
                                    (self.image_view.width(),
                                    self.image_view.height()),
                                    Image.ANTIALIAS
                                    )
                    img.save(f"./cache/{self.pics[self.pic_index]}")
                    return f"./cache/{self.pics[self.pic_index]}", binary
                elif response.status_code == 401:
                    self.re_login()
                    index, binary = self.get_image()
                    return index, binary
                else:
                    raise MinioError(
                        f"minio error on image retrieval, status code {response.status_code}"
                    )
            except requests.exceptions.ConnectionError:
                return "./cache/nothing.jpg"

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
            try:
                with open(f"./pepes/{self.pics[self.pic_index]}", "wb") as current_pic:
                    current_pic.write(self.get_image()[1])
                return f"./pepes/{self.pics[self.pic_index]}"
            except IndexError:
                return

    def prev_img(self):
        if self.pic_index > 0:
            self.pic_index -= 1
        self.progressBar.setValue(self.pic_index)
        try:
            remove(self.current_pic)
        except FileNotFoundError:
            pass
        try:
            self.current_pic = self.get_image()[0]
        except MinioError:
            self.current_pic = "./cache/nothing.jpg"
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
        try:
            self.current_pic = self.get_image()[0]
        except MinioError:
            self.current_pic = "./cache/nothing.jpg"
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

    def remember_boards(self):
        headers = {
            "Authorization": f"Bearer {self.token}",
            "accept": "application/json",
            "Content-Type": "application/json",
        }
        data = {
            "boards": [key for key, value in self.set_states().items() if value is True]
        }
        if data.get("boards") != []:
            response = requests.post(
                "http://127.0.0.1:8000/users/set_relevants/",
                headers=headers,
                data=json.dumps(data),
            )
            if response.status_code == 200:
                self.rescan()
                return 0
            elif response.status_code == 401:
                if self.re_login():
                    return self.remember_boards()
                else:
                    return 401
        return 0

    def scrape_ws(self):
        self.socket = scrape_socket(self.token, self.username,
                                    [key for key, value in
                                     self.set_states().items()
                                     if value is True])
        self.socket.task_ready.connect(self.rescan)
        self.socket.start()

    def purge_unsaved(self):
        headers = {
            "Authorization": f"Bearer {self.token}",
            "accept": "application/json",
            "Content-Type": "application/json",
        }
        response = requests.get("http://127.0.0.1:8000/purge_unsaved/", headers=headers)
        if response.status_code == 200:
            self.rescan()
            self.current_pic = "./cache/nothing.jpg"
            return 0
        elif response.status_code == 401:
            if self.re_login():
                return self.purge_unsaved()
            else:
                return 401

    def zip_files(self, dest: str):
        file_paths = listdir(f"./{dest}")
        if len(file_paths) != 0:
            with ZipFile(f'./{dest}/{self.username}_arch_{dest}.zip', 'w') as zip_file:
                # writing each file one by one
                while len(file_paths) != 0:
                    file = file_paths.pop()
                    if ".zip" not in file:
                        file_path = f"./{dest}/{file}"
                        zip_file.write(file_path, basename(file_path))
                        remove(file_path)
            return f'./{dest}/{self.username}_arch_{dest}.zip'

    def extract_files(self, dest: str):
        file_paths = listdir(f"./{dest}")
        if f"{self.username}_arch_{dest}.zip" in file_paths:
            with ZipFile(f'./{dest}/{self.username}_arch_{dest}.zip', 'r') as zip_file:
                zip_file.extractall(f"./{dest}")
            remove(f'./{dest}/{self.username}_arch_{dest}.zip')
            return 0
        else:
            logger.error("No saved files were found")

    def send_saved(self):
        saved_archive = self.zip_files("saved_pics")
        files = {'zipfile': (f'{self.username}_arch_saved_pics.zip', open(saved_archive, 'rb').read(), 'application/zip')}
        headers = {
            "Authorization": f"Bearer {self.token}",
            "accept": "application/json",
        }
        response = requests.post("http://127.0.0.1:8000/get_saved/", headers=headers, files=files)
        if response.status_code == 200:
            return 0
        elif response.status_code == 401:
            if self.re_login():
                return self.send_pepes()
            else:
                return 401

    def purge_saved(self):
        headers = {
            "Authorization": f"Bearer {self.token}",
            "accept": "application/json",
            "Content-Type": "application/json",
        }
        response = requests.get("http://127.0.0.1:8000/purge_saved/", headers=headers)
        if response.status_code == 200:
            return 0
        elif response.status_code == 401:
            if self.re_login():
                return self.purge_saved()
            else:
                return 401

    def get_saved(self):
        headers = {
            "Authorization": f"Bearer {self.token}",
            "accept": "application/zip",
            "Content-Type": "application/json",
        }
        response = requests.get("http://127.0.0.1:8000/send_saved/", headers=headers)
        if response.status_code == 200:
            with open(f'./saved_pics/{self.username}_arch_saved_pics.zip', "wb") as archive:
                archive.write(response.content)
            self.extract_files("saved_pics")
            return 0
        elif response.status_code == 401:
            if self.re_login():
                return self.get_pepes()
            else:
                return 401

    def send_pepes(self):
        pepe_archive = self.zip_files("pepes")
        files = {'zipfile': (f'{self.username}_arch_pepes.zip', open(pepe_archive, 'rb').read(), 'application/zip')}
        statinfo = os.stat(pepe_archive).st_size
        headers = {
            "Authorization": f"Bearer {self.token}",
            "accept": "application/json",
            "Content-Length": str(statinfo)
        }
        response = requests.post("http://127.0.0.1:8000/get_pepes/", headers=headers, files=files)
        if response.status_code == 200:
            return 0
        elif response.status_code == 401:
            if self.re_login():
                return self.send_pepes()
            else:
                return 401

    def purge_pepes(self):
        headers = {
            "Authorization": f"Bearer {self.token}",
            "accept": "application/json",
            "Content-Type": "application/json",
        }
        response = requests.get("http://127.0.0.1:8000/purge_pepes/", headers=headers)
        if response.status_code == 200:
            return 0
        elif response.status_code == 401:
            if self.re_login():
                return self.purge_pepes()
            else:
                return 401

    def get_pepes(self):
        headers = {
            "Authorization": f"Bearer {self.token}",
            "accept": "application/zip",
            "Content-Type": "application/json",
        }
        response = requests.get("http://127.0.0.1:8000/send_pepes/", headers=headers)
        if response.status_code == 200:
            with open(f'./pepes/{self.username}_arch_pepes.zip', "wb") as archive:
                archive.write(response.content)
            self.extract_files("pepes")
            return 0
        elif response.status_code == 401:
            if self.re_login():
                return self.get_pepes()
            else:
                return 401
