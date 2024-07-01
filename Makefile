
all: hook
	@echo "Done!"
	pm2 status
hook:
	pm2 start ./run.sh --name HookScript --silent --log

clean:
	pm2 delete HookScript
