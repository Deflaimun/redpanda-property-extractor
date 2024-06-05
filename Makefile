.PHONY: build venv clean

build: clean venv
	git submodule init
	git submodule update
	if [ -d "/tmp/redpanda" ]; then \
		cd /tmp/redpanda && git pull; \
	else \
		git clone https://github.com/redpanda-data/redpanda.git /tmp/redpanda; \
	fi
	mkdir -p gen
	. /tmp/redpanda-property-extractor-venv/bin/activate; ./property_extractor.py --recursive --path /tmp/redpanda --output gen/properties-output.json
	make clean
	@echo "File generated at ./gen/properties-output.json"

venv: requirements.txt
	python3 -m venv /tmp/redpanda-property-extractor-venv
	. /tmp/redpanda-property-extractor-venv/bin/activate; pip install --no-cache-dir -r requirements.txt

clean:
	rm -rf /tmp/redpanda-property-extractor-venv
