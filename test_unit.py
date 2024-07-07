import pytest
import main


@pytest.fixture(scope="session", autouse=True)
def init_boot():
    main.BOX = {"port": 8000, "repo": {}}
    yield


@pytest.fixture
def mock_fix(monkeypatch, mocker):
    def mock_lumos(cmd, warning=True):
        return 0

    # monkeypatch.setattr("main.lumos", mock_lumos)
    mocker.patch("main.lumos", return_value=0)
    yield


def test_pull_success(mock_fix, tmp_path):
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    (repo_path / ".git").mkdir()
    assert main.pull(repo_path) is True
    assert main.pull(repo_path, "git fetch && git rebase && make reload") is True


def test_pull_no_repo(mock_fix, tmp_path):
    repo_empty_path = tmp_path / "repo_empty"
    repo_nogit_path = tmp_path / "repo_nogit"
    repo_nogit_path.mkdir()
    assert main.pull(repo_empty_path) is None
    assert main.pull(repo_nogit_path) is None


def test_pull_git_fetch_fail(mocker, tmp_path):
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    (repo_path / ".git").mkdir()

    mocker.patch("main.lumos", return_value=1)

    assert main.pull(repo_path) is None


@pytest.fixture
def client(mocker):
    """创建一个 Flask 测试客户端"""
    main.app.config["TESTING"] = True
    client = main.app.test_client()

    # 初始化 BOX 变量
    main.BOX["repo"] = {
        "repo1": {"path": "/path/to/repo1", "secret": "secret1"},
        "repo2": {"path": "/path/to/repo2", "secret": "secret2"},
    }

    # 模拟 pull 函数
    mocker.patch("main.pull", return_value=True)

    yield client


def test_main_get(client):
    """测试 GET 请求"""
    response = client.get("/repo1")
    assert response.data == b"Hello World!"


def test_main_post_success(client):
    """测试 POST 请求且签名验证成功"""
    import hashlib
    import hmac

    repo = "repo1"
    secret = main.BOX["repo"][repo]["secret"]
    data = b"some data"
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


def test_main_post_invalid_signature(client):
    """测试 POST 请求且签名验证失败"""
    repo = "repo1"
    secret = main.BOX["repo"][repo]["secret"]
    data = b"some data"
    invalid_signature = "sha256=invalidsignature"

    response = client.post(
        f"/{repo}", data=data, headers={"X-Hub-Signature-256": invalid_signature}
    )

    assert response.data == b"Invalid signature"
    assert response.status_code == 400
