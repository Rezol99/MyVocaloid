.PHONY:
format:
	@echo "Formatting code..."
	uv run black ./myvocaloid

.PHONY:
train:
	@echo "Training model..."
	uv run python ./myvocaloid/train.py

.PHONY:
train-encode:
	@echo "Training model..."
	uv run python ./myvocaloid/train.py --encode

.PHONY:
generate:
	@echo "Generating music..."
	uv run python ./myvocaloid/generate_audio.py