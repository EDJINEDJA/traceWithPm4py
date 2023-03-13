initialize_git:
	@echo "initialization ..."
	git init
	git add .
	git commit -m "My first commit"
	git branch -M main
	git remote add origin https://github.com/EDJINEDJA/traceWithPm4py.git
	git push origin main

install:
	@echo "setup virtual environnement"
	pipenv install
	pipenv run pre-commit install

env:
	@echo "activate virtual environnement"
	pipenv shell

pip_git:
	@echo "pushing ..."
	git add .
	sleep 2
	git commit -m "commit"
	sleep 2
	git push origin main

setup: initialize_git install
