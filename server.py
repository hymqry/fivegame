import json
import os
import sys
import socket
from http.server import HTTPServer, BaseHTTPRequestHandler

from board import Board, BOARD_SIZE, EMPTY, BLACK, WHITE
from win_check import check_win
from ai import get_ai_move

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")

MIME_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
}


class Game:
    def __init__(self, mode="pvp"):
        self.board = Board()
        self.current_player = BLACK
        self.game_over = False
        self.winner = EMPTY
        self.mode = mode

    def play(self, row, col):
        if self.game_over:
            return False
        if not self.board.place(row, col, self.current_player):
            return False
        if check_win(self.board, row, col, self.current_player):
            self.game_over = True
            self.winner = self.current_player
            return True
        if self.board.is_full():
            self.game_over = True
            self.winner = EMPTY
            return True
        self.current_player = WHITE if self.current_player == BLACK else BLACK
        return True


game = Game()


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self._serve_file("index.html")
        elif self.path == "/qr":
            self._serve_qr_page()
        elif self.path == "/css/style.css":
            self._serve_file("css/style.css")
        elif self.path == "/js/game.js":
            self._serve_file("js/game.js")
        elif self.path == "/js/api.js":
            self._serve_file("js/api.js")
        elif self.path == "/api/game/state":
            self._send_json(self._build_state_json())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/api/game/new":
            self._handle_new_game()
        elif self.path == "/api/game/move":
            self._handle_move()
        else:
            self.send_response(404)
            self.end_headers()

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        return self.rfile.read(length).decode("utf-8")

    def _send_json(self, obj, status=200):
        data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self._add_cors_headers()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _serve_file(self, rel_path):
        full_path = os.path.join(STATIC_DIR, rel_path)
        if not os.path.isfile(full_path):
            self._send_json({"error": "not found"}, 404)
            return
        ext = os.path.splitext(rel_path)[1]
        mime = MIME_TYPES.get(ext, "text/plain; charset=utf-8")
        with open(full_path, "rb") as f:
            data = f.read()
        self.send_response(200)
        self._add_cors_headers()
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _build_board_json(self):
        board_data = []
        for i in range(BOARD_SIZE):
            row_data = []
            for j in range(BOARD_SIZE):
                row_data.append(game.board.get(i, j))
            board_data.append(row_data)
        return board_data

    def _build_state_json(self):
        return {
            "gameOver": game.game_over,
            "winner": game.winner,
            "currentPlayer": game.current_player,
            "mode": game.mode,
            "board": self._build_board_json(),
        }

    def _handle_new_game(self):
        body = self._read_body()
        try:
            data = json.loads(body)
            mode = data.get("mode", "pvp")
        except (json.JSONDecodeError, TypeError):
            mode = "pvp"

        global game
        game = Game(mode)
        self._send_json({"success": True, "mode": mode})

    def _handle_move(self):
        body = self._read_body()
        try:
            data = json.loads(body)
            row = int(data["row"])
            col = int(data["col"])
        except (json.JSONDecodeError, KeyError, TypeError, ValueError):
            self._send_json({"success": False})
            return

        ok = game.play(row, col)
        if not ok:
            self._send_json({"success": False})
            return

        ai_row = -1
        ai_col = -1

        if game.mode == "pve" and not game.game_over:
            ai_move = get_ai_move(game.board, WHITE)
            game.play(ai_move[0], ai_move[1])
            ai_row, ai_col = ai_move

        self._send_json({
            "success": True,
            "gameOver": game.game_over,
            "winner": game.winner,
            "aiRow": ai_row,
            "aiCol": ai_col,
        })

    def _add_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(204)
        self._add_cors_headers()
        self.end_headers()

    def log_message(self, format, *args):
        pass  # Suppress request logs

    def _serve_qr_page(self):
        ext_url = os.getenv("RENDER_EXTERNAL_URL")
        if ext_url:
            game_url = ext_url
        else:
            host_ip = get_lan_ip()
            game_url = f"http://{host_ip}:{PORT}"
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>扫码开始游戏</title>
    <style>
        body {{
            font-family: "Microsoft YaHei", Arial, sans-serif;
            background: linear-gradient(135deg, #1a1a2e, #16213e, #0f3460);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            color: #fff;
            margin: 0;
            padding: 20px;
        }}
        .container {{
            text-align: center;
            padding: 30px;
            background: rgba(255,255,255,0.05);
            border-radius: 16px;
            border: 1px solid rgba(255,255,255,0.1);
            max-width: 400px;
        }}
        h1 {{ margin-bottom: 10px; }}
        .url {{
            font-size: 1.2em;
            color: #e94560;
            margin: 20px 0;
            padding: 10px;
            background: rgba(0,0,0,0.3);
            border-radius: 8px;
            word-break: break-all;
        }}
        img {{
            max-width: 100%;
            border-radius: 8px;
        }}
        .hint {{ color: #aaa; font-size: 0.9em; margin-top: 15px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📱 扫码开始游戏</h1>
        <p>请用手机扫描二维码</p>
        <p class="url">{game_url}</p>
        <img src="https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={game_url}" alt="QR Code">
        <p class="hint">确保手机和电脑在同一个局域网下</p>
    </div>
</body>
</html>"""
        data = html.encode("utf-8")
        self.send_response(200)
        self._add_cors_headers()
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


PORT = int(os.getenv("PORT", "8080"))


def get_lan_ip():
    # In cloud deployment, use external URL
    ext_url = os.getenv("RENDER_EXTERNAL_URL")
    if ext_url:
        return ext_url.replace("https://", "").replace("http://", "")
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(1)
        s.connect(("114.114.114.114", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        try:
            hostname = socket.gethostname()
            for ip in socket.gethostbyname_ex(hostname)[2]:
                if ip.startswith("192.") or ip.startswith("10.") or ip.startswith("172."):
                    return ip
        except Exception:
            pass
        return "127.0.0.1"


def main():
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    ext_url = os.getenv("RENDER_EXTERNAL_URL")
    if ext_url:
        print(f"五子棋游戏服务器启动: {ext_url}")
    else:
        lan_ip = get_lan_ip()
        print(f"五子棋游戏服务器启动在 http://0.0.0.0:{PORT}")
        print(f"局域网访问: http://{lan_ip}:{PORT}")
        print(f"手机扫码: http://{lan_ip}:{PORT}/qr")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n服务器已关闭")
        server.server_close()


if __name__ == "__main__":
    main()
