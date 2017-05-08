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
from ipywidgets import (DOMWidget, Box, VBox, HBox, Dropdown, Widget, IntSlider,
                        FloatSlider, Layout, Button, widget_serialization, register)
from traitlets import Unicode, Integer, Bool, List, Instance, Int, Float

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
    shape = Bool(False).tag(sync=True)
    field = Unicode("null").tag(sync=True)
    field_nx = Int(20).tag(sync=True)
    field_ny = Int(20).tag(sync=True)
    field_nz = Int(20).tag(sync=True)
    isoval = Float(3.0).tag(sync=True)

    def __init__(self, *args, **kwargs):
        super(ContainerWidget, self).__init__(*args, **kwargs)

width = "200px"
alayout = Layout(width=width)
rpad = "margin: 0px 0px 0px -40px;"
blayout = Layout(width=width, margin=rpad)

@register("exawidgets.ContainerBox")
class ContainerBox(Box):
    _model_module = Unicode("jupyter-exawidgets").tag(sync=True)
    _view_module = Unicode("jupyter-exawidgets").tag(sync=True)
    _model_name = Unicode("ContainerBoxModel").tag(sync=True)
    _view_name = Unicode("ContainerBoxView").tag(sync=True)
    bclear = Instance(Button).tag(sync=True, **widget_serialization)
    bshape = Instance(Button).tag(sync=True, **widget_serialization)
    bcolor = Instance(Button).tag(sync=True, **widget_serialization)
    drop = Instance(Dropdown).tag(sync=True, **widget_serialization)
    nxsl = Instance(IntSlider).tag(sync=True, **widget_serialization)
    nysl = Instance(IntSlider).tag(sync=True, **widget_serialization)
    nzsl = Instance(IntSlider).tag(sync=True, **widget_serialization)
    isosl = Instance(FloatSlider).tag(sync=True, **widget_serialization)
    container = Instance(ContainerWidget).tag(sync=True, **widget_serialization)

    def __init__(self, *args, **kwargs):
        bclear = Button(icon="bomb", description=" Clear", layout=alayout)
        bshape = Button(icon="cubes", description="  Geometry", layout=alayout)
        bcolor = Button(icon="paint-brush", description="  Color", layout=alayout)
        drop = Dropdown(options=["null", "sphere", "torus", "ellipsoid"],
                        layout=alayout)
        nxsl = IntSlider(min=10, max=50, step=1, description="N$_{x}$", layout=blayout)
        nysl = IntSlider(min=10, max=50, step=1, description="N$_{y}$", layout=blayout)
        nzsl = IntSlider(min=10, max=50, step=1, description="N$_{z}$", layout=blayout)
        isosl = FloatSlider(min=3.0, max=10.0, description="Iso.", layout=blayout)
        container = ContainerWidget()
        # Button handlers
        def _onclear(b): self.container.clear = not self.container.clear == True
        def _onshape(b): self.container.shape = not self.container.shape == True
        def _oncolor(b): self.container.color = not self.container.color == True
        # Button callbacks
        bclear.on_click(_onclear)
        bshape.on_click(_onshape)
        bcolor.on_click(_oncolor)
        # Slider handlers
        def _onfield(c): self.container.field = c["new"]
        def _onnxsl(c): self.container.field_nx = c["new"]
        def _onnysl(c): self.container.field_ny = c["new"]
        def _onnzsl(c): self.container.field_nz = c["new"]
        def _oniso(c): self.container.isoval = c["new"]
        # Slider callbacks
        drop.observe(_onfield, names="value")
        nxsl.observe(_onnxsl, names="value")
        nysl.observe(_onnysl, names="value")
        nzsl.observe(_onnzsl, names="value")
        isosl.observe(_oniso, names="value")
        # Stitch it all together
        gui = VBox([bclear, bshape, bcolor, drop, isosl, nxsl, nysl, nzsl])
        children = HBox([gui, container])
        super(ContainerBox, self).__init__(*args, children=[children],
                                           bclear=bclear, bshape=bshape,
                                           bcolor=bcolor, drop=drop, isosl=isosl,
                                           nxsl=nxsl, nysl=nysl, nzsl=nzsl,
                                           container=container, **kwargs)
