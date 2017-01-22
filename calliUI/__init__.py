# -*- coding: utf-8 -*-
from chaco.plot_containers import OverlayPlotContainer
from enable.component_editor import ComponentEditor
import numpy as np
from traits.trait_types import Instance, Bool, List, File, Button
from traitsui.editors import ListEditor
from traitsui.group import VGroup, HGroup
from calliDB import ImageSource
from calliUI.image_plot import ImagePlot
from menu import *
from chaco.tools.broadcaster import BroadcasterTool
from chaco.tools.pan_tool import PanTool
from chaco.tools.zoom_tool import ZoomTool
# from enthought.traits.api import HasTraits, Code, Str, Int, on_trait_change
# from enthought.traits.ui.api import View, Item, Handler, CodeEditor
# from enthought.traits.ui.menu import Action, ActionGroup, Menu, MenuBar, ToolBar
# from enthought.pyface.image_resource import ImageResource

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
            plots = []
            for p in self.img_list:
                img_data = p.img_data['img'].astype("float")
                img_data[np.where(p.img_mat>127)] = np.nan
                p.img_data['img'] = img_data
                plots.append(p.plot)
            self.img_overlay = OverlayPlotContainer(*plots, bgcolor="transparent")
            broadcast = BroadcasterTool()
            for p in plots:
                tool = p.tools
                broadcast.tools += tool
                p.tools = []
                p.overlays = []
            self.img_overlay.tools.append(broadcast)
            self.edit_traits(handler=ImagesJuxtaposeHandler, view='view_overlay')
        else:
            for p in self.img_list:
                p.image_tools()
                p.draw()
            self.edit_traits(handler=ImagesJuxtaposeHandler, view='view_default')

class ImagesJuxtaposeHandler(Handler):
    def object_combine_changed(self, info):
        if  not info.initialized:
            return
        info.ui.dispose()