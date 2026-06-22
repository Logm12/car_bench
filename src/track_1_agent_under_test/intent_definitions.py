from enum import Enum

class ViviIntent(Enum):
    AUDIO_CONTROL = "audio_control"
    BODY_CONTROL = "body_control"
    CHECK_TRAFFIC = "check_traffic"
    CLIMATE_CONTROL = "climate_control"
    COMFORT_CONTROL = "comfort_control"
    COMPUTE_ROUTES = "compute_routes"
    CONNECTIVITY_CONTROL = "connectivity_control"
    DISPLAY_CONTROL = "display_control"
    DRIVE_SYSTEM = "drive_system"
    LIFESTYLE = "lifestyle"
    LIGHT_CONTROL = "light_control"
    MAP_CONTROL = "map_control"
    MEDIA_CONTROL = "media_control"
    MOVIE = "movie"
    NEWS_SEARCH = "news_search"
    PHONE_MANAGER = "phone_manager"
    SAVED_PLACES = "saved_places"
    SEARCH_PLACES = "search_places"
    SEAT_CONTROL = "seat_control"
    SOFTWARE_RELEASE = "software_release"
    VEHICLE_TROUBLESHOOT = "vehicle_troubleshoot"
    VINFAST_KB = "vinfast_kb"
    WEATHER = "weather"
    WEB_SEARCH = "web_search"
    ZODIAC = "zodiac"

VIVI_INTENT_DESCRIPTIONS = {
    ViviIntent.AUDIO_CONTROL: "Control audio volume, mute state, or sound sources.",
    ViviIntent.BODY_CONTROL: "Control physical car parts such as doors, windows, trunk, sunroof, etc.",
    ViviIntent.CHECK_TRAFFIC: "Query traffic congestion, conditions, or routes info.",
    ViviIntent.CLIMATE_CONTROL: "Adjust climate settings, temperature, fan speed, airflow direction, air conditioning, recirculation, etc.",
    ViviIntent.COMFORT_CONTROL: "Control luxury/comfort features such as perfume diffuser or ambient lights.",
    ViviIntent.COMPUTE_ROUTES: "Calculate distance, duration, or travel time for route segments.",
    ViviIntent.CONNECTIVITY_CONTROL: "Manage Wi-Fi, cellular, hotspot, Bluetooth, etc.",
    ViviIntent.DISPLAY_CONTROL: "Adjust central screen brightness, themes, dark mode, or screensavers.",
    ViviIntent.DRIVE_SYSTEM: "Query or configure driving modes, battery capacity, battery status, or vehicle ranges.",
    ViviIntent.LIFESTYLE: "Search for points of interest like restaurants, cafes, hotels, or recommendations.",
    ViviIntent.LIGHT_CONTROL: "Manage headlights, low beams, high beams, fog lights, reading lights, or cabin lights.",
    ViviIntent.MAP_CONTROL: "Manage map views, orientation, 2D/3D selection, or map zooming.",
    ViviIntent.MEDIA_CONTROL: "Control audio/video playback (play, pause, skip, rewind).",
    ViviIntent.MOVIE: "Query movie theaters, showtimes, schedules, or titles.",
    ViviIntent.NEWS_SEARCH: "Search for online news articles, headlines, or RSS updates.",
    ViviIntent.PHONE_MANAGER: "Manage phone calling, messaging, contact details, call logs, sync, etc.",
    ViviIntent.SAVED_PLACES: "Manage favorite locations or quick-access waypoints.",
    ViviIntent.SEARCH_PLACES: "Search addresses, specific POI names, or locations.",
    ViviIntent.SEAT_CONTROL: "Control seat adjustments, heating, cooling, or ventilation.",
    ViviIntent.SOFTWARE_RELEASE: "Query or install firmware updates (FOTA) for the vehicle.",
    ViviIntent.VEHICLE_TROUBLESHOOT: "Query error warning meanings, troubleshoot car issues, or search error guides.",
    ViviIntent.VINFAST_KB: "Retrieve instructions, manual information, or user guide info specifically for VinFast vehicles.",
    ViviIntent.WEATHER: "Search weather forecasts, parameters, temperatures for specified locations.",
    ViviIntent.WEB_SEARCH: "Perform generic web search queries.",
    ViviIntent.ZODIAC: "Retrieve daily horoscope or zodiac descriptions."
}
