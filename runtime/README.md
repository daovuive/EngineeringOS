# Local AI Runtime

Engineering OS currently uses Ollama as the default local LLM runtime.

Runtime configuration lives in `configs/ai-runtime.json`.

Useful commands:

```bash
python eng.py llm pull-plan
python eng.py llm status
python eng.py llm chat "Summarize this project." --role chat
```

The default Ollama endpoint is `http://localhost:11434`. `localhost` is resolved
from the process running `eng.py`: if the CLI runs in WSL, it looks for Ollama in
WSL; if it runs on Windows, it looks for Ollama on Windows.

When `stream` is enabled in `configs/ai-runtime.json`, the Ollama adapter uses
streaming transport internally, then buffers chunks and returns one final string
to current callers.

The current model set follows `knowledge/architect/asr/ASR-0001-llm-model-selection-for-ollama-personal-pc.md`.

Knowledge indexing uses the runtime embedding model and stores generated data
under `runtime/index/`. Build and query the initial Markdown index with:

```bash
python eng.py knowledge index
python eng.py knowledge search "architecture boundary"
```
