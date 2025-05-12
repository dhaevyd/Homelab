#!/bin/bash

# Check if the correct number of arguments is provided
if [ $# -lt 2 ]; then
  echo "Usage: $0 <directory> <command>"
  exit 1
fi

# Assign the first argument to directory and the rest to the command
DIR=$1
shift
COMMAND="$@"

# Navigate to each first-level subdirectory and run the command
find "$DIR" -mindepth 1 -maxdepth 1 -type d | while read SUBDIR; do
  # Skip if the subdirectory is named 'kopia' or 'archive'
  if [ "$(basename "$SUBDIR")" = "kopia" ] || [ "$(basename "$SUBDIR")" = "archive" ]; then
    echo "Skipping directory: $SUBDIR (name is '$(basename "$SUBDIR")')"
    continue
  fi

  echo "Navigating to: $SUBDIR"
  cd "$SUBDIR" || continue
  echo "Running command: $COMMAND"
  $COMMAND
done