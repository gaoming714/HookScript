
all: hook
	@echo "Done!"
	pm2 status

hook:
	pm2 start ./run.sh --name HookScript --silent --log

clean:
	pm2 delete HookScript

reload: install
	pm2 reload HookScript

install:
	poetry install --no-root

init:
	poetry run python init.py