PORT ?= 3000

.PHONY: docs-manual-serve docs-maintainer-serve
docs-manual-serve:
	npx docsify-cli serve docs/manual -p $(PORT)

docs-maintainer-serve:
	npx docsify-cli serve docs/maintainer -p $(PORT)
