#!/bin/bash

# Configuration
BATCH_SIZE=5
COMMIT_MSG_PREFIX="Batch update"
BRANCH_NAME=$(git branch --show-current)

# Get all modified and untracked files safely into an array
FILES=()
while IFS= read -r line; do
    # Extract filename from git status (handles spaces cleanly)
    FILE=$(echo "$line" | sed 's/^...//')
    if [ -n "$FILE" ]; then
        FILES+=("$FILE")
    fi
done < <(git status --porcelain)

TOTAL_FILES=${#FILES[@]}
if [ "$TOTAL_FILES" -eq 0 ]; then
    echo "No changes detected."
    exit 0
fi

echo "Found $TOTAL_FILES changed files. Processing in batches of $BATCH_SIZE..."

COUNTER=0
BATCH_NUM=1
CURRENT_BATCH_FILES=()

for FILE in "${FILES[@]}"; do
    # Skip if file was deleted externally but still tracked
    if [ ! -e "$FILE" ] && ! git ls-files --error-unmatch "$FILE" >/dev/null 2>&1; then
        continue
    fi

    CURRENT_BATCH_FILES+=("$FILE")
    ((COUNTER++))

    # Process batch when size is reached or at the end of the file list
    if [ "$COUNTER" -eq "$BATCH_SIZE" ] || [ "$FILE" = "${FILES[TOTAL_FILES-1]}" ]; then
        if [ ${#CURRENT_BATCH_FILES[@]} -gt 0 ]; then
            echo "-----------------------------------"
            echo "Processing Batch #$BATCH_NUM (${#CURRENT_BATCH_FILES[@]} files)..."
            
            # Stage files
            git add "${CURRENT_BATCH_FILES[@]}"
            
            # Commit
            git commit -m "$COMMIT_MSG_PREFIX - Part $BATCH_NUM"
            
            # Push
            echo "Pushing Batch #$BATCH_NUM to origin/$BRANCH_NAME..."
            git push origin "$BRANCH_NAME"
            
            # Reset batch variables
            CURRENT_BATCH_FILES=()
            COUNTER=0
            ((BATCH_NUM++))
        fi
    fi
done

echo "-----------------------------------"
echo "All batches processed successfully!"

