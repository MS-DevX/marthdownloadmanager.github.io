#!/usr/bin/env python3
"""
Threaded SPA Server with Hot Reload (SSE) for MDM Website.
- Serves static assets and falls back to index.html for SPA routes.
- Provides /livereload SSE endpoint to auto-refresh connected browsers on file changes.
- Uses SO_REUSEADDR and SO_REUSEPORT for instant port reuse.
"""

import http.server
import socketserver
import socket
import os
import sys
import time
import threading

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

clients = []
clients_lock = threading.Lock()

def get_latest_mtime():
    latest = 0.0
    for root, dirs, files in os.walk(DIRECTORY):
        if any(part.startswith(".") for part in root.split(os.sep)):
            continue
        for f in files:
            if f.endswith((".html", ".js", ".css", ".svg", ".png", ".jpg", ".json")):
                p = os.path.join(root, f)
                try:
                    m = os.path.getmtime(p)
                    if m > latest:
                        latest = m
                except OSError:
                    pass
    return latest

def file_watcher():
    last_mtime = get_latest_mtime()
    while True:
        time.sleep(0.4)
        current_mtime = get_latest_mtime()
        if current_mtime > last_mtime:
            last_mtime = current_mtime
            timestamp = time.strftime("%H:%M:%S")
            print(f"[Hot Reload] File change detected at {timestamp}, reloading clients...")
            with clients_lock:
                for q in list(clients):
                    try:
                        q.append("reload")
                    except Exception:
                        pass

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    daemon_threads = True
    allow_reuse_address = True

    def server_bind(self):
        if hasattr(socket, 'SO_REUSEPORT'):
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        super().server_bind()

class SPAHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_GET(self):
        path = self.path.split("?")[0].split("#")[0]

        if path == "/livereload":
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache, no-transform")
            self.send_header("Connection", "keep-alive")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

            q = []
            with clients_lock:
                clients.append(q)

            try:
                self.wfile.write(b"data: connected\n\n")
                self.wfile.flush()

                while True:
                    time.sleep(0.1)
                    if q:
                        msg = q.pop(0)
                        self.wfile.write(f"data: {msg}\n\n".encode("utf-8"))
                        self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError, OSError):
                pass
            finally:
                with clients_lock:
                    if q in clients:
                        clients.remove(q)
            return

        local_path = os.path.join(DIRECTORY, path.lstrip("/"))
        if not os.path.exists(local_path) and not any(path.endswith(ext) for ext in [".js", ".css", ".svg", ".png", ".jpg", ".ico", ".json", ".woff", ".woff2", ".ttf"]):
            self.path = "/index.html"

        return super().do_GET()

    def do_POST(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(b"{\"status\":\"ok\"}")

    def log_message(self, format, *args):
        # Suppress noisy GET /livereload logs
        if len(args) > 0 and isinstance(args[0], str) and "/livereload" in args[0]:
            return
        sys.stderr.write("%s - - [%s] %s\n" % (self.client_address[0], self.log_date_time_string(), format % args))

def main():
    watcher = threading.Thread(target=file_watcher, daemon=True)
    watcher.start()

    with ThreadedTCPServer(("0.0.0.0", PORT), SPAHandler) as httpd:
        print(f"MDM Website running with Hot Reload at: http://localhost:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")

if __name__ == "__main__":
    main()
