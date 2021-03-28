#!/usr/bin/env python

from __future__ import print_function
import base64
import requests
import yaml
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from samplebase import SampleBase
import threading
import datetime
from .timing import RepeatedTimer


class CommitHeatmap(SampleBase):
    def __init__(self, *args, **kwargs):
        super(CommitHeatmap, self).__init__(*args, **kwargs)
        self.data = {}
        self.read_config("sensitive.yaml")
        self.read_config("config.yaml")
        self.color = self.data["start-color"]
        self.heatmap_flag = False

    def read_config(self, filename):
        with open(filename) as f:
            self.data.update(yaml.load(f))

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
            req = requests.post(url=url, json=query, headers=headers)
            json_object = req.json()
            led_array = np.zeros([53, 7])
        except Exception as ex:
            print(ex)

        for r, weeks in enumerate(json_object['data']['user']['contributionsCollection']['contributionCalendar']['weeks']):
            for c, days in enumerate(weeks['contributionDays']):
                led_array[r, c] = heatmap_dict[days['contributionLevel']]
        heatmap = np.transpose(led_array)
        self.generate_heatmap_image(heatmap)

    def generate_heatmap_image(self, heatmap_array):
        image = np.dstack((np.full_like(heatmap_array, self.color/6.0),np.full_like(values, 1),values))
        image = matplotlib.colors.hsv_to_rgb(image)
        image = Image.fromarray(np.uint8(image*255)).convert('RGB')
        with threading.Lock():
            self.heatmap_image = image
            self.heatmap_flag = True

    def display_time(self):
        #TODO
        pass


    def run(self):
        self.get_heatmap()
        self.heatmap_getter = RepeatedTimer(self.data["interval"], self.get_heatmap)
        canvas = self.matrix.CreateFrameCanvas()


        canvas.clear()

        while True:
            """
            Code goes here
            """
            if self.heatmap_flag:
                canvas.SetImage(self.heatmap_image,self.rows-53, self.columns-7)
                canvas = self.matrix.SwapOnVSync(canvas)
                self.heatmap_flag= False

if __name__ == "__main__":
    commit_heatmap = CommitHeatmap()

    if (not commit_heatmap.process()):
        commit_heatmap.print_help()
