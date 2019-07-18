"use strict";

var _REGION_EDGE_TOL = 5; // pixel
var _REGION_POINT_RADIUS = 3;
var _REGION_MIN_DIM = 3;
var _MOUSE_CLICK_TOL = 2;
var _CANVAS_DEFAULT_ZOOM_LEVEL_INDEX = 3;
var _CANVAS_ZOOM_LEVELS = [0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 2.5, 3.0, 4, 5];

var _THEME_REGION_BOUNDARY_WIDTH = 2;
var _THEME_BOUNDARY_LINE_COLOR = "#ff0000";
var _THEME_BOUNDARY_FILL_COLOR = "#aaeeff";
var _THEME_SEL_REGION_FILL_COLOR = "#e9e9e9";
var _THEME_SEL_REGION_FILL_BOUNDARY_COLOR = "#000000";
var _THEME_SEL_REGION_OPACITY = 0.5;
var _THEME_MESSAGE_TIMEOUT_MS = 2500;
var _THEME_ATTRIBUTE_VALUE_FONT = ' system-ui';
var _THEME_CONTROL_POINT_COLOR = '#ff0000';
var _THEME_REGION_ID_COLOR = '#0000ff';
var _CSV_SEP = '\t';

var _canvas_regions = []; // image regions spec. in canvas space
var region_boundaries = []; // store region boundaries from txt file
var _canvas_scale = 1.0; // current scale of canvas image

var _current_image;
var _current_image_width;
var _current_image_height;

var image_url;
var average_box_height = 0.0;

// image canvas
var _img_canvas = document.getElementById("image_canvas");
var _img_ctx = _img_canvas.getContext("2d");
var _reg_canvas = document.getElementById("region_canvas");
var _reg_ctx = _reg_canvas.getContext("2d");
var _canvas_width, _canvas_height;

// canvas zoom
var _canvas_zoom_level_index = _CANVAS_DEFAULT_ZOOM_LEVEL_INDEX; // 1.0
var _canvas_scale_without_zoom = 1.0;

// state of the application
var _is_user_drawing_region = false;
var _current_image_loaded = false;
var _is_window_resized = false;
var _is_user_resizing_region = false;
var _is_user_moving_region = false;
var _is_user_drawing_polygon = false;
var _is_region_selected = false;
var _is_all_region_selected = false;
var _is_user_updating_attribute_name = false;
var _is_user_updating_attribute_value = false;
var _is_user_adding_attribute_name = false;
var _is_loaded_img_list_visible = false;
var _is_attributes_panel_visible = false;
var _is_reg_attr_panel_visible = false;
var _is_file_attr_panel_visible = false;
var _is_canvas_zoomed = false;
var _is_loading_current_image = false;
var _is_region_id_visible = true;
var _is_region_boundary_visible = true;
var _is_ctrl_pressed = false;
var _cur_region_id = 0;
var _cur_reg_drawing_id = -1;
var nested_region_id = -1;

// region
var _current_polygon_region_id = -1;
var _user_sel_region_id = -1;
var _click_x0 = 0;
var _click_y0 = 0;
var _click_x1 = 0;
var _click_y1 = 0;
var _region_click_x, _region_click_y;
var _copied_image_regions = [];
var _region_edge = [-1, -1];
var _current_x = 0;
var _current_y = 0;

// message
var _message_clear_timer;

// attributes
var _region_attributes = {};
var _current_update_attribute_name = "";
var _current_update_region_id = -1;
var _file_attributes = {};
var _visible_attr_name = '';
var _current_type = 'text';

// UI html elements
var image_panel = document.getElementById("image_panel");
var canvas_panel = document.getElementById("canvas_panel");

var annotation_list_snippet = document.getElementById("annotation_list_snippet");
var annotation_textarea = document.getElementById("annotation_textarea");

var loaded_img_list_panel = document.getElementById('loaded_img_list_panel');
var attributes_panel = document.getElementById('attributes_panel');
var annotation_data_window;

var BBOX_LINE_WIDTH = 4;
var BBOX_SELECTED_OPACITY = 0.3;
var BBOX_BOUNDARY_FILL_COLOR_ANNOTATED = "#f2f2f2";
var BBOX_BOUNDARY_FILL_COLOR_NEW = "#aaeeff";
var BBOX_BOUNDARY_LINE_COLOR = "#1a1a1a";
var BBOX_SELECTED_FILL_COLOR = "#ffffff";

//
// Initialization routine
//
function init() {
  image_url = document.getElementById("before_man_seg_img").src;
  import_region_attributes_from_file(function () {
    show_image();
  });
}

// Image to be manually segmented is provided to JS via
// a URL in iframe. 
// region_boundaries is the var holding the bounding boxes
// information with the same scale as the image.
// average_box_height is used for drawing region IDs
// next to the bounding boxes.
function import_region_attributes_from_file(_callback) {
  var oFrame = document.getElementById("boundaries_file_iframe");
  var strRawContents;

  $.ajax({
    type: 'GET',
    url: oFrame.src,
    datatype: 'text',
    success: function (data) {
      strRawContents = data;

      while (strRawContents.indexOf("\r") >= 0)
        strRawContents = strRawContents.replace("\r", "");

      var lines = strRawContents.split("\n");

      // using lines.length-1 since last line in
      // file is always empty
      for (var i = 0; i < lines.length - 1; ++i) {
        var attributes = lines[i].split('\t');
        var region = {};
        region['x'] = parseInt(attributes[0]);
        region['y'] = parseInt(attributes[1]);
        region['width'] = parseInt(attributes[2]);
        region['height'] = parseInt(attributes[3]);

        average_box_height += parseInt(attributes[3]);
        region_boundaries.push(region);
      }
      _region_attributes['x'] = true;
      _region_attributes['y'] = true;
      _region_attributes['width'] = true;
      _region_attributes['height'] = true;
      average_box_height /= lines.length - 1;
      _callback();
    }
  });
}

function clone_image_region(r0) {
  var r1 = new ImageRegion();
  r1.is_user_selected = r0.is_user_selected;

  // copy shape attributes
  for (var key in r0.shape_attributes) {
    r1.shape_attributes[key] = clone_value(r0.shape_attributes[key]);
  }

  // copy region attributes
  for (var key in r0.region_attributes) {
    r1.region_attributes[key] = clone_value(r0.region_attributes[key]);
  }
  return r1;
}

function clone_value(value) {
  if (typeof (value) === 'object') {
    if (Array.isArray(value)) {
      return value.slice(0);
    } else {
      var copy = {};
      for (var p in value) {
        if (value.hasOwnProperty(p)) {
          copy[p] = clone_value(value[p]);
        }
      }
      return copy;
    }
  }
  return value;
}


//
// Maintainers of user interface
//
function show_message(msg, t) {
  /*if ( _message_clear_timer ) {
    clearTimeout(_message_clear_timer); // stop any previous timeouts
  }
  var timeout = t;
  if ( typeof t === 'undefined' ) {
    timeout = _THEME_MESSAGE_TIMEOUT_MS;
  }
  document.getElementById('message_panel').innerHTML = msg;
  _message_clear_timer = setTimeout( function() {
    document.getElementById('message_panel').innerHTML = ' ';
  }, timeout);*/
}

// This function takes care of:
// - loading the image and deciding the scale of the image so
//   that it fits display_area width
// - drawing the image and the regions on the image and the
//   the region canvases respectively
function show_image() {
  _current_image = new Image();
  _current_image.src = image_url
  _click_x0 = 0;
  _click_y0 = 0;
  _click_x1 = 0;
  _click_y1 = 0;
  _is_user_drawing_region = false;
  _is_window_resized = false;
  _is_user_resizing_region = false;
  _is_user_moving_region = false;
  _is_region_selected = false;
  _user_sel_region_id = -1;
  _current_image_width = _current_image.naturalWidth;
  _current_image_height = _current_image.naturalHeight;

  // set the size of canvas
  // based on the current dimension of browser window
  var de = document.documentElement;
  var canvas_panel_width = document.getElementById('display_area').clientWidth - 20;
  var canvas_panel_height = document.getElementById('display_area').clientHeight - 20;
  _canvas_width = _current_image_width;
  _canvas_height = _current_image_height;

  // if image is big, resize it to match the panel width
  var scale_width = canvas_panel_width / _current_image_width;
  _canvas_width = canvas_panel_width;
  _canvas_height = _current_image_height * scale_width;

  _canvas_width = Math.round(_canvas_width);
  _canvas_height = Math.round(_canvas_height);
  _canvas_scale = _current_image_width / _canvas_width;
  _canvas_scale_without_zoom = _canvas_scale;
  set_all_canvas_size(_canvas_width, _canvas_height);

  // ensure that all the canvas are visible
  hide_all_canvas();
  show_all_canvas();

  // we only need to draw the image once in the image_canvas
  _img_ctx.clearRect(0, 0, _canvas_width, _canvas_height);
  _current_image.onload = function () {
    _img_ctx.drawImage(_current_image, 0, 0,
      _canvas_width, _canvas_height);
  }

  // refresh the attributes panel
  _load_canvas_regions(); // image to canvas space transform
  _redraw_reg_canvas();
  _reg_canvas.focus();
}

// Transform regions in image space to canvas space.
// Region boundaries are wrt to image scale. They need
// to be scaled appropriately to _canvas_scale before
// being drawn on the region canvas.
// _canvas_regions is a global variable
function _load_canvas_regions() {
  var regions = region_boundaries;
  _canvas_regions = [];
  for (var i = 0; i < regions.length; ++i) {
    var region_i = {};
    for (var key in regions[i]) {
      region_i[key] = regions[i][key];
    }
    _canvas_regions.push(region_i);

    var x = regions[i]['x'] / _canvas_scale;
    var y = regions[i]['y'] / _canvas_scale;
    var width = regions[i]['width'] / _canvas_scale;
    var height = regions[i]['height'] / _canvas_scale;

    _canvas_regions[i]['x'] = Math.round(x);
    _canvas_regions[i]['y'] = Math.round(y);
    _canvas_regions[i]['width'] = Math.round(width);
    _canvas_regions[i]['height'] = Math.round(height);
    _canvas_regions[i].is_user_selected = false;
  }
}

// updates currently selected region shape
// TODO: Not needed as of now; needed only when we want to draw ONLY when DRAW mode is active.
function draw_region() {
  var ui_element = document.getElementById('region_shape_rect');
  ui_element.classList.add('selected');
}

// Sets the size of 3 elements
//  - canvas panel (parent node of image and region canvases)
//  - image canvas
//  - region cavas
function set_all_canvas_size(w, h) {
  _img_canvas.height = h;
  _img_canvas.width = w;

  _reg_canvas.height = h;
  _reg_canvas.width = w;

  canvas_panel.style.height = h + 'px';
  canvas_panel.style.width = w + 'px';
}

// Sets the scale of both the canvases - image and region.
// Same scale is applied on both x and y directions and 
// both the canvases so that the regions overlay on
// top of the image appropriately while zooming in/out.
function set_all_canvas_scale(s) {
  _img_ctx.scale(s, s);
  _reg_ctx.scale(s, s);
}

function show_all_canvas() {
  canvas_panel.style.display = 'inline-block';
}

function hide_all_canvas() {
  canvas_panel.style.display = 'none';
}

function toggle_all_regions_selection(is_selected) {
  for (var i = 0; i < _canvas_regions.length; ++i) {
    _canvas_regions[i].is_user_selected = is_selected;
    // _img_metadata[_image_id].regions[i].is_user_selected = is_selected;
  }
  _is_all_region_selected = is_selected;
}

// Given a region ID, make only that region selected
function select_only_region(region_id) {
  toggle_all_regions_selection(false);
  set_region_select_state(region_id, true);
  _is_region_selected = true;
  _user_sel_region_id = region_id;
}

// Set the state of a particular region
function set_region_select_state(region_id, is_selected) {
  _canvas_regions[region_id].is_user_selected = is_selected;
  region_boundaries[region_id].is_user_selected = is_selected;
}

function show_annotation_data() {
  var hstr = '<pre>' + pack_metadata('csv').join('') + '</pre>';
  if (typeof annotation_data_window === 'undefined') {
    var window_features = 'toolbar=no,menubar=no,location=no,resizable=yes,scrollbars=yes,status=no';
    window_features += ',width=800,height=600';
    annotation_data_window = window.open('', 'Image Metadata ', window_features);
  }
  annotation_data_window.document.body.innerHTML = hstr;
}

//
// Image click handlers
//

// TODO: Is annotation mode really necessary?
// enter annotation mode on double click
// _reg_canvas.addEventListener('dblclick', function (e) {
//   _click_x0 = e.offsetX;
//   _click_y0 = e.offsetY;
//   var region_id = is_inside_region(_click_x0, _click_y0);
//   console.log(_click_x0, _click_y0);
//   if (region_id !== -1) {
//     // user clicked inside a region, show attribute panel
//     if (!_is_reg_attr_panel_visible) {
//       toggle_reg_attr_panel();
//     }
//   }

// }, false);

// MOUSEDOWN event on canvas
// implies one of these actions is being done
//  - draw a new region
//  - select / resize / move an existing region
_reg_canvas.addEventListener('mousedown', function (e) {
  _click_x0 = e.offsetX;
  _click_y0 = e.offsetY;

  // region edge has 2 pieces of information:
  // 1. region id
  // 2. corner which was clicked: 
  //    - 1: top left
  //    - 2: top right
  //    - 3: bottom right
  //    - 4: bottom left
  // if no corner was clicked, it simply returns
  // [-1, -1]
  _region_edge = is_on_region_corner(_click_x0, _click_y0);

  var region_id = is_inside_region(_click_x0, _click_y0);

  // if region is already selected, then
  //  (1) User is resizing the region if they clicked on its edge
  //  (2) User is moving the region if they clicked inside it
  //  (3) They are drawing a region if they clicked outside any of the regions
  // NOTE: Moving is only possible if they have selected the region. So if 
  //       region is not selected, they're most likely drawing a new
  //       region.
  if (_is_region_selected) {
    // if on region boundary, they're resizing the region
    if (_region_edge[1] > 0) {
      if (!_is_user_resizing_region) {
        // resize region
        if (_region_edge[0] !== _user_sel_region_id) {
          _user_sel_region_id = _region_edge[0];
        }
        _is_user_resizing_region = true;
      }
    } else {
      var yes = is_inside_this_region(_click_x0,
        _click_y0,
        _user_sel_region_id);
      // clicked inside the selected region, 
      if (yes) {
        if (!_is_user_moving_region) {
          _is_user_moving_region = true;
          _region_click_x = _click_x0;
          _region_click_y = _click_y0;
        }
      }
      // clicked out any region, they're drawing a new region
      if (region_id === -1) {
        _is_user_drawing_region = true;
        // unselect all regions
        _is_region_selected = false;
        _user_sel_region_id = -1;
        toggle_all_regions_selection(false);
      }
    }
  }
  // if no region is selected, then mousedown would indicate
  //  (1) User is drawing a region if they have clicked outside all of the regions.
  //  (2) If user clicked inside a region, they are either 
  //    (a) drawing a region or
  //    (b) selecting a region
  else {
    _is_user_drawing_region = true;
  }
  // prevent the default mousedown action from taking place
  e.preventDefault();
}, false);

// MOUSEUP event on canvas
// implements the following functionalities:
//  - Drawing a new region
//  - Moving / resizing / selecting / unselecting existing region
_reg_canvas.addEventListener('mouseup', function (e) {
  _click_x1 = e.offsetX;
  _click_y1 = e.offsetY;

  var click_dx = Math.abs(_click_x1 - _click_x0);
  var click_dy = Math.abs(_click_y1 - _click_y0);

  // user has finished moving a region
  if (_is_user_moving_region) {
    _is_user_moving_region = false;
    _reg_canvas.style.cursor = "default";
    // find out how much they have moved
    var move_x = Math.round(_click_x1 - _region_click_x);
    var move_y = Math.round(_click_y1 - _region_click_y);

    // change boundaries only if they've moved more than a tolerance limit
    if (Math.abs(move_x) > _MOUSE_CLICK_TOL ||
      Math.abs(move_y) > _MOUSE_CLICK_TOL) {

      var image_attr = region_boundaries[_user_sel_region_id];
      var canvas_attr = _canvas_regions[_user_sel_region_id];

      var xnew = image_attr['x'] + Math.round(move_x * _canvas_scale);
      var ynew = image_attr['y'] + Math.round(move_y * _canvas_scale);
      image_attr['x'] = xnew;
      image_attr['y'] = ynew;

      canvas_attr['x'] = Math.round(image_attr['x'] / _canvas_scale);
      canvas_attr['y'] = Math.round(image_attr['y'] / _canvas_scale);
    } else {
      // indicates a user click on an already selected region
      // this could indicate a user's intention to select another
      // nested region within this region

      // traverse the canvas regions in alternating ascending
      // and descending order to solve the issue of nested regions
      nested_region_id = is_inside_region(_click_x0, _click_y0, true);
      if (nested_region_id >= 0 &&
        nested_region_id !== _user_sel_region_id) {
        _user_sel_region_id = nested_region_id;
        _is_region_selected = true;
        _is_user_moving_region = false;

        _current_type = region_boundaries[_user_sel_region_id];
        _THEME_SEL_REGION_FILL_COLOR = '#000000';

        // de-select all other regions if the user has not pressed Shift
        if (!e.shiftKey) {
          toggle_all_regions_selection(false);
        }
        set_region_select_state(nested_region_id, true);
        // update_attributes_panel();
      }
    }
    _redraw_reg_canvas();
    _reg_canvas.focus();
    return;
  }

  // indicates that user has finished resizing a region
  if (_is_user_resizing_region) {
    // _click(x0,y0) to _click(x1,y1)
    _is_user_resizing_region = false;
    _reg_canvas.style.cursor = "default";
    // update the region
    var region_id = _region_edge[0];
    var image_attr = region_boundaries[region_id];
    var canvas_attr = _canvas_regions[region_id];

    // d has the canvas coordinates of the 4 points of the region
    var d = [canvas_attr['x'], canvas_attr['y'], 0, 0];
    d[2] = d[0] + canvas_attr['width'];
    d[3] = d[1] + canvas_attr['height'];

    var mx = _current_x;
    var my = _current_y;
    var preserve_aspect_ratio = false;

    // constrain (mx,my) to lie on a line connecting a diagonal of rectangle
    if (_is_ctrl_pressed) {
      preserve_aspect_ratio = true;
    }

    rect_update_corner(_region_edge[1], d, mx, my, preserve_aspect_ratio);
    // ensure (x, y) is top left coordinate
    rect_standardize_coordinates(d);

    var w = Math.abs(d[2] - d[0]);
    var h = Math.abs(d[3] - d[1]);

    image_attr['x'] = Math.round(d[0] * _canvas_scale);
    image_attr['y'] = Math.round(d[1] * _canvas_scale);
    image_attr['width'] = Math.round(w * _canvas_scale);
    image_attr['height'] = Math.round(h * _canvas_scale);

    canvas_attr['x'] = Math.round(image_attr['x'] / _canvas_scale);
    canvas_attr['y'] = Math.round(image_attr['y'] / _canvas_scale);
    canvas_attr['width'] = Math.round(image_attr['width'] / _canvas_scale);
    canvas_attr['height'] = Math.round(image_attr['height'] / _canvas_scale);

    _redraw_reg_canvas();
    _reg_canvas.focus();
    return;
  }

  // denotes a single click (= mouse down + mouse up)
  if (click_dx < _MOUSE_CLICK_TOL ||
    click_dy < _MOUSE_CLICK_TOL) {
    var region_id = is_inside_region(_click_x0, _click_y0);
    _cur_region_id = region_id;
    if (region_id >= 0) {
      // first click selects region
      _user_sel_region_id = region_id;
      _is_region_selected = true;
      _is_user_moving_region = false;
      _is_user_drawing_region = false;

      // de-select all other regions if the user has not pressed Shift
      if (!e.shiftKey) {
        toggle_all_regions_selection(false);
      }
      set_region_select_state(region_id, true);
      //show_message('Click and drag to move or resize the selected region');
    } else {
      if (_is_user_drawing_region) {
        // clear all region selection
        _is_user_drawing_region = false;
        _is_region_selected = false;
        toggle_all_regions_selection(false);
      }
    }
    _redraw_reg_canvas();
    _reg_canvas.focus();
    return;
  }

  // indicates that user has finished drawing a new region
  if (_is_user_drawing_region) {

    _is_user_drawing_region = false;

    var region_x0, region_y0, region_x1, region_y1;
    // ensure that (x0,y0) is top-left and (x1,y1) is bottom-right
    if (_click_x0 < _click_x1) {
      region_x0 = _click_x0;
      region_x1 = _click_x1;
    } else {
      region_x0 = _click_x1;
      region_x1 = _click_x0;
    }

    if (_click_y0 < _click_y1) {
      region_y0 = _click_y0;
      region_y1 = _click_y1;
    } else {
      region_y0 = _click_y1;
      region_y1 = _click_y0;
    }

    var original_img_region = {};
    var canvas_img_region = {};
    var region_dx = Math.abs(region_x1 - region_x0);
    var region_dy = Math.abs(region_y1 - region_y0);

    // newly drawn region is automatically selected
    toggle_all_regions_selection(false);
    original_img_region.is_user_selected = true;
    canvas_img_region.is_user_selected = true;
    _is_region_selected = true;
    _user_sel_region_id = _canvas_regions.length; // new region's id
    // _current_type = _img_metadata[_image_id].regions[_user_sel_region_id].shape_attributes.type;

    if (region_dx > _REGION_MIN_DIM ||
      region_dy > _REGION_MIN_DIM) { // avoid regions with 0 dim
      var x = Math.round(region_x0 * _canvas_scale);
      var y = Math.round(region_y0 * _canvas_scale);
      var width = Math.round(region_dx * _canvas_scale);
      var height = Math.round(region_dy * _canvas_scale);
      original_img_region['x'] = x;
      original_img_region['y'] = y;
      original_img_region['width'] = width;
      original_img_region['height'] = height;

      canvas_img_region['x'] = Math.round(x / _canvas_scale);
      canvas_img_region['y'] = Math.round(y / _canvas_scale);
      canvas_img_region['width'] = Math.round(width / _canvas_scale);
      canvas_img_region['height'] = Math.round(height / _canvas_scale);

      region_boundaries.push(original_img_region);
      _canvas_regions.push(canvas_img_region);
    } else {
      show_message('Cannot add such a small region');
    }
    // update_attributes_panel();
    _redraw_reg_canvas();
    _reg_canvas.focus();
    return;
  }

});


// MOUSEMOVE event
// Thi function handles:
//  - display resizing icons when hovering over corner edges of the 
//    selected region
//  - draw region on the canvas as user resizes it / draws it
//  - move region on the canvas when in moving_region mode
_reg_canvas.addEventListener('mousemove', function (e) {

  _current_x = e.offsetX;
  _current_y = e.offsetY;

  if (_is_region_selected) {
    if (!_is_user_resizing_region) {
      // check if user moved mouse cursor to region boundary
      // which indicates an intention to resize the region

      _region_edge = is_on_region_corner(_current_x, _current_y);

      if (_region_edge[0] === _user_sel_region_id) {
        switch (_region_edge[1]) {
          // rect
        case 1: // Fall-through // top-left corner of rect
        case 3: // bottom-right corner of rect
          _reg_canvas.style.cursor = "nwse-resize";
          break;
        case 2: // Fall-through // top-right corner of rect
        case 4: // bottom-left corner of rect
          _reg_canvas.style.cursor = "nesw-resize";
          break;

          // circle and ellipse
        case 5:
          _reg_canvas.style.cursor = "n-resize";
          break;
        case 6:
          _reg_canvas.style.cursor = "e-resize";
          break;

        default:
          _reg_canvas.style.cursor = "default";
          break;
        }
      } else {
        var yes = is_inside_this_region(_current_x,
          _current_y,
          _user_sel_region_id);
        if (yes) {
          _reg_canvas.style.cursor = "move";
        } else {
          _reg_canvas.style.cursor = "default";
        }
      }
    }
  }

  if (_is_user_drawing_region) {
    // draw region as the user drags the mouse cursor
    if (_canvas_regions.length) {
      _redraw_reg_canvas(); // clear old intermediate rectangle
    } else {
      // first region being drawn, just clear the full region canvas
      _reg_ctx.clearRect(0, 0, _reg_canvas.width, _reg_canvas.height);
    }

    var region_x0, region_y0;

    if (_click_x0 < _current_x) {
      if (_click_y0 < _current_y) {
        region_x0 = _click_x0;
        region_y0 = _click_y0;
      } else {
        region_x0 = _click_x0;
        region_y0 = _current_y;
      }
    } else {
      if (_click_y0 < _current_y) {
        region_x0 = _current_x;
        region_y0 = _click_y0;
      } else {
        region_x0 = _current_x;
        region_y0 = _current_y;
      }
    }
    var dx = Math.round(Math.abs(_current_x - _click_x0));
    var dy = Math.round(Math.abs(_current_y - _click_y0));

    _draw_rect_region(region_x0, region_y0, dx, dy, true);

    _reg_canvas.focus();
  }

  if (_is_user_resizing_region) {
    // user has clicked mouse on bounding box edge and is now moving it
    // draw region as the user drags the mouse coursor
    if (_canvas_regions.length) {
      _redraw_reg_canvas(); // clear old intermediate rectangle
    } else {
      // first region being drawn, just clear the full region canvas
      _reg_ctx.clearRect(0, 0, _reg_canvas.width, _reg_canvas.height);
    }

    var region_id = _region_edge[0];
    var attr = _canvas_regions[region_id];
    // original rectangle
    var d = [attr['x'], attr['y'], 0, 0];
    d[2] = d[0] + attr['width'];
    d[3] = d[1] + attr['height'];

    var mx = _current_x;
    var my = _current_y;
    var preserve_aspect_ratio = false;

    // constrain (mx,my) to lie on a line connecting a diagonal of rectangle
    if (_is_ctrl_pressed) {
      preserve_aspect_ratio = true;
    }

    rect_update_corner(_region_edge[1], d, mx, my, preserve_aspect_ratio);
    rect_standardize_coordinates(d);

    var w = Math.abs(d[2] - d[0]);
    var h = Math.abs(d[3] - d[1]);
    _draw_rect_region(d[0], d[1], w, h, true);
    _reg_canvas.focus();
  }

  if (_is_user_moving_region) {
    // draw region as the user drags the mouse coursor
    if (_canvas_regions.length) {
      _redraw_reg_canvas(); // clear old intermediate rectangle
    } else {
      // first region being drawn, just clear the full region canvas
      _reg_ctx.clearRect(0, 0, _reg_canvas.width, _reg_canvas.height);
    }

    var move_x = (_current_x - _region_click_x);
    var move_y = (_current_y - _region_click_y);
    var attr = _canvas_regions[_user_sel_region_id];

    _draw_rect_region(attr['x'] + move_x,
      attr['y'] + move_y,
      attr['width'],
      attr['height'],
      true);

    _reg_canvas.focus();
    return;
  }
});


//
// Canvas update routines
//
function _redraw_img_canvas() {
  _img_ctx.clearRect(0, 0, _img_canvas.width, _img_canvas.height);
  _img_ctx.drawImage(_current_image, 0, 0,
    _img_canvas.width, _img_canvas.height);
}

function _redraw_reg_canvas() {
  if (_canvas_regions.length > 0) {
    _reg_ctx.clearRect(0, 0, _reg_canvas.width, _reg_canvas.height);
    if (_is_region_boundary_visible) {
      draw_all_regions();
    }

    if (_is_region_id_visible) {
      draw_all_region_id();
    }
  }
}

function _clear_reg_canvas() {
  _reg_ctx.clearRect(0, 0, _reg_canvas.width, _reg_canvas.height);
}

function draw_all_regions() {
  for (var i = 0; i < _canvas_regions.length; ++i) {
    var attr = _canvas_regions[i];
    _cur_reg_drawing_id = i;
    var is_selected = _canvas_regions[i].is_user_selected;

    _draw_rect_region(attr['x'],
      attr['y'],
      attr['width'],
      attr['height'],
      is_selected);
  }
}

// control point for resize of region boundaries
function _draw_control_point(cx, cy) {
  _reg_ctx.beginPath();
  _reg_ctx.arc(cx, cy, _REGION_POINT_RADIUS, 0, 2 * Math.PI, false);
  _reg_ctx.closePath();

  _reg_ctx.fillStyle = _THEME_CONTROL_POINT_COLOR;
  _reg_ctx.globalAlpha = 1.0;
  _reg_ctx.fill();
}

function _draw_rect_region(x, y, w, h, is_selected) {
  if (is_selected) {
    _draw_rect(x, y, w, h);

    _reg_ctx.strokeStyle = _THEME_SEL_REGION_FILL_BOUNDARY_COLOR;
    _reg_ctx.lineWidth = _THEME_REGION_BOUNDARY_WIDTH;
    _reg_ctx.stroke();

    _reg_ctx.fillStyle = _THEME_SEL_REGION_FILL_COLOR;
    _reg_ctx.globalAlpha = _THEME_SEL_REGION_OPACITY;
    _reg_ctx.fill();
    _reg_ctx.globalAlpha = 1.0;

    _draw_control_point(x, y);
    _draw_control_point(x + w, y + h);
    _draw_control_point(x, y + h);
    _draw_control_point(x + w, y);
  } else {
    if (w > _THEME_REGION_BOUNDARY_WIDTH &&
      h > _THEME_REGION_BOUNDARY_WIDTH) {
      // draw a boundary line on both sides of the fill line
      _reg_ctx.strokeStyle = _THEME_BOUNDARY_LINE_COLOR;
      _reg_ctx.lineWidth = _THEME_REGION_BOUNDARY_WIDTH;
      _draw_rect(x - _THEME_REGION_BOUNDARY_WIDTH / 2,
        y - _THEME_REGION_BOUNDARY_WIDTH / 2,
        w + _THEME_REGION_BOUNDARY_WIDTH / 2,
        h + _THEME_REGION_BOUNDARY_WIDTH / 2);
      _reg_ctx.stroke();
    }
  }
}

function _draw_rect(x, y, w, h) {
  _reg_ctx.beginPath();
  _reg_ctx.moveTo(x, y);
  _reg_ctx.lineTo(x + w, y);
  _reg_ctx.lineTo(x + w, y + h);
  _reg_ctx.lineTo(x, y + h);
  _reg_ctx.closePath();
}

// prints IDs next to bounding boxes
function draw_all_region_id() {
  _reg_ctx.shadowColor = "transparent";
  for (var i = 0; i < _canvas_regions.length; ++i) {
    var canvas_reg = _canvas_regions[i];

    var bbox = get_region_bounding_box(canvas_reg);
    var x = bbox[0];
    var y = bbox[1];
    var w = Math.abs(bbox[2] - bbox[0]);
    var h = Math.abs(bbox[3] - bbox[1]);

    _reg_ctx.font = Math.floor(average_box_height / _canvas_scale) + "px" + _THEME_ATTRIBUTE_VALUE_FONT;

    var annotation_str = (i + 1).toString();
    var annotation_str_length = _reg_ctx.measureText(annotation_str).width;

    var char_width = _reg_ctx.measureText('M').width;
    var char_height = 1.8 * char_width;

    var r = _canvas_regions[i];

    x = x - annotation_str_length - char_width;
    if (x < 0) { x = 0; }
    // draw text over this background rectangle
    _reg_ctx.globalAlpha = 1.0;
    _reg_ctx.fillStyle = _THEME_REGION_ID_COLOR;
    _reg_ctx.fillText(annotation_str,
      Math.floor(x),
      // Math.floor(x + 0.4*char_width),
      Math.floor(y + 0.8 * h));

  }
}

function get_region_bounding_box(region) {
  var d = region;
  var bbox = new Array(4);

  bbox[0] = d['x'];
  bbox[1] = d['y'];
  bbox[2] = d['x'] + d['width'];
  bbox[3] = d['y'] + d['height'];

  return bbox;
}

//
// Region collision routines
//
function is_inside_region(px, py, descending_order) {
  var N = _canvas_regions.length;
  if (N === 0) {
    return -1;
  }
  var start, end, del;
  // traverse the canvas regions in alternating ascending
  // and descending order to solve the issue of nested regions
  if (descending_order) {
    start = N - 1;
    end = -1;
    del = -1;
  } else {
    start = 0;
    end = N;
    del = 1;
  }

  var i = start;
  while (i !== end) {
    var yes = is_inside_this_region(px, py, i);
    if (yes) {
      return i;
    }
    i = i + del;
  }
  return -1;
}

function is_inside_this_region(px, py, region_id) {
  var attr = _canvas_regions[region_id];
  var result = false;
  result = is_inside_rect(attr['x'],
    attr['y'],
    attr['width'],
    attr['height'],
    px, py);
  return result;
}

function is_inside_rect(x, y, w, h, px, py) {
  return px > x &&
    px < (x + w) &&
    py > y &&
    py < (y + h);
}


// returns
// >0 if (x2,y2) lies on the left side of line joining (x0,y0) and (x1,y1)
// =0 if (x2,y2) lies on the line joining (x0,y0) and (x1,y1)
// >0 if (x2,y2) lies on the right side of line joining (x0,y0) and (x1,y1)
// source: http://geomalgorithms.com/a03-_inclusion.html
function is_left(x0, y0, x1, y1, x2, y2) {
  return (((x1 - x0) * (y2 - y0)) - ((x2 - x0) * (y1 - y0)));
}

function is_on_region_corner(px, py) {
  var _region_edge = [-1, -1]; // region_id, corner_id [top-left=1,top-right=2,bottom-right=3,bottom-left=4]

  for (var i = 0; i < _canvas_regions.length; ++i) {
    var attr = _canvas_regions[i]
    var result = false;
    _region_edge[0] = i;

    result = is_on_rect_corner(attr['x'],
      attr['y'],
      attr['width'],
      attr['height'],
      px, py);
    if (result > 0) {
      _region_edge[1] = result;
      return _region_edge;
    }
  }
  _region_edge[0] = -1;
  return _region_edge;
}

function is_on_rect_corner(x, y, w, h, px, py) {
  var dx0 = Math.abs(x - px);
  var dy0 = Math.abs(y - py);
  var dx1 = Math.abs(x + w - px);
  var dy1 = Math.abs(y + h - py);

  //[top-left=1,top-right=2,bottom-right=3,bottom-left=4]
  if (dx0 < _REGION_EDGE_TOL &&
    dy0 < _REGION_EDGE_TOL) {
    return 1;
  }
  if (dx1 < _REGION_EDGE_TOL &&
    dy0 < _REGION_EDGE_TOL) {
    return 2;
  }
  if (dx1 < _REGION_EDGE_TOL &&
    dy1 < _REGION_EDGE_TOL) {
    return 3;
  }

  if (dx0 < _REGION_EDGE_TOL &&
    dy1 < _REGION_EDGE_TOL) {
    return 4;
  }
  return 0;
}

function rect_standardize_coordinates(d) {
  // d[x0,y0,x1,y1]
  // ensures that (d[0],d[1]) is top-left corner while
  // (d[2],d[3]) is bottom-right corner
  if (d[0] > d[2]) {
    // swap
    var t = d[0];
    d[0] = d[2];
    d[2] = t;
  }

  if (d[1] > d[3]) {
    // swap
    var t = d[1];
    d[1] = d[3];
    d[3] = t;
  }
}

function rect_update_corner(corner_id, d, x, y, preserve_aspect_ratio) {
  // pre-condition : d[x0,y0,x1,y1] is standardized
  // post-condition : corner is moved ( d may not stay standardized )
  if (preserve_aspect_ratio) {
    switch (corner_id) {
    case 1: // Fall-through // top-left

    case 2: // Fall-through // top-right

    case 3: // bottom-right
      var dx = d[2] - d[0];
      var dy = d[3] - d[1];
      var norm = Math.sqrt(dx * dx + dy * dy);
      var nx = dx / norm; // x component of unit vector along the diagonal of rect
      var ny = dy / norm; // y component
      var proj = (x - d[0]) * nx + (y - d[1]) * ny;
      var proj_x = nx * proj;
      var proj_y = ny * proj;
      // constrain (mx,my) to lie on a line connecting (x0,y0) and (x1,y1)
      x = Math.round(d[0] + proj_x);
      y = Math.round(d[1] + proj_y);
      break;

    case 4: // bottom-left
      var dx = d[2] - d[0];
      var dy = d[1] - d[3];
      var norm = Math.sqrt(dx * dx + dy * dy);
      var nx = dx / norm; // x component of unit vector along the diagonal of rect
      var ny = dy / norm; // y component
      var proj = (x - d[0]) * nx + (y - d[3]) * ny;
      var proj_x = nx * proj;
      var proj_y = ny * proj;
      // constrain (mx,my) to lie on a line connecting (x0,y0) and (x1,y1)
      x = Math.round(d[0] + proj_x);
      y = Math.round(d[3] + proj_y);
      break;
    }
  }

  switch (corner_id) {
  case 1: // top-left
    d[0] = x;
    d[1] = y;
    break;

  case 3: // bottom-right
    d[2] = x;
    d[3] = y;
    break;

  case 2: // top-right
    d[2] = x;
    d[1] = y;
    break;

  case 4: // bottom-left
    d[0] = x;
    d[3] = y;
    break;
  }
}

function del_sel_regions() {
  var del_region_count = 0;

  if (_is_all_region_selected) {
    del_region_count = _canvas_regions.length;
    _canvas_regions.splice(0);
    region_boundaries.splice(0);
  } else {
    var sorted_sel_reg_id = [];
    for (var i = 0; i < _canvas_regions.length; ++i) {
      if (_canvas_regions[i].is_user_selected) {
        sorted_sel_reg_id.push(i);
      }
    }
    sorted_sel_reg_id.sort(function (a, b) {
      return (b - a);
    });
    for (var i = 0; i < sorted_sel_reg_id.length; ++i) {
      _canvas_regions.splice(sorted_sel_reg_id[i], 1);
      region_boundaries.splice(sorted_sel_reg_id[i], 1);
      del_region_count += 1;
    }
  }

  _is_all_region_selected = false;
  _is_region_selected = false;
  _user_sel_region_id = -1;

  if (_canvas_regions.length === 0) {
    // all regions were deleted, hence clear region canvas
    _clear_reg_canvas();
  } else {
    _redraw_reg_canvas();
  }
  _reg_canvas.focus();

  show_message('Deleted ' + del_region_count + ' selected regions');
}

function sel_all_regions() {
  toggle_all_regions_selection(true);
  _is_all_region_selected = true;
  _redraw_reg_canvas();
}

function copy_sel_regions() {
  if (_is_region_selected ||
    _is_all_region_selected) {
    _copied_image_regions.splice(0);
    for (var i = 0; i < _img_metadata[_image_id].regions.length; ++i) {
      var img_region = _img_metadata[_image_id].regions[i];
      var canvas_region = _canvas_regions[i];
      if (canvas_region.is_user_selected) {
        _copied_image_regions.push(clone_image_region(img_region));
      }
    }
    show_message('Copied ' + _copied_image_regions.length +
      ' selected regions. Press Ctrl + v to paste');
  } else {
    show_message('Select a region first!');
  }
}

function paste_sel_regions() {
  if (_copied_image_regions.length) {
    var pasted_reg_count = 0;
    for (var i = 0; i < _copied_image_regions.length; ++i) {
      // ensure copied the regions are within this image's boundaries
      var bbox = get_region_bounding_box(_copied_image_regions[i]);
      if (bbox[2] < _current_image_width &&
        bbox[3] < _current_image_height) {
        var r = clone_image_region(_copied_image_regions[i]);
        _img_metadata[_image_id].regions.push(r);

        pasted_reg_count += 1;
      }
    }
    _load_canvas_regions();
    var discarded_reg_count = _copied_image_regions.length - pasted_reg_count;
    show_message('Pasted ' + pasted_reg_count + ' regions. ' +
      'Discarded ' + discarded_reg_count + ' regions exceeding image boundary.');
    _redraw_reg_canvas();
    _reg_canvas.focus();
  } else {
    show_message('To paste a region, you first need to select a region and copy it!');
  }
}

function reset_zoom_level() {
  if (_is_canvas_zoomed) {
    _is_canvas_zoomed = false;
    _canvas_zoom_level_index = _CANVAS_DEFAULT_ZOOM_LEVEL_INDEX;
    console.log("reset zoom level");
    var zoom_scale = _CANVAS_ZOOM_LEVELS[_canvas_zoom_level_index];
    set_all_canvas_scale(zoom_scale);
    set_all_canvas_size(_canvas_width, _canvas_height);
    _canvas_scale = _canvas_scale_without_zoom;

    _load_canvas_regions(); // image to canvas space transform
    _redraw_img_canvas();
    _redraw_reg_canvas();
    _reg_canvas.focus();
    show_message('Zoom reset');
  } else {
    show_message('Cannot reset zoom because image zoom has not been applied!');
  }
}

function zoom_in() {
  if (_canvas_zoom_level_index === (_CANVAS_ZOOM_LEVELS.length - 1)) {
    show_message('Further zoom-in not possible');
  } else {
    _canvas_zoom_level_index += 1;

    console.log("zooming in");
    _is_canvas_zoomed = true;
    var zoom_scale = _CANVAS_ZOOM_LEVELS[_canvas_zoom_level_index];
    set_all_canvas_scale(zoom_scale);
    set_all_canvas_size(_canvas_width * zoom_scale,
      _canvas_height * zoom_scale);
    // set_all_canvas_size(_canvas_width, _canvas_height);
    _canvas_scale = _canvas_scale_without_zoom / zoom_scale;

    _load_canvas_regions(); // image to canvas space transform
    _redraw_img_canvas();
    _redraw_reg_canvas();
    _reg_canvas.focus();
    show_message('Zoomed in to level ' + zoom_scale + 'X');
  }
}

function zoom_out() {
  if (_canvas_zoom_level_index === 0) {
    show_message('Further zoom-out not possible');
  } else {
    _canvas_zoom_level_index -= 1;
    console.log("zooming out");
    _is_canvas_zoomed = true;
    var zoom_scale = _CANVAS_ZOOM_LEVELS[_canvas_zoom_level_index];
    set_all_canvas_scale(zoom_scale);
    set_all_canvas_size(_canvas_width * zoom_scale,
      _canvas_height * zoom_scale);
    _canvas_scale = _canvas_scale_without_zoom / zoom_scale;

    _load_canvas_regions(); // image to canvas space transform
    _redraw_img_canvas();
    _redraw_reg_canvas();
    _reg_canvas.focus();
    show_message('Zoomed out to level ' + zoom_scale + 'X');
  }
}

function toggle_region_boundary_visibility() {
  _is_region_boundary_visible = !_is_region_boundary_visible;
  _redraw_reg_canvas();
  _reg_canvas.focus();
}

function toggle_region_id_visibility() {
  _is_region_id_visible = !_is_region_id_visible;
  _redraw_reg_canvas();
  _reg_canvas.focus();
}

// Once bounding boxes have been added / modified and
// the page is ready for OCR phase, a file containing
// the bounding box coordinates is made and saved to the 
// server
function save_segmentation() {
  var sorted_region_boundaries = sort_region_boundaries();
  var all_region_data = pack_data(sorted_region_boundaries);
  // console.log(all_region_data);
  var blob_attr = { type: 'text/csv;charset=utf-8' };
  var all_region_data_blob = new Blob(all_region_data, blob_attr);

  upload_seg_file(all_region_data_blob);
  // create a href element with the URL to the 
  // generated .txt file
  // var a = document.createElement('a');
  // a.href = URL.createObjectURL(all_region_data_blob);
  // a.target = '_blank';
  // a.download = "region_data.txt"

  // // simulate a mouse click event
  // var event = new MouseEvent('click', {
  //   view: window,
  //   bubbles: true,
  //   cancelable: true
  // });

  // a.dispatchEvent(event);

}

// When region boundaries are saved to the file
// they are sorted based on their y-coordinates so
// that the IDs are increasing as we go down the page.
// This will be useful during editing OCR output.
function sort_region_boundaries() {
  var new_region_boundaries = region_boundaries.concat().sort(
    function (a, b) {
      return a.y - b.y;
    });
  return new_region_boundaries;
}

function pack_data(_region_boundaries) {
  var data = [];
  var r = _region_boundaries;

  if (r.length !== 0) {
    for (var i = 0; i < r.length; ++i) {
      var line = [];
      var r_i = r[i];
      line.push(r[i].x);
      line.push(r[i].y);
      line.push(r[i].width);
      line.push(r[i].height);
      data.push(line.join(_CSV_SEP) + "\n");
    }
  }
  return data;
}

function upload_seg_file(upload_file_blob) {
  var form_data = new FormData();
  var image_name = image_url.split("/").pop().split(".")[0]
  form_data.append('segmentation_plot_file', upload_file_blob, image_name + "_seg_plot_image.txt");
  var form = document.getElementById("upload_seg_plot_file_form");
  form_data.append('csrfmiddlewaretoken', form.csrfmiddlewaretoken.value);
  $.ajax({
    url: form.action,
    type: form.method,
    data: form_data,
    processData: false,
    contentType: false,
    success: function (data) {
      window.location = data.url;
      window.location.reload(true);
    },
    error: function (xhr) {
      alert(xhr.statusText);
    },
  });
}

// Buttons remain focused even after mouseup.
// Manually blurring them after every mouseup event.
$(".btn-man-seg").mouseup(function () {
  $(this).blur();
})