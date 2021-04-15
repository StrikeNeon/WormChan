from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.label import Label
from os import mkdir, listdir, remove
import requests
import json
from tempfile import NamedTemporaryFile


class MinioError(Exception):
    pass


def build_scan(username="lain", password="cyberia"):
    data = {'grant_type': 'password',
            'username': username,
            'password': password}
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

    token = response.json().get("access_token")

    headers = {'accept': 'application/json',
               'Authorization': f"Bearer {token}"}
    response = requests.get('http://127.0.0.1:8000/get_mem_names/', headers=headers)
    if response.status_code == 200:
        with open("./cache/piclist.json", "w") as cache:
            json.dump(response.json(), cache)


class Img_Screen(BoxLayout):
    # image display
    def __init__(self, **kwargs):
        super(Img_Screen, self).__init__(**kwargs)
        self.token = self.login()
        self.errorimage = self.get_no_image()
        self.pics = self.get_cached_pic_names()
        self.pic_index = 0
        self.current_pic = self.get_image()[0]

        self.control = GridLayout()
        self.control.rows = 2
        self.control.cols = 3
        self.prev_btn = Button(text='previous')
        self.control.add_widget(self.prev_btn)
        self.prev_btn.bind(on_press=self.prev_img)

        self.rescan_btn = Button(text='rescan')
        self.control.add_widget(self.rescan_btn)
        self.rescan_btn.bind(on_press=lambda a: self.rescan())

        self.next_btn = Button(text='next')
        self.control.add_widget(self.next_btn)
        self.next_btn.bind(on_press=self.next_img)

        self.save_btn = Button(text='mark saved')
        self.control.add_widget(self.save_btn)
        self.save_btn.bind(on_press=lambda a: self.save())

        self.empty = Button(text='')
        self.control.add_widget(self.empty)

        self.save_pepe_btn = Button(text='mark pepe')
        self.control.add_widget(self.save_pepe_btn)
        self.save_pepe_btn.bind(on_press=lambda a: self.save(pepe=True))

        self.add_widget(self.control)
        # login here, save creds, time relogin
        try:
            if not self.current_pic:
                self.loaded_image = Image(source=self.errorimage.name)
                self.add_widget(self.loaded_image)
            else:
                self.loaded_image = Image(source=self.get_image()[0])
                self.add_widget(self.loaded_image)
        except MinioError:
            self.error_label = Label(text='[color=098f1a][b]Minio shat itself[/b][/color]', markup=True)
            self.add_widget(self.error_label)
        except Exception as ex:
            print(ex)

    def login(self, username="lain", password="cyberia"):
        data = {'grant_type': 'password',
                'username': 'lain',
                'password': 'cyberia'}
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
        return response.json().get("access_token")

    def rescan(self):
        headers = {'accept': 'application/json',
                   'Authorization': f"Bearer {self.token}"}
        response = requests.get('http://127.0.0.1:8000/get_mem_names/', headers=headers)
        if response.status_code == 200:
            with open("./cache/piclist.json", "w") as cache:
                json.dump(response.json(), cache)

    def callback_scan(self, instance):
        self.pics = self.rescan()

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
                return f"./cache/{self.pics[self.pic_index]}", binary
            elif response.status_code == 401:
                self.token = self.login()
                index, binary = self.get_image()
                return index, binary
            else:
                raise MinioError(f"minio error on placeholder retrieval, status code {response.status_code}")

    def get_no_image(self):
        headers = {'accept': 'application/json'}
        response = requests.get('http://127.0.0.1:8000/get_placeholder/', headers=headers)
        if response.status_code == 200:
            temp = NamedTemporaryFile(mode='w+b', dir="./cache", delete=False, suffix='.jpg')
            temp.write(response.content)
            temp.close()
            return temp
        else:
            raise MinioError(f"minio error on placeholder retrieval, status code {response.status_code}")

    def get_cached_pic_names(self):
        with open("./cache/piclist.json", "r") as data:
            return json.load(data)["pics"]

    def save(self, pepe=False):
        if not pepe:
            with open(f"./saved_pics/{self.pics[self.pic_index]}", "wb") as current_pic:
                current_pic.write(self.get_image()[1])
            return f"./saved_pics/{self.pics[self.pic_index]}"
        else:
            with open(f"./pepes/{self.pics[self.pic_index]}", "wb") as current_pic:
                current_pic.write(self.get_image()[1])
            return f"./pepes/{self.pics[self.pic_index]}"

    def prev_img(self, instance):
        if self.pic_index > 0:
            self.pic_index -= 1
        img_path = self.loaded_image.source
        self.remove_widget(self.loaded_image)
        remove(img_path)
        self.loaded_image = Image(source=self.get_image()[0])
        self.add_widget(self.loaded_image)

    def next_img(self, instance):
        if self.pic_index < len(self.pics):
            self.pic_index += 1
        img_path = self.loaded_image.source
        self.remove_widget(self.loaded_image)
        remove(img_path)
        self.loaded_image = Image(source=self.get_image()[0])
        self.add_widget(self.loaded_image)


class MemEaterCLI(App):

    def build(self):
        try:
            mkdir("./cache")
            mkdir("./saved_pics")
        except FileExistsError:
            pass
        try:
            if "piclist.json" not in listdir("./cache"):
                build_scan()
        except requests.exceptions.ConnectionError:
            print("initial caching failed")
        return Img_Screen()


if __name__ == '__main__':
    MemEaterCLI().run()
