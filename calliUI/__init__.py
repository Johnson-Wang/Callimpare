# -*- coding: utf-8 -*-
from chaco.array_plot_data import ArrayPlotData
from chaco.api import gray, DataRange1D
from chaco.color_mapper import ColorMapper
from chaco.plot import Plot
from chaco.plot_containers import OverlayPlotContainer
from chaco.tools.better_selecting_zoom import BetterSelectingZoom
from chaco.tools.broadcaster import BroadcasterTool
from chaco.tools.api import PanTool, ZoomTool, DragZoom
from enable.component_editor import ComponentEditor
import numpy as np
from traitsui.api import Handler
from traits.has_traits import HasTraits, on_trait_change
from traits.trait_types import Instance, Bool, List, File, Button, Str, Enum, Range
from traitsui.editors import ListEditor, RangeEditor
from traitsui.group import VGroup, HGroup, Include
from traitsui.item import Item, UItem
from traitsui.view import View
from calliDB import ImageSource
from callimage import Graph
from callimage.image_processings import edge_detection
import cv2 as cv
from menu import *

# from enthought.traits.api import HasTraits, Code, Str, Int, on_trait_change
# from enthought.traits.ui.api import View, Item, Handler, CodeEditor
# from enthought.traits.ui.menu import Action, ActionGroup, Menu, MenuBar, ToolBar
# from enthought.pyface.image_resource import ImageResource

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


class ImageOverlay(HasTraits):
    plot = Instance(OverlayPlotContainer)
    plot1 = Instance(Plot)
    plot2 = Instance(Plot)
    choice1 = Bool(True)
    choice2 = Bool(True)
    traits_view = View(
        VGroup(
            HGroup(Item('choice1', show_label=True),
                Item('choice2', show_label=True)),
            Item('plot',editor=ComponentEditor(), show_label=False)),
        width=700, height=700, resizable=True, title="Chaco Plot")

    def _choice_fired(self):
        self.dock1 = not self.dock1

    def __init__(self, **traits):
        super(ImageOverlay, self).__init__(**traits)
        x = np.linspace(-14, 14, 300)
        y = np.sin(x) * x**3
        z = np.cos(x)
        data1 = ArrayPlotData(x=x, y=y)
        data2 = ArrayPlotData(x=x, y=z)
        plot1 = Plot(data1)
        plot2 = Plot(data2)
        plot1.plot(("x", "y"), type="line", color="blue")
        plot2.plot(("x", "y"), type="line", color="blue")
        plot = OverlayPlotContainer(plot1, plot2)
        self.plot = plot
        self.plot1 = plot1
        self.plot2 = plot2
        self.p1 = PanTool(plot1)
        self.p2 = PanTool(plot2)
        self.z1 = ZoomTool(plot1)
        self.z2 = ZoomTool(plot2)
        self.dz1 = DragZoom(plot1, drag_button='middle', maintain_aspect_ratio=True, speed=0.05)
        self.dz2 = DragZoom(plot2, drag_button='middle', maintain_aspect_ratio=True, speed=0.05)
        self.change_dock()

    @on_trait_change('choice1, choice2')
    def change_dock(self):
        plot = self.plot
        plot.tools = []
        plot.overlays = []
        if self.choice1 and (not self.choice2):
            plot.tools.append( self.p1)
            plot.tools.append( self.dz1)
            plot.overlays.append( self.z1)
        elif self.choice2 and (not self.choice1):
            plot.tools.append( self.p2)
            plot.tools.append( self.dz2)
            plot.overlays.append( self.z2)
        elif self.choice1 and self.choice2:
            broadcast = BroadcasterTool()
            broadcast.tools.append( self.p1)
            broadcast.tools.append( self.p2)
            broadcast.tools.append( self.dz1)
            broadcast.tools.append( self.dz2)
            plot.tools.append(broadcast)

class ImagesJuxtapose(HasTraits):
    img_list = List(Instance(ImagePlot))
    img_overlay = Instance(OverlayPlotContainer)
    img_file_name = File(filter=[u"*"])
    add_image_button = Button(u"添加")
    expand = Bool(False)
    combine = Bool(False)
    view_default = View(
        VGroup(
            HGroup(
                Item("img_file_name", label=u"打开图片", width=400),
                Item("add_image_button", show_label=False),
                Item("expand", label=u"展开"),
                Item("combine", label=u"合并")
            ),
            Item("img_list", style="custom", show_label=False,
                 editor=ListEditor(
                     use_notebook=True,
                     deletable=True,
                     dock_style="tab",
                     page_name=".img_name")
                )
        ),
        menubar = MenuBar(file_menu, about_menu),
        toolbar = tool_bar,
        resizable = True,
        height = 0.8,
        width = 0.8
    )
    view_overlay = View(
        VGroup(
            HGroup(
                Item("img_file_name", label=u"打开图片", width=400),
                Item("add_image_button", show_label=False),
                Item("combine", label=u"合并")
            ),
            Item("img_overlay", show_label=False,
                 editor=ComponentEditor())
        ),
        menubar = MenuBar(file_menu, about_menu),
        toolbar = tool_bar,
        resizable = True,
        height = 0.8,
        width = 0.8
    )
    traits_view = view_default

    # def default_traits_view(self):
    #     return self.view_default

    def _img_file_name_changed(self):
        self.image = ImageSource()
        self.image.load_image(self.img_file_name)
        self.add_image_button = True

    def _add_image_button_fired(self):
        if self.image != None:
            self.img_list.append(ImagePlot(img_mat = self.image.img_mat, img_name = self.image.img_name))

    def open_file(self):
        self.image = ImageSource()
        self.image.load_image(self.img_file_name)
        self.add_image_button = True

    def _combine_changed(self):
        if self.combine:
            # self.traits_view = "view_overlay"
            plots = []
            for p in self.img_list:
                p.img_mat = p.img_mat.astype("float")
                p.img_mat[np.where(p.img_mat>127)] = np.nan
                plots.append(p.plot)
                p.draw()
            self.img_overlay = OverlayPlotContainer(*plots, bgcolor="transparent")
            self.edit_traits(handler=ImagesJuxtaposeHandler, view='view_overlay')
        else:
            self.edit_traits(handler=ImagesJuxtaposeHandler, view='view_default')

class ImagesJuxtaposeHandler(Handler):
    object = Instance(ImagesJuxtapose)
    def init(self, info):
        """ Initializes the controls of a user interface.
        Overridden here to assign the 'view' trait.
        """
        self.object = info.object

    def object_combine_changed(self, info):
        if  not info.initialized:
            return
        info.ui.dispose()