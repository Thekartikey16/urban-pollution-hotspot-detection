# ==========================================
# P_286 - LOCAL DEVELOPMENT SERVER
# Serves the dashboard locally on localhost
# Mimics Vercel's routing behavior
# ==========================================
#
# Usage:
#   python local_server.py
#
# Then open: http://localhost:8000
# ==========================================

import http.server
import socketserver
import os
import json
import sys
from urllib.parse import urlparse, parse_qs


# ==========================================
# CONFIGURATION
# ==========================================

PORT = 8000

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

PUBLIC_DIR = os.path.join(BASE_DIR, "public")

DATA_DIR = os.path.join(PUBLIC_DIR, "data")


# ==========================================
# REQUEST HANDLER
# ==========================================

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    """
    Custom handler that mimics Vercel's routing:
    - /data/*         -> public/data/* (static JSON)
    - /api/summary    -> api/summary.py logic
    - /api/city_data  -> api/city_data.py logic
    - /api/map_data   -> api/map_data.py logic
    - /*.css|js|json  -> public/* (static assets)
    - /*              -> public/index.html (SPA fallback)
    """

    def __init__(self, *args, **kwargs):

        super().__init__(
            *args,
            directory=PUBLIC_DIR,
            **kwargs
        )

    def do_GET(self):

        parsed = urlparse(self.path)
        path = parsed.path

        # ==========================================
        # API ROUTES
        # ==========================================

        if path.startswith("/api/"):
            self.handle_api_route(path, parsed.query)
            return

        # ==========================================
        # DATA ROUTES -> Serve static JSON
        # ==========================================

        if path.startswith("/data/"):

            file_path = os.path.join(
                PUBLIC_DIR, path.lstrip("/")
            )

            if os.path.isfile(file_path):
                self.serve_json_file(file_path)
                return

            self.send_error(404, "Data file not found")
            return

        # ==========================================
        # STATIC ASSETS (css, js, etc.)
        # ==========================================

        static_extensions = (
            ".css", ".js", ".json", ".png",
            ".jpg", ".ico", ".svg"
        )

        if any(path.endswith(ext) for ext in static_extensions):

            # SimpleHTTPRequestHandler serves
            # from PUBLIC_DIR automatically
            super().do_GET()
            return

        # ==========================================
        # SPA FALLBACK -> index.html
        # ==========================================

        self.path = "/index.html"
        super().do_GET()

    # ==========================================
    # API HANDLER
    # ==========================================

    def handle_api_route(self, path, query_string):

        params = parse_qs(query_string)

        city_filter = params.get(
            "city", [None]
        )[0]

        try:

            # ----------------------------------
            # /api/summary
            # ----------------------------------

            if path == "/api/summary":

                summary_path = os.path.join(
                    DATA_DIR, "summary.json"
                )

                with open(summary_path, "r") as f:
                    summary = json.load(f)

                self.send_json_response({
                    "status": "ok",
                    "project": "P_286 Urban Pollution Hotspot Detection",
                    "summary": summary
                })

                return

            # ----------------------------------
            # /api/city_data
            # ----------------------------------

            if path == "/api/city_data":

                with open(
                    os.path.join(
                        DATA_DIR, "city_stats.json"
                    ), "r"
                ) as f:
                    city_stats = json.load(f)

                with open(
                    os.path.join(
                        DATA_DIR, "city_pollution.json"
                    ), "r"
                ) as f:
                    city_pollution = json.load(f)

                if city_filter and city_filter != "All":

                    city_stats = [
                        c for c in city_stats
                        if c["city"] == city_filter
                    ]

                    city_pollution = [
                        c for c in city_pollution
                        if c["city"] == city_filter
                    ]

                self.send_json_response({
                    "status": "ok",
                    "city_stats": city_stats,
                    "city_pollution": city_pollution
                })

                return

            # ----------------------------------
            # /api/map_data
            # ----------------------------------

            if path == "/api/map_data":

                with open(
                    os.path.join(
                        DATA_DIR, "map_points.json"
                    ), "r"
                ) as f:
                    points = json.load(f)

                if city_filter and city_filter != "All":

                    points = [
                        p for p in points
                        if p["city"] == city_filter
                    ]

                self.send_json_response({
                    "status": "ok",
                    "total": len(points),
                    "points": points
                })

                return

            # ----------------------------------
            # Unknown API route
            # ----------------------------------

            self.send_json_response(
                {
                    "status": "error",
                    "message": f"Unknown API route: {path}"
                },
                status_code=404
            )

        except Exception as e:

            self.send_json_response(
                {
                    "status": "error",
                    "message": str(e)
                },
                status_code=500
            )

    # ==========================================
    # HELPERS
    # ==========================================

    def send_json_response(
        self, data, status_code=200
    ):

        response = json.dumps(data).encode("utf-8")

        self.send_response(status_code)

        self.send_header(
            "Content-Type",
            "application/json"
        )

        self.send_header(
            "Access-Control-Allow-Origin",
            "*"
        )

        self.send_header(
            "Content-Length",
            str(len(response))
        )

        self.end_headers()

        self.wfile.write(response)

    def serve_json_file(self, file_path):

        with open(file_path, "rb") as f:
            content = f.read()

        self.send_response(200)

        self.send_header(
            "Content-Type",
            "application/json"
        )

        self.send_header(
            "Access-Control-Allow-Origin",
            "*"
        )

        self.send_header(
            "Content-Length",
            str(len(content))
        )

        self.end_headers()

        self.wfile.write(content)

    def log_message(self, format, *args):
        """Custom log formatting."""

        sys.stdout.write(
            f"  [{self.log_date_time_string()}] "
            f"{format % args}\n"
        )


# ==========================================
# START SERVER
# ==========================================

if __name__ == "__main__":

    print()
    print("==========================================")
    print("P_286 LOCAL DEVELOPMENT SERVER")
    print("==========================================")
    print()

    # Check if data files exist
    required_files = [
        "summary.json",
        "map_points.json",
        "city_stats.json",
        "city_pollution.json",
        "hotspot_table.json"
    ]

    missing = [
        f for f in required_files
        if not os.path.isfile(
            os.path.join(DATA_DIR, f)
        )
    ]

    if missing:

        print("  WARNING: Missing data files:")

        for f in missing:
            print(f"    - public/data/{f}")

        print()
        print("  Run 'python prepare_deploy_data.py'")
        print("  to generate the data files first.")
        print()

    print(f"  Serving on: http://localhost:{PORT}")
    print(f"  Static dir: {PUBLIC_DIR}")
    print()
    print("  Press Ctrl+C to stop")
    print("==========================================")
    print()

    with socketserver.TCPServer(
        ("", PORT), DashboardHandler
    ) as httpd:

        try:
            httpd.serve_forever()

        except KeyboardInterrupt:
            print("\n  Server stopped.")
            httpd.server_close()
