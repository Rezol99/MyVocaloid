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

generate:
	@echo "Generating music..."
	uv run python ./myvocaloid/generate_audio.py