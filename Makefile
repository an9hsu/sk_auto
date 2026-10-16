SRC = configs selenium_object utils tests

.PHONY: fix
fix:
	ruff check --select I --fix $(SRC)
	ruff format $(SRC)

.PHONY: check
check:
	ruff check $(SRC)
	ruff format --check $(SRC)
	mypy --ignore-missing-imports --check-untyped-defs --no-namespace-packages $(SRC)
