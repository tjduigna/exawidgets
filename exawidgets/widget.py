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
from ipywidgets import DOMWidget, Layout, Button, widget_serialization, register
from traitlets import Unicode, Integer, Bool, Instance

display_params = {
    'savedir': '',
    'filename': '',
}

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

@register("exawidgets.BaseDOM")
class BaseDOM(DOMWidget):
    _view_module = Unicode("jupyter-exawidgets").tag(sync=True)
    _model_module = Unicode("jupyter-exawidgets").tag(sync=True)
    _model_name = Unicode("BaseDOMModel").tag(sync=True)
    _view_name = Unicode("BaseDOMView").tag(sync=True)

@register("exawidgets.GUIWidget")
class GUIWidget(BaseDOM):
    _model_name = Unicode("GUIModel").tag(sync=True)
    _view_name = Unicode("GUIView").tag(sync=True)
    button = Instance(Button).tag(sync=True, **widget_serialization)
    width = Unicode("250").tag(sync=True)

    def __init__(self, *args, button=None, **kwargs):
        if button is None: button = Button()
        super(GUIWidget, self).__init__(*args, button=button, **kwargs)

@register("exawidgets.SceneWidget")
class SceneWidget(BaseDOM):
    _model_name = Unicode("SceneModel").tag(sync=True)
    _view_name = Unicode("SceneView").tag(sync=True)

@register("exawidgets.ContainerWidget")
class ContainerWidget(BaseDOM):
    _model_name = Unicode("ContainerModel").tag(sync=True)
    _view_name = Unicode("ContainerView").tag(sync=True)
    gui = Instance(GUIWidget).tag(sync=True, **widget_serialization)
    scene = Instance(SceneWidget).tag(sync=True, **widget_serialization)
    layout = Instance(Layout).tag(sync=True, **widget_serialization)

    def __init__(self, *args, container=None, gui=None, scene=None, layout=None, **kwargs):
        if gui is None: gui = GUIWidget()
        if scene is None: scene = SceneWidget()
        if layout is None: layout = Layout(width="980", height="500")
        super(ContainerWidget, self).__init__(*args, gui=gui, scene=scene, layout=layout, **kwargs)
        self.container = container
        if container is None:
            test = Bool(True).tag(sync=True)
            self.add_traits(test=test)
        self.params = display_params
