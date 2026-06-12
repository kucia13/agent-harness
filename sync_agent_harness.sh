#!/usr/bin/env bash
# ==============================================================================
# sync_agent_harness.sh
# 
# Synchronizes and maintains configuration alignment, custom skills, and MCP 
# configurations across Claude Code, Gemini/Antigravity CLI, and Codex CLI.
# ==============================================================================

set -euo pipefail

echo "========================================="
echo "🔄 Starting Agent Harness Synchronization"
echo "========================================="

# Paths
AGENT_SKILLS_DIR="$HOME/.agents/skills"
GOVERNANCE_FILE="$HOME/.agents/GOVERNANCE.md"

# 1. Ensure Hub Directories Exist
mkdir -p "$AGENT_SKILLS_DIR"

# 2. Synchronize Governance Rulebook links
echo "📄 Syncing Governance Rulebook links..."

# Gemini/Antigravity
ln -sfn "$GOVERNANCE_FILE" "$HOME/.gemini/GEMINI.md"
echo "  - Link created: ~/.gemini/GEMINI.md -> $GOVERNANCE_FILE"

# Claude Code
CLAUDE_MD="$HOME/.claude/CLAUDE.md"
if [ -f "$CLAUDE_MD" ]; then
  if ! grep -q "@$GOVERNANCE_FILE" "$CLAUDE_MD"; then
    # Prepend reference
    printf "%s\n%s\n" "@$GOVERNANCE_FILE" "$(cat "$CLAUDE_MD")" > "$CLAUDE_MD"
    echo "  - Added GOVERNANCE.md reference to ~/.claude/CLAUDE.md"
  fi
else
  mkdir -p "$(dirname "$CLAUDE_MD")"
  echo -e "@$GOVERNANCE_FILE\n@RTK.md" > "$CLAUDE_MD"
  echo "  - Created ~/.claude/CLAUDE.md referencing GOVERNANCE.md"
fi

# Codex
CODEX_AGENTS="$HOME/.codex/AGENTS.md"
if [ -f "$CODEX_AGENTS" ]; then
  if ! grep -q "@$GOVERNANCE_FILE" "$CODEX_AGENTS"; then
    printf "%s\n%s\n" "@$GOVERNANCE_FILE" "$(cat "$CODEX_AGENTS")" > "$CODEX_AGENTS"
    echo "  - Added GOVERNANCE.md reference to ~/.codex/AGENTS.md"
  fi
else
  mkdir -p "$(dirname "$CODEX_AGENTS")"
  echo -e "@$GOVERNANCE_FILE\n@/Users/kucia/.codex/RTK.md\n@/Users/kucia/.codex/CODEX_GOVERNANCE.md" > "$CODEX_AGENTS"
  echo "  - Created ~/.codex/AGENTS.md referencing GOVERNANCE.md"
fi

# 3. Synchronize Skills from Repositories
echo "⚙️  Syncing agent skills..."

link_skill() {
  local src_dir="$1"
  local skill_name="$2"
  
  if [ -d "$src_dir" ] && [ -f "$src_dir/SKILL.md" ]; then
    ln -sfn "$src_dir" "$AGENT_SKILLS_DIR/$skill_name"
    echo "  [Skills] Linked: $skill_name"
  fi
}

# Sync Superpowers skills
if [ -d "$HOME/.codex/superpowers/skills" ]; then
  for skill_path in "$HOME/.codex/superpowers/skills"/*; do
    if [ -d "$skill_path" ]; then
      name=$(basename "$skill_path")
      link_skill "$skill_path" "$name"
    fi
  done
fi

# Sync PUA skills
if [ -d "$HOME/.codex/pua/skills" ]; then
  for skill_path in "$HOME/.codex/pua/skills"/*; do
    if [ -d "$skill_path" ]; then
      name=$(basename "$skill_path")
      link_skill "$skill_path" "$name"
    fi
  done
fi

# Sync Awesome Claude Skills
AWESOME_CLAUDE_DIR="$HOME/awesome-claude-skills"
if [ -d "$AWESOME_CLAUDE_DIR" ]; then
  for skill_path in "$AWESOME_CLAUDE_DIR"/*; do
    if [ -d "$skill_path" ] && [ "$(basename "$skill_path")" != "composio-skills" ] && [ "$(basename "$skill_path")" != ".git" ]; then
      name=$(basename "$skill_path")
      link_skill "$skill_path" "$name"
    fi
  done
  
  # Link composio automation skills if present
  if [ -d "$AWESOME_CLAUDE_DIR/composio-skills" ]; then
    for comp_skill in "$AWESOME_CLAUDE_DIR/composio-skills"/*; do
      if [ -d "$comp_skill" ]; then
        name=$(basename "$comp_skill")
        link_skill "$comp_skill" "$name"
      fi
    done
  fi
fi

# 4. Verify Hooks & Config Files
echo "🛡️  Verifying CLI configuration files..."

# Check Gemini settings.json
GEMINI_SETTINGS="$HOME/.gemini/settings.json"
if [ -f "$GEMINI_SETTINGS" ]; then
  if grep -q "rtk hook gemini" "$GEMINI_SETTINGS"; then
    echo "  - [Hook] Gemini RTK Hook is correctly configured."
  else
    echo "  - [WARNING] Gemini RTK Hook is missing in settings.json!"
  fi
  if grep -q "scrapling" "$GEMINI_SETTINGS"; then
    echo "  - [MCP] Gemini Scrapling MCP is correctly configured."
  fi
  if grep -q "cloakbrowser" "$GEMINI_SETTINGS"; then
    echo "  - [MCP] Gemini CloakBrowser MCP is correctly configured."
  fi
fi

# Check Codex config.toml
CODEX_CONFIG="$HOME/.codex/config.toml"
if [ -f "$CODEX_CONFIG" ]; then
  if grep -q "scrapling" "$CODEX_CONFIG"; then
    echo "  - [MCP] Codex Scrapling MCP is correctly configured."
  fi
  if grep -q "cloakbrowser" "$CODEX_CONFIG"; then
    echo "  - [MCP] Codex CloakBrowser MCP is correctly configured."
  fi
fi

echo "========================================="
echo "✅ Synchronization Finished Successfully!"
echo "========================================="
