import os
import socket
from collections import deque
from datetime import datetime
from threading import Lock

from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)

def _get_int_env(name: str, default: int) -> int:
    value = os.getenv(name, str(default))
    try:
        return int(value)
    except ValueError:
        return default


def get_config() -> dict:
    return {
        "default_mac": os.getenv("DEFAULT_MAC", ""),
        "default_broadcast": os.getenv("DEFAULT_BROADCAST", "255.255.255.255"),
        "default_port": _get_int_env("DEFAULT_PORT", 9),
        "log_limit": _get_int_env("LOG_LIMIT", 50),
    }


log_lock = Lock()
logs = deque(maxlen=get_config()["log_limit"])


def update_log_limit(new_limit: int) -> None:
    global logs
    safe_limit = max(new_limit, 0)
    if logs.maxlen == safe_limit:
        return
    with log_lock:
        entries = list(logs)[:safe_limit]
        logs = deque(entries, maxlen=safe_limit)


@app.before_request
def refresh_env() -> None:
    load_dotenv(override=True)
    config = get_config()
    update_log_limit(config["log_limit"])


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
    config = get_config()
    if request.method == "POST":
        mac = request.form.get("mac", "").strip()
        broadcast = request.form.get("broadcast", config["default_broadcast"]).strip()
        port_raw = request.form.get("port", str(config["default_port"])).strip()
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
        default_mac=config["default_mac"],
        default_broadcast=config["default_broadcast"],
        default_port=config["default_port"],
        logs=log_entries,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8200)
