"""Map data is rendered client-side with Leaflet (see static/js/maps.js); this module builds its GeoJSON."""


def recommendations_geojson(recs):
    return {"type": "FeatureCollection", "features": [
        {"type": "Feature", "geometry": {"type": "Point", "coordinates": [r["longitude"], r["latitude"]]},
         "properties": {"rank": r["rank"], "area": r["area"], "score": r["score"]}} for r in recs]}
