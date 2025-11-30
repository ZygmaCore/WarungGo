BRANCH ?= main
MSG ?= "chore: update"

push:
	git add .
	git commit -m $(MSG)
	git push origin $(BRANCH)