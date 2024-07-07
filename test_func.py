import pytest
import main
import util


@pytest.fixture(scope="session", autouse=True)
def init_boot():
    main.BOX = {"port": 8000, "repo": {}}
    yield


@pytest.fixture
def client():
    main.app.config["TESTING"] = True
    main.app.config["WTF_CSRF_ENABLED"] = False
    client = main.app.test_client()
    yield client


def test_smoke(client, tmp_path):
    git_url = "https://github.com/gaoming714/HookScript"
    main.BOX["repo"] = {
        "HookScript": {"path": tmp_path / "HookScript", "secret": "secret1"}
    }
    repo_path = main.BOX["repo"]["HookScript"]["path"]
    target_hash = repo_path / "target.hash"
    origin_hash = repo_path / "origin.hash"
    latest_hash = repo_path / "latest.hash"
    # clone
    cmd = "cd {} && git clone {}".format(tmp_path, git_url)
    util.lumos(cmd)
    assert repo_path.exists()
    # get terget hash
    cmd = "cd {} && git rev-parse HEAD > target.hash".format(repo_path)
    util.lumos(cmd)
    # reset
    cmd = "cd {} && git reset --hard HEAD^".format(repo_path, git_url)
    util.lumos(cmd)
    # get origin hash
    cmd = "cd {} && git rev-parse HEAD > origin.hash".format(repo_path)
    util.lumos(cmd)

    if target_hash.exists() and origin_hash.exists():
        target_content = target_hash.read_text(encoding="utf-8").strip()
        origin_content = origin_hash.read_text(encoding="utf-8").strip()
    assert target_content != origin_content

    import hashlib
    import hmac

    repo = "HookScript"
    secret = main.BOX["repo"][repo]["secret"]
    data = b"payload data"
    signature = (
        "sha256="
        + hmac.new(
            secret.encode("utf-8"), msg=data, digestmod=hashlib.sha256
        ).hexdigest()
    )

    response = client.post(
        f"/{repo}", data=data, headers={"X-Hub-Signature-256": signature}
    )

    assert response.data == b"Pull executed successfully."
    assert response.status_code == 200
    # get latest hash
    cmd = "cd {} && git rev-parse HEAD > latest.hash".format(repo_path)
    util.lumos(cmd)
    if target_hash.exists() and latest_hash.exists():
        target_content = target_hash.read_text(encoding="utf-8").strip()
        latest_content = latest_hash.read_text(encoding="utf-8").strip()
    assert target_content == latest_content
