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

    def run(self):
        canvas = self.matrix.CreateFrameCanvas()

        while True:
            canvas.Clear()
            """
            Code goes here
            """
            canvas = self.matrix.SwapOnVSync(canvas)


if __name__ == "__main__":
    commit_heatmap = CommitHeatmap()
    if (not commit_heatmap.process()):
        commit_heatmap.print_help()
