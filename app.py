import os
import socket
from collections import deque
from datetime import datetime
from threading import Lock

from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, url_for

load_dotenv()

app = Flask(__name__)

DEFAULT_MAC = os.getenv("DEFAULT_MAC", "")
DEFAULT_BROADCAST = os.getenv("DEFAULT_BROADCAST", "255.255.255.255")
DEFAULT_PORT = int(os.getenv("DEFAULT_PORT", "9"))

LOG_LIMIT = int(os.getenv("LOG_LIMIT", "50"))

log_lock = Lock()
logs = deque(maxlen=LOG_LIMIT)


def normalize_mac(raw_mac: str) -> str:
    cleaned = raw_mac.strip().lower().replace("-", "").replace(":", "")
    if len(cleaned) != 12 or not all(ch in "0123456789abcdef" for ch in cleaned):
        raise ValueError("MACアドレスの形式が正しくありません。")
    return cleaned


def build_magic_packet(mac_hex: str) -> bytes:
    mac_bytes = bytes.fromhex(mac_hex)
    return b"\xff" * 6 + mac_bytes * 16


def send_magic_packet(mac: str, broadcast: str, port: int) -> None:
    packet = build_magic_packet(normalize_mac(mac))
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(packet, (broadcast, port))


def add_log(status: str, message: str, details: dict) -> None:
    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": status,
        "message": message,
        "details": details,
    }
    with log_lock:
        logs.appendleft(entry)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        mac = request.form.get("mac", "").strip()
        broadcast = request.form.get("broadcast", DEFAULT_BROADCAST).strip()
        port_raw = request.form.get("port", str(DEFAULT_PORT)).strip()
        try:
            port = int(port_raw)
            send_magic_packet(mac, broadcast, port)
            add_log(
                "success",
                "マジックパケットを送信しました。",
                {"mac": mac, "broadcast": broadcast, "port": port},
            )
        except Exception as exc:  # noqa: BLE001 - user-facing log
            add_log(
                "error",
                f"送信に失敗しました: {exc}",
                {"mac": mac, "broadcast": broadcast, "port": port_raw},
            )
        return redirect(url_for("index"))

    with log_lock:
        log_entries = list(logs)
    return render_template(
        "index.html",
        default_mac=DEFAULT_MAC,
        default_broadcast=DEFAULT_BROADCAST,
        default_port=DEFAULT_PORT,
        logs=log_entries,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8200)
