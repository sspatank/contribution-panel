#!/usr/bin/env python3

from __future__ import print_function
import base64
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import yaml
import numpy as np
import matplotlib
from PIL import Image
from samplebase import SampleBase
from rgbmatrix import graphics
import threading
import datetime
import time
from timing import RepeatedTimer
import sys
import os

class CommitHeatmap(SampleBase):
    def __init__(self, *args, **kwargs):
        super(CommitHeatmap, self).__init__(*args, **kwargs)
        self.data = {}
        self.current_path = os.path.dirname(os.path.abspath(__file__))
        self.read_config(os.path.join(self.current_path, "sensitive.yaml"))
        self.read_config(os.path.join(self.current_path, "config.yaml"))
        self.color = self.data['start-color']
        
        self.update_flag = False
        self.font_file = os.path.join(self.current_path, "..", "rpi-rgb-led-matrix/fonts/4x6.bdf")
        self.font = graphics.Font()
        self.font.LoadFont(self.font_file)
        clock_color = [int(255*x) for x in matplotlib.colors.hsv_to_rgb([4/6.0,1.0,1])]
        self.text_color = graphics.Color(clock_color[0], clock_color[1], clock_color[2])
        
        self.parser.set_defaults(led_rows=self.data['rows'])
        self.parser.set_defaults(led_cols=self.data['columns'])
        self.parser.set_defaults(led_chain=self.data['chain-length'])
        self.parser.set_defaults(led_parallel=self.data['parallel-chains'])
        self.parser.set_defaults(led_gpio_mapping=self.data['hardware-mapping'])

    def read_config(self, filename):
        with open(filename) as f:
            self.data.update(yaml.safe_load(f))

    def get_heatmap(self):
        heatmap_dict =  {
                'NONE':            0.0,
                'FIRST_QUARTILE':  0.25,
                'SECOND_QUARTILE': 0.5,
                'THIRD_QUARTILE':  0.75,
                'FOURTH_QUARTILE': 1.0
                        }
        url = 'https://api.github.com/graphql'
        query = {'query': '{ viewer { login } user(login: "%s") { id contributionsCollection { contributionCalendar { totalContributions weeks { contributionDays { color contributionLevel date weekday } firstDay } } } } }' % self.data['username'] }
        headers = {'Authorization': 'token %s' % self.data['api-token']}
        try:
            session = requests.Session()
            retry = Retry(connect=3, backoff_factor=0.5)
            adapter = HTTPAdapter(max_retries=retry)
            session.mount('http://',adapter)
            session.mount('https://', adapter)
            req = session.post(url=url, json=query, headers=headers)
            json_object = req.json()
            led_array = np.zeros([53, 7])

            for r, weeks in enumerate(json_object['data']['user']['contributionsCollection']['contributionCalendar']['weeks']):
                for c, days in enumerate(weeks['contributionDays']):
                    led_array[r, c] = heatmap_dict[days['contributionLevel']]
            heatmap = np.transpose(led_array)
            self.generate_heatmap_image(heatmap)
        except requests.exceptions.ConnectionError:
            time.sleep(5)
            pass
        except Exception as ex:
            print(ex)

    def generate_heatmap_image(self, heatmap_array):
        image = np.dstack((np.full_like(heatmap_array, self.color/6.0),np.full_like(heatmap_array, 1),heatmap_array))
        image = matplotlib.colors.hsv_to_rgb(image)
        image = Image.fromarray(np.uint8(image*255)).convert('RGB')
        with threading.Lock():
            self.heatmap_image = image
            self.update_flag = True

    def get_time(self):
        with threading.Lock():
            self.current_time = datetime.datetime.now().strftime("%H%M %a,%-d %b")
            self.update_flag = True

    def run(self):
        canvas = None
        try:
            self.get_time()
            self.get_heatmap()
            self.time_getter = RepeatedTimer(1, self.get_time)
            self.heatmap_getter = RepeatedTimer(self.data["heatmap-interval"], self.get_heatmap)
            canvas = self.matrix.CreateFrameCanvas()
            canvas.Clear()

            while True:
                if self.update_flag:
                    canvas.Clear()
                    canvas.SetImage(self.heatmap_image, int((self.matrix.width-53)/2), self.matrix.height-7, unsafe=False)
                    graphics.DrawText(canvas, self.font, 2, 6, self.text_color, self.current_time)
                    self.update_flag = False
                    canvas = self.matrix.SwapOnVSync(canvas)
        except Exception as ex:
            if canvas is not None:
                canvas.Clear()
            print(ex)
            sys.exit()


if __name__ == "__main__":
    commit_heatmap = CommitHeatmap()

    if (not commit_heatmap.process()):
        commit_heatmap.print_help()
