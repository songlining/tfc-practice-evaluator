#!/bin/bash
# TFC/TFE Practice Evaluator - Installation Script
# 
# One-liner install:
#   curl -fsSL https://raw.githubusercontent.com/songlining/tfc-practice-evaluator/main/install.sh | bash
#
# Or with wget:
#   wget -qO- https://raw.githubusercontent.com/songlining/tfc-practice-evaluator/main/install.sh | bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPO_URL="https://github.com/songlining/tfc-practice-evaluator.git"
SKILL_NAME="tfc-practice-evaluator"
CLAUDE_SKILLS_DIR="${HOME}/.claude/skills"

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   TFC/TFE Practice Evaluator - Skill Installer          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check for git
if ! command -v git &> /dev/null; then
    echo -e "${RED}Error: git is not installed. Please install git first.${NC}"
    exit 1
fi

# Create skills directory if it doesn't exist
if [ ! -d "$CLAUDE_SKILLS_DIR" ]; then
    echo -e "${YELLOW}Creating Claude skills directory: ${CLAUDE_SKILLS_DIR}${NC}"
    mkdir -p "$CLAUDE_SKILLS_DIR"
fi

# Install or update the skill
INSTALL_PATH="${CLAUDE_SKILLS_DIR}/${SKILL_NAME}"

if [ -d "$INSTALL_PATH" ]; then
    echo -e "${YELLOW}Skill already exists. Updating...${NC}"
    cd "$INSTALL_PATH"
    git pull origin main
    echo -e "${GREEN}✓ Skill updated successfully!${NC}"
else
    echo -e "${BLUE}Installing skill to ${INSTALL_PATH}...${NC}"
    git clone "$REPO_URL" "$INSTALL_PATH"
    echo -e "${GREEN}✓ Skill installed successfully!${NC}"
fi

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   Installation Complete!                                ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "Skill installed to: ${BLUE}${INSTALL_PATH}${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Restart Claude (or VS Code with Claude extension)"
echo "  2. Set your TFC credentials:"
echo "     export TFC_TOKEN=\"your-token\""
echo "     export TFC_ORG=\"your-org\""
echo "  3. Ask Claude: \"Evaluate my TFC\""
echo ""
echo -e "${BLUE}Documentation: https://github.com/songlining/tfc-practice-evaluator${NC}"
