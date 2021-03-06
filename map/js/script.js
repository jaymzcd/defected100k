
var map;
var mapBounds = new OpenLayers.Bounds( 0.0, -15072.0, 15216.0, 0.0);
var mapMinZoom = 1;
var mapMaxZoom = 6;

var close_markers;
var far_markers;
var close_size = new OpenLayers.Size(144, 144);
var far_size = new OpenLayers.Size(63, 100);
var close_offset = new OpenLayers.Pixel(-(close_size.w/2), -(close_size.h/2));
var far_offset = new OpenLayers.Pixel(-(far_size.w/2), -far_size.h);
var close_icon = new OpenLayers.Icon('images/close_marker.png', close_size, close_offset);
var far_icon = new OpenLayers.Icon('images/far_marker.png', far_size, far_offset);

// avoid pink tiles
OpenLayers.IMAGE_RELOAD_ATTEMPTS = 3;
OpenLayers.Util.onImageLoadErrorColor = "transparent";

function zoomChanged(e) {
    // When we get far enough out we want to show the defected style pins rather
    // than the encompassing "outline" overlay
    console.log(e);
    try {
        if(e.object.zoom < 3) {
            far_markers.setVisibility(true);
            close_markers.setVisibility(false);
        } else {
            far_markers.setVisibility(false);
            close_markers.setVisibility(true);
        }
    } catch(err) {
        console.log(err);
        // pass
    }
}

function init() {
    var options = {
        controls: [],
        maxExtent: new OpenLayers.Bounds(  0.0, -15072.0, 15216.0, 0.0 ),
        maxResolution: 64.000000,
        numZoomLevels: 7,
        theme: null
    };

    map = new OpenLayers.Map('map', options);
    map.getMinZoom = function () {
        return 1;
    }

    map.events.register("zoomend", map, zoomChanged);

    var layer = new OpenLayers.Layer.TMS( "TMS Layer","",
        {  url: '', serviceVersion: '.', layername: '.', alpha: true,
        type: 'png', getURL: overlay_getTileURL
    });
    map.addLayer(layer);
    map.zoomToExtent( mapBounds );

    map.addControl(new OpenLayers.Control.PanZoomBar());
    map.addControl(new OpenLayers.Control.MouseDefaults());
    map.addControl(new OpenLayers.Control.KeyboardDefaults());

    close_markers = new OpenLayers.Layer.Markers("Markers");
    map.addLayer(close_markers);
    far_markers = new OpenLayers.Layer.Markers("Markers");
    map.addLayer(far_markers);
}

function overlay_getTileURL(bounds) {
    var res = this.map.getResolution();
    var x = Math.round((bounds.left - this.maxExtent.left) / (res * this.tileSize.w));
    var y = Math.round((bounds.bottom - this.maxExtent.bottom) / (res * this.tileSize.h));
    var z = this.map.getZoom();
    if (x >= 0 && y >= 0) {
        return this.url + "weare/" + z + "/" + x + "/" + y + "." + this.type;
    } else {
        return "http://www.maptiler.org/img/none.png";
    }
}

function getWindowHeight() {
    if (self.innerHeight) return self.innerHeight;
    if (document.documentElement && document.documentElement.clientHeight)
        return document.documentElement.clientHeight;
    if (document.body) return document.body.clientHeight;
    return 0;
}

function getWindowWidth() {
    if (self.innerWidth) return self.innerWidth;
    if (document.documentElement && document.documentElement.clientWidth)
        return document.documentElement.clientWidth;
    if (document.body) return document.body.clientWidth;
    return 0;
}

function resize() {
    var map_element = document.getElementById("map");
    map_element.style.height = getWindowHeight() + "px";
    map_element.style.width = getWindowWidth() + "px";
    if (map_element.updateSize) { map_element.updateSize(); };
}

function addMarker(tilex, tiley) {
    // add a marker for the avatar image at x, y in tile space - these
    // are 48px square

    var tilesize = 48;
    close_markers.addMarker(
        new OpenLayers.Marker(
            new OpenLayers.LonLat(tilesize * tilex + (tilesize/2), -1 * tilesize * tiley - (tilesize/2)),
            close_icon.clone()
        )
    );
    far_markers.addMarker(
        new OpenLayers.Marker(
            new OpenLayers.LonLat(tilesize * tilex + (tilesize/2), -1 * tilesize * tiley - (tilesize/2)),
            far_icon.clone()
        )
    );
}

onresize=function(){ resize(); };

$(document).ready(function() {

    $('#lookup-form').submit(function (){
        if($('#twitterHandle').val() == '') {
            return false;
        }

        $.getJSON('lookup.php', {handle: $('#twitterHandle').val().replace('@', '')}, function(data) {
            $('#whereAmIBox').modal('hide');
            $('#twitterHandle').val('');

            if(data) {
                addMarker(data.xpos, data.ypos);
                map.setCenter(new OpenLayers.LonLat(48 * data.xpos, -1 * 48 * data.ypos ), 6);
                $('#enterCompetition').modal('show');
            } else {
                $('#cantFindYou').modal('show');
            }

        });
        return false;
    });

$('#OpenLayers.Control.PanZoomBar_113_panup_innerImage').attr('src', 'http://www.openlayers.org/api/2.7/img/south-mini.png');

});
