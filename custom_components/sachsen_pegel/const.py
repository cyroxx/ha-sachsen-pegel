from datetime import timedelta

DOMAIN = "sachsen_pegel"

CONF_BASE_URL = "base_url"
CONF_STATION_ID = "station_id"

DEFAULT_BASE_URL = "https://sachsen-pegel-proxy.vercel.app"
SCAN_INTERVAL = timedelta(minutes=5)
REQUEST_TIMEOUT = 30
