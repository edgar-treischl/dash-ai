# Ollama on macOS

## 1. Start Ollama
Open a separate terminal and run:

```bash
ollama serve
```

Keep this terminal running.

## 2. List downloaded models

In another terminal:

```bash
ollama list
```

Download via:

```bash
ollama pull mistral
```

Run 

```bash
ollama run mistral
```

Storage 

```bash
~/.ollama/models/
```

Disk usage

```bash
du -sh ~/.ollama/models
```



