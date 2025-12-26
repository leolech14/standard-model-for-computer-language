#!/bin/bash

# 🧠 DEEP SCAN (100% Coverage Mode)
# Uses Qwen2.5-7B via Ollama to classify "Dark Matter"

# 1. Check for Ollama
if ! command -v ollama &> /dev/null; then
    echo "❌ Error: 'ollama' is not installed."
    echo "Please install from https://ollama.ai"
    exit 1
fi

# 2. Check server status
if ! curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "⚠️  Ollama server not running. Starting it..."
    ollama serve &
    sleep 5
fi

# 3. Check for Model
MODEL="qwen2.5:7b-instruct"
if ! ollama list | grep -q "$MODEL"; then
    echo "⬇️  Pulling model $MODEL..."
    ollama pull $MODEL
fi

REPO_PATH=$1
if [ -z "$REPO_PATH" ]; then
    echo "Usage: ./scan_deep.sh /path/to/repo"
    exit 1
fi

echo "🚀 Starting DEEP SCAN on $REPO_PATH..."
echo "   (This may take some time as it asks the LLM about every unknown component)"

# 4. Run Learning Engine with LLM Enabled
python3 tools/learning_engine.py \
    --single-repo "$REPO_PATH" \
    --llm \
    --llm-model "$MODEL" \
    --output output/deep_scan

echo "✅ Deep Scan Complete. Check output/deep_scan/report.md"
