test: test_app test_plugin

# test_sdk:
# 	@cd ./hiagent-plugin-sdk && poetry run pytest && cd -

image=hub.byted.org/epscprelease/plugin-runtime:v1.6.0-alpha.1-1740291612
pkg:=*

test_app:
	@poetry run pytest ./tests

test_plugin:
	@bash scripts/test_plugins.sh

build_plugins:
	@bash scripts/build_plugins.sh

patch_offline_amd64:
	@docker run --rm -it -v $(PWD):/app -v $(PWD)/.pip_cache:/root/.cache/pip --platform=linux/amd64 $(image) bash -c '\
		for dir in "dist"/$(pkg); do \
			if [ -f "$$dir" ]; then \
					echo "build amd64 offline: $$dir"; \
					python ./scripts/offline-wheel.py package $$dir --out=./dist/offline-amd64 --arch=amd64 --index-url=https://bytedpypi.byted.org/simple/; \
			fi; \
		done'

patch_offline_arm64:
	@docker run --rm -it -v $(PWD):/app -v $(PWD)/.pip_cache:/root/.cache/pip --platform=linux/arm64 $(image) bash -c '\
		for dir in "dist"/$(pkg); do \
			if [ -f "$$dir" ]; then \
					echo "build arm64 offline: $$dir"; \
					python ./scripts/offline-wheel.py package $$dir --out=./dist/offline-arm64 --arch=arm64 --index-url=https://bytedpypi.byted.org/simple/; \
			fi; \
		done'

.PHONY: linux-container

linux-container:
	@docker build . -f ./build/dockerfile -t hub.byted.org/epscprelease/plugin-runtime:v1 --platform=linux/amd64 --progress=plain
