all: install
.PHONY: all

help :           ## Show this help.
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'
	
install: ## Installation of tools
	pip install poetry
	poetry install
	cd trackerapp/ && npm install && cd ..
 
png:  install ## Produce png images
	poetry shell
	cd mjtracker
	python main.py --dest ../figs/ --png
	cd ..

app:  install ## Build the application
	cd mjtracker
	poetry run python main.py --dest ../trackerapp/data/graphs/ --json --merit_profiles --test
	cd ..
	cd trackerapp/ && npm run build && cd ..

dev:  install ## Run the application on a development mode
	cd mjtracker
	poetry run python main.py --dest ../trackerapp/data/graphs/ --json --merit_profiles --test
	cd ..
	ls -l trackerapp/data/graphs/
	cd trackerapp/ && npm run dev
