# Default branch & commit message
BRANCH ?= main
MSG ?= "chore: update"

# Add semua file, commit, lalu push
g:
	git add .
	git commit -m $(MSG)
	git push origin $(BRANCH)

# Cuma add + commit
gc:
	git add .
	git commit -m $(MSG)

# Cuma push
gp:
	git push origin $(BRANCH)
