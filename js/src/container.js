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
var TrackballControls = require("three-trackballcontrols");
//var TestApp = require("./test.js").TestApp;

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
            clear: false,
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

    /*
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
            that.clear();
        };
        var icon = document.createElement("i");
        icon.className = "fa fa-bars";
        clear.appendChild(icon);
        this.el.appendChild(clear);

        //this.el.appendChild(this.model.get("button"));

        var dropdown = document.createElement("dropdown");
        dropdown.classList.add("jupyter-widgets");
        dropdown.classList.add("widget-inline-hbox");
        dropdown.classList.add("widget-dropdown");
        //dropdown.classList.add("dropdown");
        dropdown.setAttribute("data-toggle", "dropdown");
        dropdown.setAttribute("title", "Dropdown");
        var options = ['things', 'stuff', 'faces'];
        var listbox = document.createElement("select");
        for (var i in options) {
            var item = options[i];
            var option = document.createElement("option");
            option.textContext = item;
            option.setAttribute("data-value", item);
            option.value = item;
            listbox.appendChild(option);
        }
        dropdown.appendChild(listbox);
        /*
        dropdown.onclick = function(e) {
            console.log("can click a dropdown");
        this.el.appendChild(dropdown);
        };*/

/*
        var color = document.createElement("button");
        color.classList.add("jupyter-widgets"); // jupyter-js-widgets css
        color.classList.add("jupyter-button"); // jupyter-js-widgets css
        color.classList.add("widget-button") // jupyter-js-widgets css
        color.setAttribute("data-toggle", "tooltip");
        color.setAttribute("title", "Reset");
        color.onclick = function (e) {
            e.preventDefault();
            that.set_color();
        };
        var coloricon = document.createElement("i");
        coloricon.className = "fa fa-refresh";
        color.appendChild(coloricon);
        this.el.appendChild(color);
    }
*/

    init() {
        this.meshes = [];
        this.init_listeners();

        this.camera = new THREE.PerspectiveCamera(35, this.model.aspectRatio(), 10, 1000);
        this.camera.position.z = 500;

        this.scene = new THREE.Scene();
        this.test_geometry();
        this.scene.add(this.meshes[0]);

        this.renderer = new THREE.WebGLRenderer({
            antialias: true,
            alpha: true
        });
        this.renderer.setSize(this.model.get("layout").get("width"),
                              this.model.get("layout").get("height"));
        this.el.appendChild(this.renderer.domElement);

        this.controls = new TrackballControls(this.camera, this.renderer.domElement);
        this.controls.rotateSpeed = 10.0;
        this.controls.zoomSpeed = 5.0;
        this.controls.panSpeed = 0.5;
        this.controls.noZoom = false;
        this.controls.noPan = false;
        this.controls.staticMoving = true;
        this.controls.dynamicDampingFactor = 0.3;
        this.controls.keys = [65, 83, 68];
        this.controls.addEventListener("change", this.render.bind(this));
        this.controls.target = new THREE.Vector3(10.0, 10.0, 10.0);

        this.render();
        this.animation();
    }

    test_geometry(color) {
        color = (typeof color === "undefined") ? "red" : color;
        var geom = new THREE.IcosahedronGeometry(100, 1);
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

    clear_scene() {
        if (this.model.get("clear")) {
            this.clear_meshes();
        } else {
            var color = (this.model.get("color") === true) ? "black" : "red";
            this.test_geometry(color);
            this.add_meshes();
        }
    }

    color_scene() {
        if (this.model.get("clear") === false) {
            if (this.model.get("color")) {
                this.clear_meshes();
                this.test_geometry("black");
                this.add_meshes();
            } else {
                this.clear_meshes();
                this.test_geometry();
                this.add_meshes();
            }
        }
    }

    init_listeners() {
        this.listenTo(this.model, "change:clear", this.clear_scene);
        this.listenTo(this.model, "change:color", this.color_scene);
    }

/*
    set_color() {
        if (this.meshes.length === 0) {
            var mesh = this.test_geometry();
            this.meshes.push(mesh);
        } else {
            for (var idx in this.meshes) {
                this.scene.remove(this.meshes[idx]);
            }
            var mesh = this.test_geometry("green");
            this.render();
        }
    }
    */

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

ContainerBoxModel.serializers = _.extend({
    but1: { deserialize: widgets.unpack_models },
    container: { deserialize: widgets.unpack_models },
}, widgets.BoxModel.serializers)

class ContainerBoxView extends widgets.BoxView {
    render() {
        super.render();
        var children = this.model.get("children");
        var but1 = this.model.get("but1");
        var container = this.model.get("container");
        console.log(children);
        console.log(but1);
        console.log(container);
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

// class BaseModel extends widgets.DOMWidgetModel {
//     get defaults() {
//       return _.extend({}, widgets.DOMWidgetModel.prototype.defaults, {
//             _model_module: "jupyter-exawidgets",
//             _view_module: "jupyter-exawidgets",
//             _model_name: "BaseModel",
//             _view_name: "BaseView",
//             width: 800,
//             height: 500
//         });
//     }
// }
//
// class BaseView extends widgets.DOMWidgetView {
//
// }
//
// class ContainerModel extends BaseModel {
//     get defaults() {
//       return _.extend({}, BaseModel.prototype.defaults, {
//             _model_module: "jupyter-exawidgets",
//             _view_module: "jupyter-exawidgets",
//             _model_name: "ContainerModel",
//             _view_name: "ContainerView",
//             gui_width: 250,
//         });
//     }
// }
//
// class ContainerView extends BaseView {
//     /*"""
//     ContainerView
//     ===============
//     Base view for creating data specific container widgets used within the
//     Jupyter notebook. All logic related to communication (between Python
//     and JavaScript) should be located here. This class provides a number
//     of commonly used functions for such logic.
//
//     Warning:
//         Do not override the DOMWidgetView constructor ("initialize").
//     */
//     render() {
//         /*"""
//         render
//         -------------
//         Main entry point (called immediately after initialize) for
//         (ipywidgets) DOMWidgetView objects.
//
//         Note:
//             This function  can be overwritten by container specific code,
//             but it is more common to overwrite the **init** function.
//
//         See Also:
//             **init()**
//         */
//         this.default_listeners();
//         this.create_container();
//         this.init();              // Specific to the data container
//         this.setElement(this.container);
//     };
//
//     init() {
//         /*"""
//         init
//         -------------
//         Container view classes that extend this class can overwrite this
//         method to customize the behavior of their data specific view.
//         */
//         this.if_empty();
//     };
//
//     get_trait(name) {
//         /*"""
//         get_trait
//         -------------
//         Wrapper around the DOMWidgetView (Backbone.js) "model.get" function,
//         that attempts to convert JSON strings to objects.
//         */
//         var obj = this.model.get(name);
//         if (typeof obj === "string") {
//             try {
//                 obj = JSON.parse(obj);
//             } catch(err) {
//                 console.log(err);
//             };
//         };
//         return obj;
//     };
//
//     set_trait(name, value) {
//         /*"""
//         set_trait
//         ----------
//         Wrapper around the DOMWidgetView "model.set" function to correctly
//         set json strings.
//         */
//         if (typeof value === Object) {
//             try {
//                 value = JSON.stringify(value);
//             } catch(err) {
//                 console.log(err);
//             };
//         };
//         this.model.set(name, value);
//     };
//
//     if_empty() {
//         /*"""
//         if_empty
//         ----------------
//         If the (exa) container object is empty, render the test application
//         widget.
//         */
//         var check = this.get_trait("test");
//         if (check === true) {
//             console.log("Empty container, displaying test interface!");
//             this.app = new TestApp(this);
//         };
//     };
//
//     default_listeners() {
//         /*"""
//         default_listeners
//         -------------------
//         Set up listeners for basic variables related to the window dimensions
//         and system settings.
//         */
//         this.get_width();
//         this.get_height();
//         this.get_gui_width();
//         this.get_fps();
//         this.get_field_values();
//         this.get_field_indices();
//         this.listenTo(this.model, "change:width", this.get_width);
//         this.listenTo(this.model, "change:height", this.get_height);
//         this.listenTo(this.model, "change:gui_width", this.get_gui_width);
//         this.listenTo(this.model, "change:fps", this.get_fps);
//         this.listenTo(this.model, "change:field_values", this.get_field_values);
//         this.listenTo(this.model, "change:field_indices", this.get_field_indices);
//     };
//
//     create_container() {
//         /*"""
//         create_container
//         ------------------
//         Create a resizable container.
//         */
//         var self = this;
//         this.container = $("<div/>").width(this.width).height(this.height).resizable({
//             aspectRatio: false,
//             resize: function(event, ui) {
//                 self.width = ui.size.width - self.gui_width;
//                 self.height = ui.size.height;
//                 self.set_trait("width", self.width);
//                 self.set_trait("height", self.height);
//                 self.canvas.width(self.width);
//                 self.canvas.height(self.height);
//                 self.app.resize();
//             },
//         });
//     };
//     create_canvas() {
//         /*"""
//         create_canvas
//         ----------------
//         Create a canvas for WebGL.
//         */
//         this.canvas = $("<canvas/>").width(this.width - this.gui_width).height(this.height);
//         this.canvas.css("position", "absolute");
//         this.canvas.css("top", 0);
//         this.canvas.css("left", this.gui_width);
//     };
//
//     get_gui_width() {
//         this.gui_width = this.get_trait("gui_width");
//     };
//
//     get_fps() {
//         this.fps = this.get_trait("fps");
//     };
//
//     get_width() {
//         this.width = this.get_trait("width");
//     };
//
//     get_height() {
//         this.height = this.get_trait("height");
//     };
//
//     get_field_values() {
//         this.field_values = this.get_trait("field_values");
//     };
//
//     get_field_indices() {
//         this.field_indices = this.get_trait("field_indices");
//     };
// };
//
// module.exports = {
//     "BaseModel": BaseModel,
//     "BaseView": BaseView,
//     "ContainerView": ContainerView,
//     "ContainerModel": ContainerModel
// }
