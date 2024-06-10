.PHONY: build venv clean redpanda-git tags

TAG ?= dev

build: clean venv redpanda-git
	mkdir -p gen
	. ./tmp/redpanda-property-extractor-venv/bin/activate; ./property_extractor.py --recursive --path ./tmp/redpanda --output gen/properties-output.json
	make clean
	@echo "File generated at ./gen/properties-output.json"

venv: requirements.txt
	python3 -m venv ./tmp/redpanda-property-extractor-venv
	. ./tmp/redpanda-property-extractor-venv/bin/activate; pip install --no-cache-dir -r requirements.txt

clean:
	rm -rf ./tmp/redpanda-property-extractor-venv

redpanda-git:
	if [ -d "./tmp/redpanda" ]; then \
		cd ./tmp/redpanda && git fetch --tags; \
		if [ -z "$(TAG)" ]; then \
			git pull origin $(TAG); \
		else \
			git checkout tags/$(TAG) && git pull; \
		fi; \
		git reflog -1; \
	else \
		git clone https://github.com/redpanda-data/redpanda.git ./tmp/redpanda --branch $(TAG); \
		git reflog -1; \
	fi