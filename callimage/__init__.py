# -*- coding: utf-8 -*-
from matplotlib.figure import Figure
from traits.has_traits import HasTraits
from traits.trait_types import Str, Instance, List, Button
from traitsui.editors import EnumEditor, CheckListEditor
from traitsui.group import HSplit, VGroup
from traitsui.item import Item, Heading
from traitsui.view import View
from calliDB import ImageSource
from mpl_figure_editor import MPLFigureEditor

__author__ = 'xwangan'


class Graph(HasTraits):

    name = Str
    data_source = Instance(ImageSource)
    figure = Instance(Figure)
    selected_xaxis = Str
    selected_items = List

    clear_button = Button("clear")

    view = View(
        HSplit(
            VGroup(
                Item("name"),
                Item("clear_button"),
                Heading("X"),
                Item("selected_xaxis", editor=
                    EnumEditor(name="object.image.names", format_str=u"%s")),
                Heading("Y"),
                Item("selected_items", style="custom",
                     editor=CheckListEditor(name="object.image.names",
                            cols=2, format_str=u"%s")),
                show_border = True,
                scrollable = True,
                show_labels = False
            ),
            Item("figure", editor=MPLFigureEditor(), show_label=False, width=600)
        )
    )

    def _name_changed(self):
        axe = self.figure.axes[0]
        axe.set_title(self.name)
        self.figure.canvas.draw()

    def _clear_button_fired(self):
        self.selected_items = []
        self.update()

    def _figure_default(self):
        figure = Figure()
        figure.add_axes([0.1, 0.1, 0.85, 0.80])
        return figure

    def _selected_items_changed(self):
        self.update()

    def _selected_xaxis_changed(self):
        self.update()

    def update(self):
        axe = self.figure.axes[0]
        axe.clear()
        try:
            xdata = self.data_source.data[self.selected_xaxis]
        except:
            return
        for field in self.selected_items:
            axe.plot(xdata, self.data_source.data[field], label=field)
        axe.set_xlabel(self.selected_xaxis)
        axe.set_title(self.name)
        axe.legend()
        self.figure.canvas.draw()