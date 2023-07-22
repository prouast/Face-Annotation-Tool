#!/usr/bin/env python
"""
Facial landmark annotation tool

This program expects either a single image as an argument, or a directory
with many images, and a number n of images to be processed in that directory.
In this last case, names are sorted, and images at positions 0, floor(N/n),
floor(2N/n), ... floor((n - 1)N/n) are selected.

Output is to stdout and follows a csv format:
  'image_fname,' +
  'leye_x,leye_y,reye_x,reye_y,nose_x,nose_y, ' +
  'lmouth_x,lmouth_y,rmouth_x,rmouth_y,' +
  'rect_top_x,rect_top_y,rect_width,rect_height'

It is not necessary to annotate all points, and images can be skipped when
in multiple image mode.

Run without arguments for usage information.
"""
from __future__ import print_function
from __future__ import division
import os
import argparse
import warnings

import cv2
from matplotlib import pyplot as plt
from matplotlib.widgets import Button
import matplotlib.cbook
warnings.filterwarnings('ignore', category=matplotlib.cbook.mplDeprecation)

def enum(**enums):
    return type('Enum', (), enums)


class InteractiveViewer(object):
    def __init__(self, img_path):
        self.img_path = img_path
        self.key_pressed = False
        self.key_event = None
        self.rect_clicked = False

        self.rect_coords = [(0, 0), (0, 0)]
        self.leye_coords = None
        self.reye_coords = None
        self.nose_coords = None
        self.lmouth_coords = None
        self.rmouth_coords = None
        
        self.image = cv2.imread(img_path)
        self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        self.clone = self.image.copy()

        self.fig = None
        self.im_ax = None

        self.button_rect = None
        self.button_leye = None
        self.button_reye = None
        self.button_nose = None
        self.button_lmouth = None
        self.button_rmouth = None

        self.button_done = None

        self.button_skip = None

        self.is_finished = False
        self.is_skipped = False
        self.repeat = False

        self.States = enum(GET_RECT=1,
                           GET_LEYE=2,
                           GET_REYE=3,
                           GET_NOSE=4,
                           GET_LMOUTH=5,
                           GET_RMOUTH=6)

        self.curr_state = self.States.GET_RECT


    def redraw_annotations(self):
        self.image = self.clone.copy()

        cv2.rectangle(self.image, self.rect_coords[0], self.rect_coords[1],
                      (0, 255, 0), 1)
        if self.leye_coords is not None:
            cv2.circle(self.image, self.leye_coords, 5, (255, 0, 0), -1)
        if self.reye_coords is not None:
            cv2.circle(self.image, self.reye_coords, 5, (255, 0, 0), -1)
        if self.nose_coords is not None:
            cv2.circle(self.image, self.nose_coords, 5, (255, 0, 0), -1)
        if self.lmouth_coords is not None:
            cv2.circle(self.image, self.lmouth_coords, 5, (255, 0, 0), -1)
        if self.rmouth_coords is not None:
            cv2.circle(self.image, self.rmouth_coords, 5, (255, 0, 0), -1)

        self.im_ax.imshow(self.image)


    def update_button_labels(self):
        self.button_rect.label.set_text('Rectangle\n({},{})'.format(
            self.rect_coords[0], self.rect_coords[1]))

        self.button_leye.label.set_text(
            'Left Eye\n{}'.format(self.leye_coords))
        self.button_reye.label.set_text(
            'Right Eye\n{}'.format(self.reye_coords))
        self.button_nose.label.set_text(
            'Nose\n{}'.format(self.nose_coords))
        self.button_lmouth.label.set_text(
            'Left Mouth\n{}'.format(self.lmouth_coords))
        self.button_rmouth.label.set_text(
            'Right Mouth \n{}'.format(self.rmouth_coords))


    def on_click(self, event):
        if event.inaxes != self.im_ax:
            return

        self.rect_clicked = False

        if self.curr_state == self.States.GET_RECT:
            self.rect_coords[0] = (int(event.xdata), int(event.ydata))
            self.rect_clicked = True

        elif self.curr_state == self.States.GET_LEYE:
            self.leye_coords = (int(event.xdata), int(event.ydata))
            self.button_leye.label.set_text(
                'Left Eye\n{}'.format(self.leye_coords))
            #self.redraw_annotations()

        elif self.curr_state == self.States.GET_REYE:
            self.reye_coords = (int(event.xdata), int(event.ydata))
            self.reye_coords = (int(event.xdata), int(event.ydata))
            self.button_reye.label.set_text(
                'Right Eye\n{}'.format(self.reye_coords))
            #self.redraw_annotations()

        elif self.curr_state == self.States.GET_NOSE:
            self.nose_coords = (int(event.xdata), int(event.ydata))
            self.nose_coords = (int(event.xdata), int(event.ydata))
            self.button_nose.label.set_text(
                'Nose\n{}'.format(self.nose_coords))
            #self.redraw_annotations()

        elif self.curr_state == self.States.GET_LMOUTH:
            self.lmouth_coords = (int(event.xdata), int(event.ydata))
            self.lmouth_coords = (int(event.xdata), int(event.ydata))
            self.button_lmouth.label.set_text(
                'Left Mouth\n{}'.format(self.lmouth_coords))
            #self.redraw_annotations()

        elif self.curr_state == self.States.GET_RMOUTH:
            self.rmouth_coords = (int(event.xdata), int(event.ydata))
            self.rmouth_coords = (int(event.xdata), int(event.ydata))
            self.button_rmouth.label.set_text(
                'Right Mouth\n{}'.format(self.rmouth_coords))
            #self.redraw_annotations()


    def on_release(self, event):
        if event.inaxes != self.im_ax:
            return

        self.rect_clicked = False

        if self.curr_state == self.States.GET_RECT:
            self.rect_coords[1] = (int(event.xdata), int(event.ydata))

            cv2.rectangle(self.image, self.rect_coords[0], self.rect_coords[1],
                          (0, 255, 0), 1)

            self.button_rect.label.set_text('Rectangle\n({},{})'.format(
                self.rect_coords[0], self.rect_coords[1]))


            self.im_ax.imshow(self.image)


    def on_key_press(self, event):
        self.key_event = event
        self.key_pressed = True


    def on_mouse_move(self, event):
        if not self.rect_clicked or event.inaxes != self.im_ax:
            return

        self.rect_coords[1] = (int(event.xdata), int(event.ydata))
        #self.redraw_annotations()


    def connect(self):
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        self.fig.canvas.mpl_connect('key_press_event', self.on_key_press)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)


    def button_event(self, event):
        self.key_pressed = False

        if event.inaxes == self.button_rect.ax:
            self.rect_coords = [(0, 0), (0, 0)]
            self.curr_state = self.States.GET_RECT

        elif event.inaxes == self.button_leye.ax:
            self.leye_coords = None
            self.curr_state = self.States.GET_LEYE

        elif event.inaxes == self.button_reye.ax:
            self.reye_coords = None
            self.curr_state = self.States.GET_REYE

        elif event.inaxes == self.button_nose.ax:
            self.nose_coords = None
            self.curr_state = self.States.GET_NOSE

        elif event.inaxes == self.button_lmouth.ax:
            self.lmouth_coords = None
            self.curr_state = self.States.GET_LMOUTH

        elif event.inaxes == self.button_rmouth.ax:
            self.rmouth_coords = None
            self.curr_state = self.States.GET_RMOUTH

        elif event.inaxes == self.button_done.ax:
            self.is_finished = True

        elif event.inaxes == self.button_skip.ax:
            #self.is_skipped = True
            # Do another face
            self.repeat = True

        #self.redraw_annotations()
        self.update_button_labels()


    def init_subplots(self):
        self.fig = plt.figure(os.path.basename(self.img_path))

        self.im_ax = self.fig.add_subplot(1, 5, (1, 4))
        self.im_ax.set_title('Input')
        self.im_ax.imshow(self.image, interpolation='nearest')

        self.button_rect = Button(plt.axes([0.8, 0.8, 0.15, 0.09]),
                                  'Rectangle ()')
        self.button_rect.on_clicked(self.button_event)

        self.button_leye = Button(plt.axes([0.8, 0.7, 0.15, 0.09]),
                                  'Left eye ()')
        self.button_leye.on_clicked(self.button_event)

        self.button_reye = Button(plt.axes([0.8, 0.6, 0.15, 0.09]),
                                  'Right eye ()')
        self.button_reye.on_clicked(self.button_event)

        self.button_nose = Button(plt.axes([0.8, 0.5, 0.15, 0.09]),
                                  'Nose ()')
        self.button_nose.on_clicked(self.button_event)

        self.button_lmouth = Button(plt.axes([0.8, 0.4, 0.15, 0.09]),
                                    'Left mouth ()')
        self.button_lmouth.on_clicked(self.button_event)

        self.button_rmouth = Button(plt.axes([0.8, 0.3, 0.15, 0.09]),
                                    'Right mouth ()')
        self.button_rmouth.on_clicked(self.button_event)

        self.button_done = Button(plt.axes([0.8, 0.15, 0.15, 0.05]),
                                  'Done')
        self.button_done.on_clicked(self.button_event)

        self.button_skip = Button(plt.axes([0.8, 0.09, 0.15, 0.05]),
                                  'Another')
        self.button_skip.on_clicked(self.button_event)

        self.update_button_labels()


    def fill_default_coords(self):
        if self.leye_coords is None:
            self.leye_coords = (-1, -1)
        if self.reye_coords is None:
            self.reye_coords = (-1, -1)
        if self.nose_coords is None:
            self.nose_coords = (-1, -1)
        if self.lmouth_coords is None:
            self.lmouth_coords = (-1, -1)
        if self.rmouth_coords is None:
            self.rmouth_coords = (-1, -1)


    def save_annotations(self):
        self.fill_default_coords()
        f_winner.write('{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11},{12},{13},{14},{15},{16}\n'.format(
                  "0",os.path.basename(self.img_path),"1.0",
                  self.rect_coords[0][0], self.rect_coords[0][1],
                  self.rect_coords[1][0], self.rect_coords[1][1],
                  self.leye_coords[0], self.leye_coords[1],
                  self.reye_coords[0], self.reye_coords[1],
                  self.nose_coords[0], self.nose_coords[1],
                  self.lmouth_coords[0], self.lmouth_coords[1],
                  self.rmouth_coords[0], self.rmouth_coords[1]))
        f_winner.flush()
        print('{0},{1},{2},{3},{4},{5},{6},{7},{8}'
              ',{9},{10},{11},{12},{13},{14}'.format(
                  os.path.basename(self.img_path),
                  self.rect_coords[0][0], self.rect_coords[0][1],
                  self.rect_coords[1][0], self.rect_coords[1][1],
                  self.leye_coords[0], self.leye_coords[1],
                  self.reye_coords[0], self.reye_coords[1],
                  self.nose_coords[0], self.nose_coords[1],
                  self.lmouth_coords[0], self.lmouth_coords[1],
                  self.rmouth_coords[0], self.rmouth_coords[1]))


    def run(self):
        self.init_subplots()
        self.connect()

        while True:
            # Wait for output, and 'update' figure
            plt.pause(0.03)

            # Exit
            if (self.is_finished
                    or (self.key_pressed and self.key_event.key == 'q')
                    or self.is_skipped or self.repeat):
                break

        plt.close()
        self.save_annotations()
        if self.is_finished:
            return 0 # finished normally
        elif self.is_skipped:
            return 0
        elif self.repeat:
            return 2
        else:
            return 1 # aborted (pressed 'q')

import re
def sorted_alphanumeric(data):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
    return sorted(data, key=alphanum_key)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Annotate one or more face images. Output to stdout.')
    base_group = parser.add_mutually_exclusive_group()
    base_group.add_argument('-d', '--dirimgs', type=str,
                            help='dir with images')
    base_group.add_argument('-i', '--img', type=str,
                            help='single image')
    parser.add_argument('-n', '--nimgs', type=int,
                        help='number of images for -d mode', default=1)

    args = parser.parse_args()
    if args.dirimgs is None and args.img is None:
        parser.print_help()

    return args


def main(args):
    if args.dirimgs is not None:
        flist = sorted_alphanumeric(os.listdir(args.dirimgs))
        #flist = sorted(os.listdir(args.dirimgs))
        print('image_fname,rect_x0,rect_y0,rect_x1,rect_y1,leye_x,leye_y,reye_x,reye_y,nose_x,nose_y,'
              'lmouth_x,lmouth_y,rmouth_x,rmouth_y,')

        for curr_file in flist:#[::len(flist) // args.nimgs][:args.nimgs]:
            img_path = os.path.join(args.dirimgs, curr_file)
            if "DS_Store" in img_path:
                continue
            done = False
            ret = 0
            while not done:
                viewer = InteractiveViewer(img_path)
                ret = viewer.run()
                if ret != 2:
                    done = True
            if ret == 1:
                break
            else:
                continue

    elif args.img is not None:
        print('image_fname,rect_x0,rect_y0,rect_x1,rect_y1,leye_x,leye_y,reye_x,reye_y,nose_x,nose_y,'
              'lmouth_x,lmouth_y,rmouth_x,rmouth_y,')

        img_path = args.img
        viewer = InteractiveViewer(img_path)
        viewer.run()


if __name__ == '__main__':
    f_winner = open('landmark_output.csv', 'a')
    main(parse_arguments())
    f_winner.close()
