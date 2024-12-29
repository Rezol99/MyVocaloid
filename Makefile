.PHONY:
format:
	@echo "Formatting code..."
	uv run black ./myvocaloid

train:
	@echo "Training model..."
	uv run python ./myvocaloid/train.py

train-encode:
	@echo "Training model..."
	uv run python ./myvocaloid/train.py --encode