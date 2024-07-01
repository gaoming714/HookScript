# HookScript
> [!NOTE]
> A minimal Flask application to handle github webhook.
>
> Run `git fetch && git base` automanticly.
>
> Steps: add repoName&repoPath to config.toml, then run daemon only.

> [!NOTE]
> 一个用于处理 github webhook 的极简 Flask 应用程序。
>
> 自动运行 `git fetch && git base`。
>
> 步骤：将 repoName&repoPath 添加到 config.toml，然后仅运行守护进程。


## Requirements

- Set up github webhook (Payload URL and SECRET)
- Set up a server to handle webhook requests (HTTP POST)
- Python environment
- PM2 (Node.js process manager) to run and monitor the Python script

## Steps

### 1. set github webhook

set webhook  Payload URL, ex. `http://webhook.jokerpy.top/pool`

Note: Use `pool` as the repo alias to run the local path (match step 3 repoName)

set Content type `application/json` (current only json is tested & supported)

### 2. set nginx to handle payload URL redirect to 127.0.0.1:8000

make sure `http://webhook.jokerpy.top/pool` can be finded by flask

### 3. config config.toml

copy config.toml.example to config.toml.

- `[repoName]`  represents the repo alias set in step 1

- `path` specifies the local path on the server corresponding to the GitHub repository (e.g., the directory where you want to execute commands) (cd path)

- `secret` is the github webhook SECRET (step 1)

### 4. install python dep. (poetry install, if you use poery)

### 5. run python main.py (flask app)

`poetry run python main.py`


### 6. Setup PM2 as a Daemon

Configure PM2 to monitor and run the Python script as a daemon.
You can use a Makefile or shell script to trigger PM2.

Example command:

```shell
pm2 start ./run.sh --name HookScript --silent --log
```

This command starts a new PM2 process named HookScript, runs silently, and logs the output



## Final

By following these steps, you can successfully set up a server to handle GitHub webhook requests, process the payloads, and execute actions based on the received data.