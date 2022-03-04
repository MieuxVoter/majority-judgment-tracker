all: install
.PHONY: all

help :           ## Show this help.
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'
	
install:
	pip install poetry
	poetry install

png:  install
	poetry run python main.py --dest figs/ --png

app:  install
	poetry run python main.py --dest trackerapp/src/graphs/ --json
	./generate_graph_index.sh
	cd trackerapp/ && npm run build
