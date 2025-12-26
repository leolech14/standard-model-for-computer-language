#!/bin/bash

# 🏗️ ARCHITECTURAL EVALUATOR
# Pipes the Spectrometer Semantic Map to the Local LLM for critique.

CONTEXT_FILE="output/deep_scan/llm_context.md"
MODEL="qwen2.5:7b-instruct"
OUTPUT_FILE="output/deep_scan/ARCHITECTURAL_CRITIQUE.md"

if [ ! -f "$CONTEXT_FILE" ]; then
    echo "❌ Error: Context file '$CONTEXT_FILE' not found. Run ./scan_deep.sh first."
    exit 1
fi

echo "🤔 Asking $MODEL to evaluate architecture based on 100% coverage map..."
echo "   (This analyzes the structural relationships found in the scan)"

PROMPT="You are a Principal Software Architect. 
I am providing you with a 'Semantic Map' of a codebase, grouped by the 'Standard Model' of Code (Data, Logic, Organization, Execution).

Your Task: Perform a Critical Architectural Review.

Analyze the provided map and answer:
1. **Structure Assessment**: Does the code separate Logic (Functions) from Execution (Handlers) and Organization (Classes) effectively?
2. **Refactoring Status**: We are moving to a 'Strangler Fig' pattern. Do you see evidence of new 'Handlers' (EXE.HDL) separating from the legacy monolith?
3. **Coupling Analysis**: identifying 'God Classes' or 'God Functions' based on the 'calls' and 'lines' metrics visible in the IDs.
4. **Specific Recommendations**: What 3 things should be refactored next?

Here is the Codebase Map:

$(cat $CONTEXT_FILE)

Response Format: Markdown report."

# Call Ollama
ollama run "$MODEL" "$PROMPT" > "$OUTPUT_FILE"

cat "$OUTPUT_FILE"
echo ""
echo "✅ Evaluation preserved in $OUTPUT_FILE"
