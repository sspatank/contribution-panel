#!/usr/bin/env python

from __future__ import print_function
import base64
import requests
import json
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from samplebase import SampleBase


class CommitHeatmap(SampleBase):
    def __init__(self, *args, **kwargs):
        super(CommitHeatmap, self).__init__(*args, **kwargs)
        self.data = {}
        self.read_config("sensitive.json")
        self.read_config("config.json")

    def read_config(self, filename):
        with open(filename) as f:
            self.data.update(json.load(f))

    def get_heatmap(self):
        heatmap_dict = {
                'NONE':            0.0,
                'FIRST_QUARTILE':  0.25,
                'SECOND_QUARTILE': 0.5,
                'THIRD_QUARTILE':  0.75,
                'FOURTH_QUARTILE': 1.0
                    }
        url = 'https://api.github.com/graphql'
        query = {'query': '{ viewer { login } user(login: "%s") { id contributionsCollection { contributionCalendar { totalContributions weeks { contributionDays { color contributionLevel date weekday } firstDay } } } } }' % self.data['subject-username'] }
        headers = {'Authorization': 'token %s' % self.data['api-token']}
        req = requests.post(url=url, json=query, headers=headers)
        json_object = req.json()
        led_array = np.zeros([53, 7])

        for r, weeks in enumerate(json_object['data']['user']['contributionsCollection']['contributionCalendar']['weeks']):
            for c, days in enumerate(weeks['contributionDays']):
                led_array[r, c] = heatmap_dict[days['contributionLevel']]
        self.heatmap = np.transpose(led_array)

    def dark_mode_selector(self, background):
        # TODO
        light_colormap_dict = {
                'green': ,
                'red': ,
                'white': ,
                'blue': ,
                'purple',
                'orange'
                              }
        dark_colormap_dict = {
                'green': ,
                'red': ,
                'white': ,
                'blue': ,
                'purple': ,
                'orange':
                             }
        if background == "light":
            self.colormap_dict = light_colomap_dict
        elif background = "dark":
            self.colormap_dict = dark_colormap_dict

    def color_selector(self, color):
        self.colormap = dark_colormap_dict[color]

    def generate_heatmap_image(self):
        #TODO
        pass

    def display_time(self):
        #TODO
        pass

    def update_screen(self):
        """
        This should populate a canvas with the latest data
        """
        #TODO
        pass


    def run(self):
        canvas = self.matrix.CreateFrameCanvas()

        self.get_heatmap()
        while True:
            canvas.Clear()
            """
            Code goes here
            """
            # canvas = self.matrix.SwapOnVSync(canvas)


if __name__ == "__main__":
    commit_heatmap = CommitHeatmap()
    commit_heatmap.get_heatmap()
    """
    if (not commit_heatmap.process()):
        commit_heatmap.print_help()
    """
