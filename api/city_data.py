from http.server import BaseHTTPRequestHandler
import json
import os
from urllib.parse import urlparse, parse_qs


class handler(BaseHTTPRequestHandler):

    def do_GET(self):

        # ==========================================
        # PARSE QUERY PARAMETERS
        # ==========================================

        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        city_filter = params.get(
            "city", [None]
        )[0]

        # ==========================================
        # LOAD DATA
        # ==========================================

        data_dir = os.path.join(
            os.path.dirname(__file__),
            "..", "public", "data"
        )

        try:

            # Load city stats
            with open(
                os.path.join(
                    data_dir, "city_stats.json"
                ), "r"
            ) as f:
                city_stats = json.load(f)

            # Load city pollution
            with open(
                os.path.join(
                    data_dir, "city_pollution.json"
                ), "r"
            ) as f:
                city_pollution = json.load(f)

            # Filter by city if specified
            if city_filter and city_filter != "All":

                city_stats = [
                    c for c in city_stats
                    if c["city"] == city_filter
                ]

                city_pollution = [
                    c for c in city_pollution
                    if c["city"] == city_filter
                ]

            self.send_response(200)

            self.send_header(
                "Content-Type",
                "application/json"
            )

            self.send_header(
                "Access-Control-Allow-Origin",
                "*"
            )

            self.end_headers()

            self.wfile.write(
                json.dumps({
                    "status": "ok",
                    "city_stats": city_stats,
                    "city_pollution": city_pollution
                }).encode()
            )

        except Exception as e:

            self.send_response(500)

            self.send_header(
                "Content-Type",
                "application/json"
            )

            self.end_headers()

            self.wfile.write(
                json.dumps({
                    "status": "error",
                    "message": str(e)
                }).encode()
            )
