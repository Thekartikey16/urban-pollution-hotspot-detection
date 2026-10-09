from http.server import BaseHTTPRequestHandler
import json
import os


class handler(BaseHTTPRequestHandler):

    def do_GET(self):

        # ==========================================
        # LOAD SUMMARY DATA
        # ==========================================

        data_dir = os.path.join(
            os.path.dirname(__file__),
            "..", "public", "data"
        )

        summary_path = os.path.join(
            data_dir, "summary.json"
        )

        try:

            with open(summary_path, "r") as f:
                summary = json.load(f)

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
                    "project": "P_286 Urban Pollution Hotspot Detection",
                    "summary": summary
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
