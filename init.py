from pathlib import Path
import tomlkit
from util import (
    logConfig,
    logger,
    lumos,
)

logConfig("logs/init.log", rotation="10 MB", level="DEBUG", lite=True)

BOX = {}


def check():
    # Iterate over the repositories
    for repo, detail in BOX["repo"].items():
        print()
        repo_path = Path(detail["path"])
        active = detail.get("active", True)
        if repo_path.exists() and (repo_path / ".git").is_dir() and active:
            logger.success("Repo [{: <10}] - Active - {}".format(repo, repo_path))
        else:
            logger.info("Repo [{: <10}] - Inactive - {}".format(repo, repo_path))
            if repo_path.exists():
                logger.error("Repo [{: <10}] - Path Not Found {}".format(repo, repo_path))
            elif (repo_path / ".git").is_dir():
                logger.error("Repo [{: <10}] - Path not a Git {}".format(repo, repo_path))
        if "secret" in detail:
            logger.info("Repo [{: <10}] - SECRET: {}".format(repo, "********"))
        else:
            logger.error("Missing SECRET")


def boot():
    global BOX
    config_path = Path() / "config.toml"
    if not config_path.exists():
        logger.error("Missing config.toml")
        raise
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = tomlkit.parse(f.read())
    except:
        logger.error("Error Parse config.toml")
        raise
    BOX["port"] = config.get("port", 8000)
    BOX["command"] = config.get("command", "get pull")
    BOX["repo"] = config.get("repo", {})
    logger.info("Port [{: <10}]".format(BOX["port"]))
    if BOX["repo"] == {}:
        logger.error("No repo in config.toml")


if __name__ == "__main__":
    boot()
    check()
