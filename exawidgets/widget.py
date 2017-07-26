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
from collections import OrderedDict
from base64 import b64decode
from ipywidgets import (Widget, DOMWidget, Box, VBox, HBox, Label,
                        Dropdown, IntSlider, FloatSlider, Button, interactive,
                        Layout, widget_serialization, register, jslink)
from traitlets import Unicode, Bool, List, Instance, Int, Float


# Default layouts
width = "600"
height = "450"
gui_lo = Layout(width="200px")

@register("exawidgets.BaseData")
class BaseData(Widget):
    """Base class for widgets attached to ThreeJS scene."""
    _view_module = Unicode("jupyter-exawidgets").tag(sync=True)
    _model_module = Unicode("jupyter-exawidgets").tag(sync=True)
    _model_name = Unicode("BaseDataModel").tag(sync=True)
    _view_name = Unicode("BaseDataView").tag(sync=True)


@register("exawidgets.BaseDOM")
class BaseDOM(DOMWidget):
    """Base class for ThreeJS scene."""
    _view_module = Unicode("jupyter-exawidgets").tag(sync=True)
    _model_module = Unicode("jupyter-exawidgets").tag(sync=True)
    _model_name = Unicode("BaseDOMModel").tag(sync=True)
    _view_name = Unicode("BaseDOMView").tag(sync=True)
    background = Unicode("green").tag(sync=True)

    def _handle_custom_msg(self, message, callback):
        """Custom message handler."""
        typ = message["type"]
        content = message["content"]
        if typ == "image": self._handle_image(content)

    def _handle_image(self, content):
        raise NotImplementedError()

    def __init__(self, *args, **kwargs):
        super(BaseDOM, self).__init__(*args,
                                      layout=Layout(width=width, height=height),
                                      **kwargs)


@register("exawidgets.BaseBox")
class BaseBox(Box):
    """Base class for containers of a GUI and scene."""
    _model_module = Unicode("jupyter-exawidgets").tag(sync=True)
    _view_module = Unicode("jupyter-exawidgets").tag(sync=True)
    _model_name = Unicode("BaseBoxModel").tag(sync=True)
    _view_name = Unicode("BaseBoxView").tag(sync=True)


@register("exawidgets.ThreeScene")
class ThreeScene(BaseDOM):
    _model_name = Unicode("ThreeSceneModel").tag(sync=True)
    _view_name = Unicode("ThreeSceneView").tag(sync=True)
    scn_clear = Bool(False).tag(sync=True)
    scn_saves = Bool(False).tag(sync=True)
    savedir = Unicode("").tag(sync=True)
    imgname = Unicode("").tag(sync=True)

    def _handle_image(self, content):
        #print(content)
        savedir = self.savedir
        if not savedir: savedir = os.getcwd()
        fname = self.imgname
        if not fname:
            nxt = 0
            fname = "{:06d}.png".format(nxt)
            while os.path.isfile(os.sep.join([savedir, fname])):
                nxt += 1
                fname = "{:06d}.png".format(nxt)
        with open(os.sep.join([savedir, fname]), "wb") as f:
            f.write(b64decode(content.replace("data:image/png;base64,", "")))
        # Pass on this for now
        # try:
        #     crop = " ".join(["convert -trim", imgname, imgname])
        #     subprocess.call(crop, cwd=savedir, shell=True)
        # except:
        #     pass


@register("exawidgets.TestScene")
class TestScene(ThreeScene):
    _model_name = Unicode("TestSceneModel").tag(sync=True)
    _view_name = Unicode("TestSceneView").tag(sync=True)
    geo_shape = Bool(False).tag(sync=True)
    geo_color = Bool(False).tag(sync=True)
    field = Unicode("null").tag(sync=True)
    field_nx = Int(20).tag(sync=True)
    field_ny = Int(20).tag(sync=True)
    field_nz = Int(20).tag(sync=True)
    field_iso = Float(2.0).tag(sync=True)


## Disclaimer: see https://github.com/jupyter-widgets/ipywidgets/pull/1376
##             ought to fix the labeling // interactive widget spacing issue
##             we have been grappling with. It essentially amounts to adding
##             a style dict=(description_width="XXpx") keyword argument to
##             to any controller widgets we may find useful.


field_options = ["null", "sphere", "torus", "ellipsoid"]
field_n_lims = {"min": 10, "max": 50, "step": 1, "layout": gui_lo}


@register("exawidgets.TestContainer")
class TestContainer(BaseBox):
    _model_name = Unicode("TestContainerModel").tag(sync=True)
    _view_name = Unicode("TestContainerView").tag(sync=True)
    scene = Instance(TestScene).tag(sync=True, **widget_serialization)

    def init_gui(self):
        self.controls = OrderedDict([
            ('scn_clear', Button(icon="bomb", description=" Clear",
                                 layout=gui_lo)),
            ('scn_saves', Button(icon="camera", description=" Save",
                                 layout=gui_lo)),
            ('geo_shape', Button(icon="cubes", description="  Geometry",
                                 layout=gui_lo)),
            ('geo_color', Button(icon="paint-brush", description="  Color",
                                 layout=gui_lo)),
            ('field_options', Dropdown(options=field_options, layout=gui_lo)),
        ])
        # Button callbacks
        def _scn_clear(b): self.scene.scn_clear = not self.scene.scn_clear == True
        def _scn_saves(b): self.scene.scn_saves = not self.scene.scn_saves == True
        def _geo_shape(b): self.scene.geo_shape = not self.scene.geo_shape == True
        def _geo_color(b): self.scene.geo_color = not self.scene.geo_color == True
        # Button handlers
        self.controls['geo_shape'].on_click(_geo_shape)
        self.controls['scn_clear'].on_click(_scn_clear)
        self.controls['scn_saves'].on_click(_scn_saves)
        self.controls['geo_color'].on_click(_geo_color)
        # Field handler
        def _field(c):
            print(c)
            if c['new'] == 'null':
                for key in ['field_iso', 'field_nx', 'field_ny', 'field_nz']:
                    self.controls.pop(key)
            else:
                self.controls['field_iso'] = FloatSlider(min=3.0, max=10.0,
                                                         description="Iso.",
                                                         layout=gui_lo)
                self.controls['field_nx'] = IntSlider(description="Nx",
                                                      **field_n_lims)
                self.controls['field_ny'] = IntSlider(description="Ny",
                                                      **field_n_lims)
                self.controls['field_nz'] = IntSlider(description="Nz",
                                                      **field_n_lims)
                # Slider callbacks
                def _field_iso(c): self.scene.field_iso = c["new"]
                def _field_nx(c): self.scene.field_nx = c["new"]
                def _field_ny(c): self.scene.field_ny = c["new"]
                def _field_nz(c): self.scene.field_nz = c["new"]
                # Slider handlers
                self.controls['field_iso'].observe(_field_iso, names="value")
                self.controls['field_nx'].observe(_field_nx, names="value")
                self.controls['field_ny'].observe(_field_ny, names="value")
                self.controls['field_nz'].observe(_field_nz, names="value")
            self.gui = VBox([val for key, val in self.controls.items()])
            self.set_gui()

        self.controls['field'].observe(_field, names="value")
        self.gui = VBox([val for key, val in self.controls.items()])

    def set_gui(self):
        self.children[0].children[0].children = self.gui.children
        self.on_displayed(TestContainer._fire_children_displayed)

    def __init__(self, *args, **kwargs):
        self.scene = TestScene()
        self.init_gui()
        self.children = [HBox([self.gui, self.scene])]
        super(TestContainer, self).__init__(*args,
                                            children=self.children,
                                            scene=self.scene,
                                            **kwargs)
