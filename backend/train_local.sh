#!/bin/bash
# Local Training Script for VioNER
# Runs training on your Mac with full RAM and MPS GPU acceleration

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Paths
VENV_PATH="$SCRIPT_DIR/venv"
TRAIN_FILE="$SCRIPT_DIR/data/processed/train.jsonl"
VAL_FILE="$SCRIPT_DIR/data/processed/val.jsonl"
OUTPUT_DIR="$SCRIPT_DIR/models"

# Default training parameters
MODEL="${MODEL:-bert-base-cased}"
EPOCHS="${EPOCHS:-10}"
BATCH_SIZE="${BATCH_SIZE:-16}"
LEARNING_RATE="${LEARNING_RATE:-2e-5}"
RUN_EPOCHS="${RUN_EPOCHS:-}"

# Early stopping and LR scheduler (NEW)
PATIENCE="${PATIENCE:-3}"
LR_SCHEDULER="${LR_SCHEDULER:-reduce_on_plateau}"
LR_REDUCE_PATIENCE="${LR_REDUCE_PATIENCE:-2}"
EARLY_STOPPING="${EARLY_STOPPING:-true}"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  VioNER Local Training${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if virtual environment exists
if [ ! -d "$VENV_PATH" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating...${NC}"
    python3 -m venv "$VENV_PATH"
    source "$VENV_PATH/bin/activate"
    pip install torch transformers tqdm numpy
else
    source "$VENV_PATH/bin/activate"
fi

# Check for MPS
echo -e "${GREEN}Checking GPU support...${NC}"
python3 -c "import torch; mps = torch.backends.mps.is_available(); print(f'MPS (Apple Silicon GPU): {\"Available\" if mps else \"Not available\"}')"
echo ""

# Check data files
if [ ! -f "$TRAIN_FILE" ]; then
    echo -e "${YELLOW}Error: Training data not found at $TRAIN_FILE${NC}"
    exit 1
fi

if [ ! -f "$VAL_FILE" ]; then
    echo -e "${YELLOW}Error: Validation data not found at $VAL_FILE${NC}"
    exit 1
fi

# Show configuration
echo -e "${GREEN}Training Configuration:${NC}"
echo "  Model:         $MODEL"
echo "  Total Epochs:  $EPOCHS"
echo "  Batch Size:    $BATCH_SIZE"
echo "  Learning Rate: $LEARNING_RATE"
if [ -n "$RUN_EPOCHS" ]; then
    echo "  Run This Session: $RUN_EPOCHS epochs"
fi
echo "  Train Data:    $TRAIN_FILE"
echo "  Val Data:      $VAL_FILE"
echo "  Output Dir:    $OUTPUT_DIR"
echo ""
echo -e "${GREEN}Training Optimizations:${NC}"
echo "  Early Stopping: $EARLY_STOPPING (patience=$PATIENCE)"
echo "  LR Scheduler:   $LR_SCHEDULER (reduce patience=$LR_REDUCE_PATIENCE)"
echo ""

# Build command
CMD="python3 $SCRIPT_DIR/pipeline/training.py \
    --train $TRAIN_FILE \
    --val $VAL_FILE \
    --model $MODEL \
    --epochs $EPOCHS \
    --batch-size $BATCH_SIZE \
    --lr $LEARNING_RATE \
    --output $OUTPUT_DIR \
    --patience $PATIENCE \
    --lr-scheduler $LR_SCHEDULER \
    --lr-reduce-patience $LR_REDUCE_PATIENCE"

# Add early stopping flag
if [ "$EARLY_STOPPING" = "false" ]; then
    CMD="$CMD --no-early-stopping"
fi

if [ -n "$RUN_EPOCHS" ]; then
    CMD="$CMD --run-epochs $RUN_EPOCHS"
fi

# Handle resume
if [ -n "$RESUME" ]; then
    CMD="$CMD --resume $RESUME"
    echo -e "${GREEN}Resuming from: $RESUME${NC}"
fi

if [ -n "$EXTEND_EPOCHS" ]; then
    CMD="$CMD --extend-epochs $EXTEND_EPOCHS"
    echo -e "${GREEN}Extending by: $EXTEND_EPOCHS epochs${NC}"
fi

echo -e "${GREEN}Starting training...${NC}"
echo ""

# Run training
eval $CMD

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Training Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Models saved to: $OUTPUT_DIR"
echo ""
echo "To use in Docker, sync models from the Models page."
