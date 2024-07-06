from pathlib import Path
import tomlkit
import hashlib
import hmac
from flask import Flask, request
from util import (
    logConfig,
    logger,
    lumos,
)

logConfig("logs/allinOne.log", rotation="10 MB", level="DEBUG", lite=False)

BOX = {}

app = Flask(__name__)


@app.route("/<repo>", methods=["GET", "POST"])
def main(repo=None):
    if request.method == "GET":
        return "Hello World!"
    detail = BOX["repo"].get(repo, None)
    if not repo:
        return "No Repo local.", 400
    path = Path(detail["path"])
    secret = detail["secret"]
    signature = request.headers.get("X-Hub-Signature-256", "")
    expected_signature = (
        "sha256="
        + hmac.new(
            secret.encode("utf-8"), msg=request.data, digestmod=hashlib.sha256
        ).hexdigest()
    )
    # show debug msg
    logger.debug("Repo {}".format(repo))
    logger.debug("Path {}".format(path))
    logger.debug(
        "Hash check\nsegnature - {}\nexpected  - {}".format(
            signature, expected_signature
        )
    )
    if hmac.compare_digest(signature, expected_signature):
        logger.success("Signature verification succeeded. Executing pull...")
        res = pull(path)
        if res:
            logger.success("{} successfully.".format(BOX["command"]))
            return "Pull executed successfully.", 200
        else:
            logger.error("{} failed.".format(BOX["command"]))
            return "Pull executed failed.", 400

    else:
        logger.error("Signature verification failed.")
        return "Invalid signature", 400


def pull(repo_path):
    logger.info(f"Pulling {repo_path}")
    if not repo_path.exists() or not (repo_path / ".git").is_dir():
        logger.debug(f"No Repo {repo_path}")
        return
    cmd = "cd {} && {}".format(repo_path, BOX["command"])
    res = lumos(cmd, warning=True)
    if res == 0:
        return True
    else:
        return


def boot():
    global BOX
    config_path = Path() / "config.toml"
    with open(config_path, "r", encoding="utf-8") as f:
        config = tomlkit.parse(f.read())
    # BOX = config
    # add default
    # if "port" not in BOX:
    #     BOX["port"] = 8000
    # if "command" not in BOX:
    #     BOX["command"] = "git pull"
    BOX["port"] = config.get("port", 8000)
    BOX["command"] = config.get("command", "git pull")
    BOX["repo"] = config.get("repo", {})
    if BOX["repo"] == {}:
        logger.error("No repo in config.toml")


if __name__ == "__main__":
    boot()
    app.run(debug=True, port=BOX["port"])
