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
import os
from ipywidgets import DOMWidget
from traitlets import Unicode, Integer, Bool

display_params = {
    'savedir': '',
    'filename': '',
}

class Widget(DOMWidget):
    """
    Base widget class for Jupyter notebook widgets provided by exawidgets.
    Standardizes bidirectional communication handling between notebook
    extensions' frontend JavaScript and backend Python.
    """
    width = Integer(850).tag(sync=True)
    height = Integer(500).tag(sync=True)
    fps = Integer(24).tag(sync=True)

    def _handle_image(self, content):
        raise NotImplementedError()

    def _handle_custom_msg(self, message, callback):
        """
        Recieve and handle messages from notebook extensions ("frontend").
        """
        #raise NotImplementedError('Handling custom message from JS not ready')
        typ = message['type']
        content = message['content']
        # Logic to handle various types of messages...
        if typ == 'image':
            self._handle_image(content)

    def _repr_html_(self):
        self._ipython_display_()


class ContainerWidget(Widget):
    """
    Jupyter notebook widget representation of an exa-based Container. The widget
    accepts a (reference to a) container and parameters and creates a suitable
    display.
    """
    _view_module = Unicode("jupyter-exawidgets").tag(sync=True)
    _model_module = Unicode("jupyter-exawidgets").tag(sync=True)
    _model_name = Unicode("ContainerModel").tag(sync=True)
    _view_name = Unicode("ContainerView").tag(sync=True)
    gui_width = Integer(250).tag(sync=True)

    def __init__(self, container=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.container = container
        if container is None:
            self.add_traits(test=Bool(True).tag(sync=True))
        self.params = display_params
