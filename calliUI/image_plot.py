# -*- coding: utf-8 -*-
from chaco.array_plot_data import ArrayPlotData
from chaco.data_range_1d import DataRange1D
from chaco.default_colormaps import gray
from chaco.color_mapper import ColorMapper
from chaco.plot import Plot
from chaco.tools.pan_tool import PanTool
from chaco.tools.zoom_tool import ZoomTool
import cv2 as cv
from enable.component_editor import ComponentEditor
from traits.has_traits import HasTraits, on_trait_change
from traits.trait_types import Str, Instance, Bool, Range, Enum
from traitsui.editors import RangeEditor
from traitsui.group import HGroup, VGroup
from traitsui.item import Item
from traitsui.view import View
from callimage.image_processings import edge_detection

__author__ = 'xwangan'

def my_color_map(range, **traits):
    _data =  {'red':   ((0., 1, 1), (1., 1, 1)),
              'green': ((0., 1, 1), (1., 0,0)),
              'blue':  ((0., 1, 1), (1., 0, 0))}
    return ColorMapper.from_segment_map(_data, range=range, **traits)

class ImagePlot(HasTraits):
    "The picture plot/maneuver control, including the edit (left) and plot (right) controls"
    img_name = Str
    plot = Instance(Plot)
    denoise = Bool(False)
    denoise_diameter = Range(1, 15, 7)
    inverse = Bool(False)
    binary = Bool(True) # convert to binary
    binary_threshold = Range(1, 254, 126)
    edge_detect = Bool(False)
    edge_detect_method = Enum('sobel', 'canny')
    lockon = Bool(True)

    view = View(
        HGroup(
            VGroup(
                VGroup(
                    VGroup(
                    Item('denoise', label=u"降噪", width=-50, height=-20),
                    Item('denoise_diameter',
                         label=u"滤波核",
                         editor=RangeEditor(mode="slider", high=15, low=1),
                         visible_when="denoise")
                    ),
                    Item('inverse', label=u'反色', width=-50,height=-20),
                    show_border = True
                ),
                VGroup(
                    Item("binary", label=u"二值化", width=-200),
                    Item("binary_threshold", label=u"阈值",
                         editor=RangeEditor(mode='slider', high=254, low=1),
                         visible_when="binary"),
                    show_border=True,
                ),
                VGroup(
                    Item("edge_detect", label=u"边缘检测"),
                    Item("edge_detect_method", label=u"检测方法", visible_when='edge_detect'),
                    show_border=True,
                ),
                show_border=True,
            ),
            Item('plot', editor=ComponentEditor(), show_label=False, width=600)
        ),
    )

    def __init__(self, *args, **kwargs):
        self.img_mat = None
        super(ImagePlot, self).__init__(*args, **kwargs)
        self.img_mat_orig = self.img_mat[:].copy()
        self.img_data = ArrayPlotData(img = self.img_mat[:].copy()) # img = points to the latter 'img' argument
        aspect_ratio = float(self.img_mat.shape[0])/ float(self.img_mat.shape[1])
        self.plot = Plot(self.img_data, padding=10, aspect_ratio=aspect_ratio)
        self.plot.img_plot('img', origin="bottom left", colormap=gray)
        self.plot.x_axis.visible = False
        self.plot.y_axis.visible = False
        self.image_tools()
        self.image_processing(object=None, name=None, new=None)


    def draw(self):
        self.img_data['img'] = self.img_mat[:].copy()

    @on_trait_change("denoise, denoise_diameter, inverse, binary, binary_threshold, edge_detect, edge_detect_method")
    def image_processing(self, object, name, new):

        # pts1 = np.float32([[56,65],[368,52],[28,387],[389,390]])
        # pts2 = np.float32([[0,0],[300,0],[0,300],[300,300]])
        # M = cv.getPerspectiveTransform(pts1,pts2)
        # M[2, :2] = 0.; M[:2, 2] = 0.
        # self.img_mat = cv.warpPerspective(self.img_mat_orig,M,(1000, 1000))

        self.img_mat = self.img_mat_orig.copy()
        if self.denoise:
            self.img_mat[:] = cv.bilateralFilter(self.img_mat,self.denoise_diameter,75,75)
        if self.inverse:
            self.img_mat[:] = 255 - self.img_mat
        if self.binary:
            _, self.img_mat = cv.threshold(self.img_mat.copy(),self.binary_threshold,255,cv.THRESH_BINARY)
        if self.edge_detect:
            self.img_mat = edge_detection(self.img_mat.copy(), method=self.edge_detect_method)
            if self.inverse:
                self.img_mat[:] = 255 - self.img_mat
            if self.binary:
                _, self.img_mat = cv.threshold(self.img_mat.copy(), self.binary_threshold, 255,cv.THRESH_BINARY)
            self.plot.color_mapper = my_color_map(DataRange1D(self.plot.datasources['img']))
        else:
            self.plot.color_mapper = gray(DataRange1D(self.plot.datasources['img']))
        self.draw()

    def image_tools(self):
        plot = self.plot
        plot.tools = []
        plot.overlays = []
        if self.lockon:
            plot.tools.append(PanTool(plot))
            plot.tools.append(ZoomTool(plot))
            # plot.overlays.append(DragZoom(plot,
            #                               drag_button='middle',
            #                               maintain_aspect_ratio=True,
            #                               speed=0.05))