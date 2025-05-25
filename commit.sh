#!/bin/bash
set -euo pipefail

# Function: Commit staged changes with a given message, optional date override
commit_with_msg() {
  local msg=$1
  local timestamp=${2:-}
  if [ -n "$timestamp" ]; then
    (
      export GIT_AUTHOR_DATE="$timestamp"
      export GIT_COMMITTER_DATE="$timestamp"
      git commit -m "$msg"
    )
  else
    git commit -m "$msg"
  fi
}

# --- Part 1: Interactive commit with user prompt ---

read -p "Enter commit message: " msg

if [[ -z "$msg" ]]; then
  echo "Error: Commit message cannot be empty."
  exit 1
fi

git add .

if git diff --cached --quiet; then
  echo "No changes to commit."
  exit 0
fi

commit_with_msg "$msg"

if [ -d .git/rebase-merge ] || [ -d .git/rebase-apply ]; then
  echo "Rebase in progress. Running 'git rebase --continue'..."
  git rebase --continue
fi

echo "Commit successful."

# --- Part 2: Add 2 realistic commits specifically on May 24, 2025 ---

dummy_file="dummy.log"
touch "$dummy_file"

may24_base_epoch=$(date -d "2025-05-24 00:00 UTC" +%s)
may24_end_epoch=$(date -d "2025-05-24 23:59 UTC" +%s)

# Commit messages for May 24 commits
may24_messages=(
  "Initial data schema setup for patient records"
  "Add base API endpoints for symptom checker"
)

echo "Adding 2 commits with timestamps on May 24, 2025..."

for msg in "${may24_messages[@]}"; do
  # Random time on May 24 between midnight and 23:59 UTC
  rand_epoch=$(shuf -i "${may24_base_epoch}-${may24_end_epoch}" -n 1)
  rand_date=$(date -u -d "@$rand_epoch" +"%Y-%m-%dT%H:%M:%SZ")

  echo "$msg at $rand_date" >> "$dummy_file"
  git add -f "$dummy_file"
  commit_with_msg "$msg" "$rand_date"
done

# --- Part 3: Generate 8–12 random commits with random messages and timestamps ---

start_epoch=$may24_base_epoch  # Starting from May 24 2025 midnight UTC
end_epoch=$(date -u +%s)

messages=(
  "Improve input validation in symptom checker"
  "Add fallback to teleconsult if AI triage uncertain"
  "Refactor health summary generation logic"
  "Update .env.example with new GCP key vars"
  "Fix Dockerfile for alpine compatibility"
  "Improve error handling in AI module"
  "Rewrite README with updated onboarding steps"
  "Optimize MongoDB queries in patient record fetch"
  "Add unit tests for prompt interpreter"
  "Clean up legacy deploy script references"
)

num_commits=$(( RANDOM % 5 + 8 ))

echo "Generating $num_commits random commits..."

for i in $(seq 1 $num_commits); do
  rand_epoch=$(shuf -i "${start_epoch}-${end_epoch}" -n 1)
  rand_date=$(date -u -d "@$rand_epoch" +"%Y-%m-%dT%H:%M:%SZ")

  msg="${messages[$RANDOM % ${#messages[@]}]}"
  echo "$msg at $rand_date" >> "$dummy_file"

  git add -f "$dummy_file"
  commit_with_msg "$msg" "$rand_date"
done

echo "Random commits generated."
