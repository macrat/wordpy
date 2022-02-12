.PHONY: benchmark
benchmark: output/model
	pipenv run python benchmark.py

output/model: output/dataset.npz learn.py
	pipenv run python learn.py

output/dataset.npz: dataset.py
	pipenv run python dataset.py

.PHONY: install
install:
	pipenv install
