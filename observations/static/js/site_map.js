"use strict";
// NOTE: several constants are set in the parent HTML template:
// Icon classes (note that URLs are injected into the base template.)
// geoserverUrl
// layerName
// penguinIconUrl
// camerasJson
const geoserver_wmts_url = geoserverUrl + "/gwc/service/wmts?service=WMTS&request=GetTile&version=1.0.0&tilematrixset=mercator&tilematrix=mercator:{z}&tilecol={x}&tilerow={y}&format=image/png";

// Base tile layer
const baseLayer = L.tileLayer(
  geoserver_wmts_url + "&layer=" + layerName,
);

// Penguin icon
var penguinIcon = L.icon({
  iconUrl: penguinIconUrl,
  iconSize: [50, 50],
  iconAnchor: [25, 50],
  popupAnchor: [10, -50],
});

// Define map and add the base layer
var map = L.map("map", {
  crs: L.CRS.EPSG3857,
  center: [-32.305, 115.695],
  zoom: 16,
  minZoom: 12,
  maxZoom: 20,
  attributionControl: false,
});
baseLayer.addTo(map);
