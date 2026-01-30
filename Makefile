.PHONY: bump-patch bump-minor

bump-patch:
	@npm version patch --prefix frontend

bump-minor:
	@npm version minor --prefix frontend

bump-major:
	@npm version major --prefix frontend
