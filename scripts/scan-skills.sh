#!/usr/bin/env bash
# scan-skills.sh — Scan all installed skills and output a registry summary
# Used by project-orchestrator in Codex / terminal-enabled environments
# Output: prints a markdown skill registry to stdout

SKILLS_DIR="${1:-skills}"

echo "# Skill Registry Scan"
echo "Scanned: $(date)"
echo ""
echo "| Skill | Description (first 120 chars) | Role (declared) |"
echo "|-------|-------------------------------|-----------------|"

for skill_dir in "$SKILLS_DIR"/*/; do
  skill_name=$(basename "$skill_dir")
  skill_md="$skill_dir/SKILL.md"

  if [ ! -f "$skill_md" ]; then
    continue
  fi

  # Extract description from frontmatter
  description=$(awk '
    /^---/{count++; next}
    count==1 && /^description:/{
      sub(/^description:[[:space:]]*/, "")
      print substr($0, 1, 120)
      exit
    }
  ' "$skill_md")

  # Extract role from frontmatter (optional field)
  role=$(awk '
    /^---/{count++; next}
    count==1 && /^role:/{
      sub(/^role:[[:space:]]*/, "")
      print
      exit
    }
    count==2{exit}
  ' "$skill_md")

  role="${role:-auto-infer}"

  echo "| \`$skill_name\` | ${description:-(no description)} | $role |"
done

echo ""
echo "---"
echo "Total skills found: $(find "$SKILLS_DIR" -name "SKILL.md" | wc -l | tr -d ' ')"
echo ""
echo "Run 'cat skills/<name>/SKILL.md' to read full skill details."
