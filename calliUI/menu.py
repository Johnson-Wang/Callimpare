# -*- coding: utf-8 -*-
__author__ = 'xwangan'
from enthought.traits.api import HasTraits, Code, Str, Int, on_trait_change
from enthought.traits.ui.api import View, Item, Handler, CodeEditor
from enthought.traits.ui.menu import Action, ActionGroup, Menu, MenuBar, ToolBar
from enthought.pyface.image_resource import ImageResource
from os.path import join, dirname

search_path = [join(dirname(__file__), 'img')]
class MenuDemoHandler(Handler):
    def exit_app(self, info):
        info.ui.control.Close()

file_menu = Menu(
    ActionGroup(
        Action(id="open", name=u"打开", action="open_file"),
        Action(id="save", name=u"保存", action="save_file"),
    ),
    ActionGroup(
        Action(id="exit_app", name=u"退出", action="exit_app"),
    ),
    name = u"文件"
)

about_menu = Menu(
    Action(id="about", name=u"关于", action="about_dialog"),
    name = u"帮助"
)

tool_bar = ToolBar(
    Action(
        image = ImageResource("folder_page.png", search_path = search_path),
        tooltip = u"打开文档",
        action = "open_file"
    ),
    Action(
        image = ImageResource("disk.png", search_path = search_path),
        tooltip = u"保存文档",
        action = "save_file"
    ),
)

View(Item("text", style="custom", show_label=False,
         editor=CodeEditor(line="current_line")),
    menubar = MenuBar(file_menu, about_menu),
    toolbar = tool_bar,
    resizable = True,
    width = 1000, height = 800,
    title = u"Callimpare",
    handler = MenuDemoHandler()
     )

