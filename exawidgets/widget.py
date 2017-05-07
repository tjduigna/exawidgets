# -*- coding: utf-8 -*-
# Copyright (c) 2015-2016, Exa Analytics Development Team
# Distributed under the terms of the Apache License 2.0
"""
Widget
##################
Functionality for using Jupyter notebook extensions to visualize data speficic
containers. This module requires the infrastructure provided by the `traitlets`_
and `ipywidgets`_ packages.

.. _traitlets: https://traitlets.readthedocs.io/en/stable/
.. _ipywidgets: https://ipywidgets.readthedocs.io/en/latest/
"""
from ipywidgets import (DOMWidget, Box, VBox, HBox, Dropdown, Widget, SelectMultiple,
                        Layout, Button, widget_serialization, register)
from traitlets import Unicode, Integer, Bool, List, Instance

display_params = {
    'savedir': '',
    'filename': '',
}

@register("exawidgets.BaseDOM")
class BaseDOM(DOMWidget):
    _view_module = Unicode("jupyter-exawidgets").tag(sync=True)
    _model_module = Unicode("jupyter-exawidgets").tag(sync=True)
    _model_name = Unicode("BaseDOMModel").tag(sync=True)
    _view_name = Unicode("BaseDOMView").tag(sync=True)
    background = Unicode("green").tag(sync=True)

    def __init__(self, *args, layout=None, **kwargs):
        if layout is None: layout = Layout(width="600", height="450")
        super(BaseDOM, self).__init__(*args, layout=layout, **kwargs)


@register("exawidgets.BaseData")
class BaseData(Widget):
    _view_module = Unicode("jupyter-exawidgets").tag(sync=True)
    _model_module = Unicode("jupyter-exawidgets").tag(sync=True)
    _model_name = Unicode("BaseDataModel").tag(sync=True)
    _view_name = Unicode("BaseDataView").tag(sync=True)
    datars = List([0, 1, 2, 3]).tag(sync=True)


@register("exawidgets.ContainerWidget")
class ContainerWidget(BaseDOM):
    _model_name = Unicode("ContainerModel").tag(sync=True)
    _view_name = Unicode("ContainerView").tag(sync=True)
    clear = Bool(False).tag(sync=True)
    color = Bool(False).tag(sync=True)

    def __init__(self, *args, **kwargs):
        super(ContainerWidget, self).__init__(*args, **kwargs)

@register("exawidgets.ContainerBox")
class ContainerBox(Box):
    _model_module = Unicode("jupyter-exawidgets").tag(sync=True)
    _view_module = Unicode("jupyter-exawidgets").tag(sync=True)
    _model_name = Unicode("ContainerBoxModel").tag(sync=True)
    _view_name = Unicode("ContainerBoxView").tag(sync=True)
    but1 = Instance(Button).tag(sync=True, **widget_serialization)
    but2 = Instance(Button).tag(sync=True, **widget_serialization)
    container = Instance(ContainerWidget).tag(sync=True, **widget_serialization)

    def __init__(self, *args, **kwargs):
        but1 = Button(icon="bars", description=" Clear")
        but2 = Button(icon="bars", description=" Color")
        container = ContainerWidget()
        def _on1(b): self.container.clear = not self.container.clear == True
        def _on2(b): self.container.color = not self.container.color == True
        but1.on_click(_on1)
        but2.on_click(_on2)
        gui = VBox([but1, but2])
        children = HBox([gui, container])
        super(ContainerBox, self).__init__(*args, children=[children],
                                           but1=but1,
                                           but2=but2,
                                           container=container, **kwargs)


# @register("exawidgets.ControllerWidget")
# class ControllerWidget(Box):
#     but1 = Instance(Button).tag(sync=True, **widget_serialization)
#     but2 = Instance(Button).tag(sync=True, **widget_serialization)
#     drop = Instance(Dropdown).tag(sync=True, **widget_serialization)
#     scene = Instance(ContainerWidget).tag(sync=True, **widget_serialization)
#
#     def __init__(self, *args, **kwargs):
#         but1 = Button()
#         but2 = Button()
#         drop = Dropdown(options=["Things", "Stuff"])
#         scene = ContainerWidget()
#         super(ControllerWidget, self).__init__([VBox([HBox([bu1, but2]), drop])], **kwargs)



# class BaseWidget(DOMWidget):
#     """
#     Base widget class for Jupyter notebook widgets provided by exawidgets.
#     Standardizes bidirectional communication handling between notebook
#     extensions' frontend JavaScript and backend Python.
#     """
#     _view_module = Unicode("jupyter-exawidgets").tag(sync=True)
#     _model_module = Unicode("jupyter-exawidgets").tag(sync=True)
#     _model_name = Unicode("BaseModel").tag(sync=True)
#     _view_name = Unicode("BaseView").tag(sync=True)
#     width = Unicode("800").tag(sync=True)
#     height = Unicode("500").tag(sync=True)
#     fps = Integer(24).tag(sync=True)
#
#     def _handle_image(self, content):
#         raise NotImplementedError()
#
#     def _handle_custom_msg(self, message, callback):
#         """
#         Recieve and handle messages from notebook extensions ("frontend").
#         """
#         #raise NotImplementedError('Handling custom message from JS not ready')
#         typ = message['type']
#         content = message['content']
#         # Logic to handle various types of messages...
#         if typ == 'image':
#             self._handle_image(content)
#
#     def _repr_html_(self):
#         self._ipython_display_()
#
#     def __init__(self, *args, **kwargs):
#         super(BaseWidget, self).__init__(*args, layout=Layout(width="800", height="500"), **kwargs)
#
#
# class ContainerWidget(BaseWidget):
#     """
#     Jupyter notebook widget representation of an exa-based Container. The widget
#     accepts a (reference to a) container and parameters and creates a suitable
#     display.
#     """
#     _view_module = Unicode("jupyter-exawidgets").tag(sync=True)
#     _model_module = Unicode("jupyter-exawidgets").tag(sync=True)
#     _model_name = Unicode("ContainerModel").tag(sync=True)
#     _view_name = Unicode("ContainerView").tag(sync=True)
#     gui_width = Unicode("250").tag(sync=True)
#
#     def __init__(self, container=None, *args, **kwargs):
#         super(ContainerWidget, self).__init__(*args, **kwargs)
#         self.container = container
#         if container is None:
#             test = Bool(True).tag(sync=True)
#             self.add_traits(test=test)
#         self.params = display_params
