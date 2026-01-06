# llm_scripts

Enjoy an LLM using voice.
Components are python based, picked up in order to have a low memory usage and possibly not that bad experience.
- overlapping of response generation with speech synthesis,
- possibility to interrupt the current response by re-instating the "trigger word",
- "magic word" detection is a service that publish the events via websockets.

This repository currently includes:
- [create_venv.sh](https://github.com/salvatorelionetti/llm_scripts/blob/main/create_venv.sh) — helper to create and activate a Python virtual environment and install dependencies.
- [t5.py](https://github.com/salvatorelionetti/llm_scripts/blob/main/t5.py) — main component.
- [magic_word_server.py](https://github.com/salvatorelionetti/llm_scripts/blob/main/magic_word_server.py) — service that inform about "magic word" detection via Websocket.

The target I'm currently using is Jetson Orin nano, not that good, not that bad.

## Requirements

- Python 3.8+
- pip
- (Recommended) Git

The repository is intended to be used inside a virtual environment. The included `create_venv.sh` script automates venv creation and dependency installation.

## Setup

1. Clone the repo
```bash
git clone https://github.com/salvatorelionetti/llm_scripts.git
cd llm_scripts
```

2. Create and activate a virtual environment using the helper:
```bash
# Make executable if needed
chmod +x create_venv.sh

# Create a venv in ./venv and install dependencies
./create_venv.sh venv
# Activate the virtualenv (POSIX shells)
source venv/bin/activate
```

3. If you prefer manual setup, create venv and install dependencies:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Note: There is no `requirements.txt` in the repository at the moment; below is a suggested set of dependencies you may want to pin and add to `requirements.txt`.

Suggested requirements (example)
```text
transformers>=4.0.0
torch>=1.9.0       # or the appropriate CPU/GPU build for your environment
flask              # if magic_word_server.py uses Flask
uvicorn            # if server is ASGI / FastAPI
requests
```

## Usage

General note: run `python <script>.py --help` to see script-specific options when available.

t5.py
- Purpose: run or demo a T5-style text-to-text model for tasks such as summarization, translation, or conditional generation.
- Example (generic):
```bash
# Replace with actual flags supported by t5.py
python t5.py --model t5-small --input "Translate English to French: Hello world."
```
- Tip: check the script header or `--help` to discover model selection, device (cpu/cuda) and I/O options.

magic_word_server.py
- Purpose: run a small HTTP server that provides the "magic word" service or demo endpoints.
- Example:
```bash
# Start server (adjust port option if available)
python magic_word_server.py --port 8000

# Then test (example)
curl http://localhost:8000/
```
- Tip: inspect the script or run `--help` to learn available endpoints and options.

create_venv.sh
- Purpose: convenience script to create a Python virtual environment and install dependencies.
- Usage:
```bash
./create_venv.sh venv  # creates/uses 'venv' directory
source venv/bin/activate
```

## Configuration

- Add a `requirements.txt` with pinned versions matching your environment (CPU vs GPU).
- If your scripts require API keys or model paths, consider `.env` or a config file. Do NOT commit secrets to the repo.

## Development & Testing

- Add unit tests (pytest or similar) under a `tests/` directory.
- Consider adding CI (GitHub Actions) to run linting and tests on push/PR.
- Add type hints and a `pyproject.toml` or `setup.cfg` for consistent tooling.

## Contributing

- Fork the repo and open a pull request with a descriptive title.
- If you change runtime requirements, update `create_venv.sh` and include a `requirements.txt`.
- If you add or change server endpoints, document them in this README and include example curl requests.

## Next improvements
- Add a `requirements.txt` with pinned versions.
- Add usage examples with exact CLI flags for `t5.py` and `magic_word_server.py`.
- Add tests and a basic CI workflow.

## License

MIT License
---
