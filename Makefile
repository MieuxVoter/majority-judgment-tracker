all: install
.PHONY: all

help :           ## Show this help.
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'
	
install: # Installation of tools
	pip install poetry
	poetry install
	cd trackerapp/ && npm install

png:  install # Produce png images
	poetry run python main.py --dest figs/ --png

app:  install # Build the application
	poetry run python main.py --dest trackerapp/src/graphs/ --json --merit_profiles
	./generate_graph_index.sh
	cd trackerapp/ && npm run build

dev:  install # Run the application on a development mode
	poetry run python main.py --dest trackerapp/data/graphs/ --json --merit_profiles
	./generate_graph_index.sh
	cd trackerapp/ && npm run dev
