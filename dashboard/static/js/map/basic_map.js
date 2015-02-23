function initBasicMap(map_div) {
    var map = new L.Map(map_div);
    var url = "http://{s}.trimet.org"+
        "/tilecache/tilecache.py/1.0.0/currentOSM/{z}/{x}/{y}";
    var options = {
            minZoom: 8,
            maxZoom: 20,
            attribution:"Map data &copy; 2015 Oregon Metro " +
                "and <a href='http://openstreetmap.org'>OpenStreetMap</a> contributors",
            subdomains:["tilea", "tileb", "tilec", "tiled"]
    };
    map.setView(new L.LatLng(45.5, -122.5),11);
    map.addLayer(L.tileLayer(url, options));
    return map;
}

