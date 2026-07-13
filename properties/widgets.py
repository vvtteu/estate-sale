from django import forms
from django.contrib.gis.geos import Point
from django.utils.safestring import mark_safe

class LocationPickerWidget(forms.TextInput):
    """
    Карта (Leaflet + OpenStreetMap) для выбора точки местоположения.
 
    - Клик по карте -> ставит маркер, сохраняет координаты в скрытое
      текстовое поле (в формате "lat,lng"), и через Nominatim reverse-geocoding
      заполняет соседние поля формы: address, city, district.
    - Строка поиска сверху -> forward-geocoding: вписал адрес -> карта сама
      находит точку и переносит туда маркер.
    - Все автозаполненные поля остаются обычными редактируемыми input'ами.
    """
 
    class Media:
        css = {"all": ("https://unpkg.com/leaflet@1.9.4/dist/leaflet.css",)}
        js = ("https://unpkg.com/leaflet@1.9.4/dist/leaflet.js",)
 
    def __init__(
        self,
        address_field="address",
        city_field="city",
        district_field="district",
        default_lat=41.7151,  
        default_lng=44.8271,
        default_zoom=12,
        attrs=None,
    ):
        self.address_field = address_field
        self.city_field = city_field
        self.district_field = district_field
        self.default_lat = default_lat
        self.default_lng = default_lng
        self.default_zoom = default_zoom
        super().__init__(attrs)
 
    def format_value(self, value):
        if value is None or value == "":
            return ""
        if hasattr(value, "y") and hasattr(value, "x"):
            return f"{value.y},{value.x}"
        return value
 
    def render(self, name, value, attrs=None, renderer=None):
        attrs = attrs or {}
        value = self.format_value(value)
        widget_id = attrs.get("id", f"id_{name}")
        map_id = f"{widget_id}_map"
        search_id = f"{widget_id}_search"
 
        lat, lng, has_value = "", "", "false"
        if value:
            try:
                lat_s, lng_s = value.split(",")
                lat, lng = float(lat_s), float(lng_s)
                has_value = "true"
            except (ValueError, AttributeError):
                lat, lng = "", ""
 
        hidden_input = super().render(name, value, attrs)
        start_lat = lat if lat != "" else self.default_lat
        start_lng = lng if lng != "" else self.default_lng
 
        html = f"""
        <div class="location-picker" style="max-width: 760px;">
            <input type="text" id="{search_id}" placeholder="Введите адрес и нажмите Enter для поиска..."
                   style="width:100%; margin-bottom:8px; padding:8px; border:1px solid #d1d5db; border-radius:6px;" />
            <div id="{map_id}" style="height: 420px; border-radius: 8px;"></div>
            <p style="font-size:12px; color:#6b7280; margin-top:6px;">
                Кликните на карте, чтобы поставить точку — адрес, город и район заполнятся автоматически.
            </p>
            {hidden_input}
        </div>
        <script>
        (function() {{
            function initMap_{widget_id}() {{
                if (typeof L === 'undefined') {{ setTimeout(initMap_{widget_id}, 100); return; }}
 
                var map = L.map('{map_id}').setView([{start_lat}, {start_lng}], {self.default_zoom});
                L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                    attribution: '&copy; OpenStreetMap contributors',
                    maxZoom: 19
                }}).addTo(map);
 
                var marker = {("null" if has_value == "false" else f"L.marker([{start_lat}, {start_lng}]).addTo(map)")};
 
                function setHiddenValue(lat, lng) {{
                    document.getElementById('{widget_id}').value = lat + ',' + lng;
                }}
 
                function fillAddressFields(data) {{
                    var a = data.address || {{}};
                    var city = a.city || a.town || a.village || a.municipality || a.state || '';
                    var district = a.suburb || a.city_district || a.district || a.county || '';
 
                    // Собираем короткий адрес сами: улица + номер дома
                    var road = a.road || a.pedestrian || a.footway || '';
                    var houseNumber = a.house_number || '';
                    var addr = road ? (houseNumber ? (road + ', ' + houseNumber) : road) : '';
 
                    var addressInput = document.getElementById('id_{self.address_field}');
                    var cityInput = document.getElementById('id_{self.city_field}');
                    var districtInput = document.getElementById('id_{self.district_field}');
 
                    if (addressInput) addressInput.value = addr;
                    if (cityInput) cityInput.value = city;
                    if (districtInput) districtInput.value = district;
                }}
 
                function reverseGeocode(lat, lng) {{
                    fetch('https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=' + lat + '&lon=' + lng + '&accept-language=ru')
                        .then(function(r) {{ return r.json(); }})
                        .then(fillAddressFields)
                        .catch(function(e) {{ console.error('Geocoding error', e); }});
                }}
 
                function placeMarker(lat, lng) {{
                    if (marker) {{
                        marker.setLatLng([lat, lng]);
                    }} else {{
                        marker = L.marker([lat, lng]).addTo(map);
                    }}
                    setHiddenValue(lat, lng);
                    reverseGeocode(lat, lng);
                }}
 
                map.on('click', function(e) {{
                    placeMarker(e.latlng.lat, e.latlng.lng);
                }});
 
                var searchInput = document.getElementById('{search_id}');
                searchInput.addEventListener('keydown', function(e) {{
                    if (e.key === 'Enter') {{
                        e.preventDefault();
                        var query = searchInput.value.trim();
                        if (!query) return;
                        fetch('https://nominatim.openstreetmap.org/search?format=jsonv2&q=' + encodeURIComponent(query) + '&accept-language=ru&limit=1')
                            .then(function(r) {{ return r.json(); }})
                            .then(function(results) {{
                                if (!results.length) {{ alert('Адрес не найден'); return; }}
                                var res = results[0];
                                map.setView([res.lat, res.lon], 16);
                                placeMarker(parseFloat(res.lat), parseFloat(res.lon));
                            }});
                    }}
                }});
 
                setTimeout(function() {{ map.invalidateSize(); }}, 300);
            }}
            initMap_{widget_id}();
        }})();
        </script>
        """
        return mark_safe(html)
 
 
class LocationFormField(forms.CharField):
    """Поле формы, конвертирующее 'lat,lng' <-> GEOS Point для PointField модели."""
 
    def to_python(self, value):
        if not value:
            return None
        try:
            lat_str, lng_str = value.split(",")
            lat, lng = float(lat_str), float(lng_str)
        except (ValueError, AttributeError):
            raise forms.ValidationError("Некорректные координаты точки на карте.")
        return Point(lng, lat, srid=4326)
 
    def prepare_value(self, value):
        if hasattr(value, "y") and hasattr(value, "x"):
            return f"{value.y},{value.x}"
        return value