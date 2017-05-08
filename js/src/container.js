// Copyright (c) 2015-2017, Exa Analytics Development Team
// Distributed under the terms of the Apache License 2.0
/*"""
=================
container.js
=================
JavaScript "frontend" complement of exawidget's Container for use within
the Jupyter notebook interface. This "module" standardizes bidirectional
communication logic for all container widget views.

The structure of the frontend is to generate an HTML widget ("container" - see
create_container) and then populate its canvas with an application ("app")
appropriate to the type of container. If the (backend) container is empty, then
populate the HTML widget with the test application.
*/
"use strict";
var widgets = require("jupyter-js-widgets");
var _ = require("underscore");
var THREE = require("three");
var TBC = require("three-trackballcontrols");
var field = require("./field.js");
var app3d = require("./app3d.js");
var num = require("./num.js");

class BaseDataModel extends widgets.WidgetModel {
    get defaults() {
        return _.extend({}, widgets.WidgetModel.prototype.defaults, {
            _model_module: "jupyter-exawidgets",
            _view_module: "jupyter-exawidgets",
            _model_name: "BaseDataModel",
            _view_name: "BaseDataView",
            datars: [0, 1, 2, 3]
        })
    }
}

class BaseDataView extends widgets.WidgetView {
}

class BaseDOMModel extends widgets.DOMWidgetModel {

    get defaults() {
        return _.extend({}, widgets.DOMWidgetModel.prototype.defaults, {
            _model_module: "jupyter-exawidgets",
            _view_module: "jupyter-exawidgets",
            _model_name: "BaseDOMModel",
            _view_name: "BaseDOMView"
        })
    }

    clear() {
        if (this.get("background") === "green") {
            this.set("background", "black");
        } else {
            this.set("background", "green");
        }
    }

}

class BaseDOMView extends widgets.DOMWidgetView {

    initialize() {
        var that = this;
        $(this.el).width(
            this.model.get("layout").get("width")).height(
            this.model.get("layout").get("height")).resizable({
            aspectRatio: false,
            resize: function(event, ui) {
                var w = ui.size.width;
                var h = ui.size.height;
                that.model.get("layout").set("width", w);
                that.model.get("layout").set("height", h);
                that.el.width = w;
                that.el.height = h;
                that.resize(w, h);
            }
        });
        this.init();
    }

    init() {
        this.init_listeners();
    }

    init_listeners() {
        this.model.on("change:background", this.set_background, this);
    }

    set_buttons() {
        var that = this;
        var clear = document.createElement("button");
        clear.classList.add("jupyter-widgets");
        clear.classList.add("jupyter-button");
        clear.classList.add("widget-toggle-button");
        clear.setAttribute("data-toggle", "tooltip");
        clear.setAttribute("title", "Clear");
        clear.onclick = function(e) {
            e.preventDefault();
            that.model.clear();
        };
        var icon = document.createElement("i");
        icon.className = "fa fa-arrows";
        clear.appendChild(icon);
        this.el.appendChild(clear);
    }

    set_background() {
        this.$el.css({"background-color": this.model.get("background")});
    }

    render() {
        this.set_buttons();
        this.set_background();
    }

    resize(w, h) {
    }

}


// additional requirements from here
// three, three-trackballcontrols

class ContainerModel extends BaseDOMModel {
    get defaults() {
        return _.extend({}, BaseDOMModel.prototype.defaults, {
            _model_name: "ContainerModel",
            _view_name: "ContainerView",
            drop: undefined,
            field: "null",
            isoval: 1.0,
            field_nx: 20,
            field_ny: 20,
            field_nz: 20,
            clear: false,
            shape: false,
            color: false
        })
    }

    aspectRatio() {
        return this.get("layout").get("width") / this.get("layout").get("height");
    }
}

ContainerModel.serializers = _.extend({
    dummy: { deserialize: widgets.unpack_models },
    button: { deserialize: widgets.unpack_models },
}, BaseDOMModel.serializers)

class ContainerView extends BaseDOMView {

    init() {
        this.meshes = [];
        this.init_listeners();

        this.camera = new THREE.PerspectiveCamera(35, this.model.aspectRatio(), 1, 1000);
        this.camera.position.z = 10;

        this.scene = new THREE.Scene();
        this.test_geometry();
        this.field_params = {
            "isoval": this.model.get("isoval"),
            "boxsize": 3.0,
            "nx": this.model.get("field_nx"),
            "ny": this.model.get("field_ny"),
            "nz": this.model.get("field_nz"),
            "ox": -3.0, "oy": -3.0, "oz": -3.0,
            "fx":  3.0, "fy":  3.0, "fz":  3.0,
            "dxi": 0.5, "dyj": 0.5, "dzk": 0.5,
            "dxj": 0.0, "dyi": 0.0, "dzi": 0.0,
            "dxk": 0.0, "dyk": 0.0, "dzj": 0.0,
        };

        this.renderer = new THREE.WebGLRenderer({
            antialias: true,
            alpha: true
        });
        this.renderer.setSize(this.model.get("layout").get("width"),
                              this.model.get("layout").get("height"));
        this.el.appendChild(this.renderer.domElement);

        this.controls = new TBC(this.camera, this.renderer.domElement);
        this.controls.rotateSpeed = 10.0;
        this.controls.zoomSpeed = 5.0;
        this.controls.panSpeed = 0.5;
        this.controls.noZoom = false;
        this.controls.noPan = false;
        this.controls.staticMoving = true;
        this.controls.dynamicDampingFactor = 0.3;
        this.controls.keys = [65, 83, 68];
        this.controls.addEventListener("change", this.render.bind(this));
        this.controls.target = new THREE.Vector3(0.0, 0.0, 0.0);

        console.log(app3d);
        this.app3d = new app3d.App3D(this);

        this.add_meshes();
        this.animation();
    }

    test_geometry(color) {
        color = (typeof color === "undefined") ? "red" : color;
        var geom = new THREE.IcosahedronGeometry(2, 1);
        var mat = new THREE.MeshBasicMaterial({
            color: color,
            wireframe: true
        });
        var mesh = new THREE.Mesh(geom, mat);
        this.meshes.push(mesh);
    }

    render() {
        this.renderer.render(this.scene, this.camera);
    }

    resize(w, h) {
        this.model.get("layout").set("width", w);
        this.model.get("layout").set("height", h);
        this.renderer.setSize(w, h);
        this.camera.aspect = this.model.aspectRatio();
        this.camera.updateProjectionMatrix();
        this.controls.handleResize();
        this.render();
    }

    animation() {
        window.requestAnimationFrame(this.animation.bind(this));
        this.render();
        this.controls.update();
        this.resize(this.model.get("layout").get("width"),
                    this.model.get("layout").get("height"));
    }

    clear_meshes() {
        for (var idx in this.meshes) {
            this.scene.remove(this.meshes[idx]);
        };
        this.meshes = [];
        this.render();
    }

    add_meshes() {
        for (var idx in this.meshes) {
            this.scene.add(this.meshes[idx]);
        };
        this.render();
    }

    shape_scene() {
        this.clear_meshes();
        this.test_geometry();
        this.add_meshes();
    }

    color_scene() {
        var color = (this.model.get("color") === true) ? "black": "red";
        this.clear_meshes();
        this.test_geometry(color);
        this.add_meshes();
    }

    field_scene() {
        this.clear_meshes();
        var field_type = this.model.get("field");
        this.field_params["isoval"] = this.model.get("isoval");
        this.field_params["boxsize"] = this.model.get("boxsize");
        this.field_params["nx"] = this.model.get("field_nx");
        this.field_params["ny"] = this.model.get("field_ny");
        this.field_params["nz"] = this.model.get("field_nz");
        var thisfield = new field.ScalarField(this.field_params,
                                              num[field_type]);
        this.meshes = this.app3d.add_scalar_field(thisfield, this.field_params.isoval);
        this.add_meshes();
    }

    init_listeners() {
        this.listenTo(this.model, "change:clear", this.clear_meshes);
        this.listenTo(this.model, "change:shape", this.shape_scene);
        this.listenTo(this.model, "change:color", this.color_scene);
        this.listenTo(this.model, "change:field", this.field_scene);
        this.listenTo(this.model, "change:field_nx", this.field_scene);
        this.listenTo(this.model, "change:field_ny", this.field_scene);
        this.listenTo(this.model, "change:field_nz", this.field_scene);
        this.listenTo(this.model, "change:isoval", this.field_scene);
    }

}


class ContainerBoxModel extends widgets.BoxModel {
    get defaults() {
        return _.extend({}, widgets.BoxModel.prototype.defaults, {
            _model_module: "jupyter-exawidgets",
            _view_module: "jupyter-exawidgets",
            _model_name: "ContainerBoxModel",
            _view_name: "ContainerBoxView",
            container: undefined,
            but1: undefined
        })
    }
}


class ContainerBoxView extends widgets.BoxView {
    render() {
        super.render();
    }
}


module.exports = {
    BaseDataModel: BaseDataModel,
    BaseDataView: BaseDataView,
    BaseDOMModel: BaseDOMModel,
    BaseDOMView: BaseDOMView,
    ContainerModel: ContainerModel,
    ContainerView: ContainerView,
    ContainerBoxModel: ContainerBoxModel,
    ContainerBoxView: ContainerBoxView
}
