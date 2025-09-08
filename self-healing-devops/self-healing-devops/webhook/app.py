from flask import Flask, request, jsonify
import subprocess, sys, json, os, datetime

app = Flask(__name__)

def run_playbook():
    cmd = ["ansible-playbook", "-i", "/ansible/inventory.ini", "/ansible/playbooks/heal_nginx.yml", "-vvv"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    ts = datetime.datetime.utcnow().isoformat() + "Z"
    print(f"[{ts}] Ran: {' '.join(cmd)}")
    print(proc.stdout)
    if proc.stderr:
        print(proc.stderr, file=sys.stderr)
    return proc.returncode

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"ok": True})

@app.route("/alert", methods=["POST"])
def alert():
    try:
        payload = request.get_json(force=True, silent=False)
    except Exception as e:
        return jsonify({"ok": False, "error": f"invalid json: {e}"}), 400

    # Basic log
    print("Received alert:", json.dumps(payload, indent=2))

    status = payload.get("status")  # firing|resolved
    alerts = payload.get("alerts", [])
    ran = False

    for a in alerts:
        name = a.get("labels", {}).get("alertname", "")
        if status == "firing" and name == "NginxDown":
            code = run_playbook()
            ran = True
            if code == 0:
                print("Ansible playbook completed OK")
            else:
                print(f"Ansible playbook exited with {code}", file=sys.stderr)

    return jsonify({"ok": True, "playbook_ran": ran})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)