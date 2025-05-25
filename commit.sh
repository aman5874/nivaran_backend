#!/bin/bash
set -euo pipefail

# Function: Commit staged changes with a given message, optional date override
commit_with_msg() {
  local msg=$1
  local timestamp=${2:-}
  if [ -n "$timestamp" ]; then
    # Use a subshell so env vars don't leak
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

# Validate non-empty commit message
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

# If an interactive rebase is in progress, continue
if [ -d .git/rebase-merge ] || [ -d .git/rebase-apply ]; then
  echo "Rebase in progress. Running 'git rebase --continue'..."
  git rebase --continue
fi

echo "Commit successful."

# --- Part 2: Generate random commits with random messages and timestamps ---

start_epoch=$(date -d "2025-05-24 12:00 UTC" +%s)
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

# Ensure dummy file exists
touch dummy.log

num_commits=$(( RANDOM % 5 + 8 ))

echo "Generating $num_commits random commits..."

for i in $(seq 1 $num_commits); do
  # Generate random timestamp between start and now in UTC ISO8601
  rand_epoch=$(shuf -i "${start_epoch}-${end_epoch}" -n 1)
  rand_date=$(date -u -d "@$rand_epoch" +"%Y-%m-%dT%H:%M:%SZ")

  msg="${messages[$RANDOM % ${#messages[@]}]}"
  echo "$msg at $rand_date" >> dummy.log

  git add dummy.log

  commit_with_msg "$msg" "$rand_date"
done

echo "Random commits generated."
