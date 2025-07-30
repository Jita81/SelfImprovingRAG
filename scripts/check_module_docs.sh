#!/bin/bash

# Documentation Completeness Checker
# Usage: ./scripts/check_module_docs.sh [module_name]
# If no module_name provided, checks all modules

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Required documentation files for each module
REQUIRED_DOCS=("README.md" "API.md" "TESTING.md" "CHANGELOG.md")

# Function to check documentation for a single module
check_module_docs() {
    local module_name=$1
    local module_path="modules/$module_name"
    
    echo -e "${BLUE}Checking documentation for module: $module_name${NC}"
    
    # Check if module directory exists
    if [ ! -d "$module_path" ]; then
        echo -e "${RED}❌ Module directory does not exist: $module_path${NC}"
        return 1
    fi
    
    local missing_docs=()
    local found_docs=()
    
    # Check each required documentation file
    for doc in "${REQUIRED_DOCS[@]}"; do
        if [ -f "$module_path/$doc" ]; then
            found_docs+=("$doc")
            echo -e "${GREEN}✅ Found: $doc${NC}"
        else
            missing_docs+=("$doc")
            echo -e "${RED}❌ Missing: $doc${NC}"
        fi
    done
    
    # Check for inline code documentation
    echo -e "\n${BLUE}Checking inline code documentation...${NC}"
    
    # Check for docstrings in Python files
    local python_files=$(find "$module_path" -name "*.py" -not -path "*/__pycache__/*" -not -name "manual_test.py")
    local undocumented_functions=0
    local total_functions=0
    
    for py_file in $python_files; do
        if [ -f "$py_file" ]; then
            # Count functions/methods
            local func_count=$(grep -c "def " "$py_file" 2>/dev/null || echo "0")
            if [ -n "$func_count" ] && [ "$func_count" -gt 0 ]; then
                total_functions=$((total_functions + func_count))
                
                # Count functions with docstrings (basic check)
                local documented_count=$(grep -A1 "def " "$py_file" 2>/dev/null | grep -c '"""' 2>/dev/null || echo "0")
                if [ -z "$documented_count" ]; then
                    documented_count=0
                fi
                undocumented_functions=$((undocumented_functions + func_count - documented_count))
            fi
        fi
    done
    
    if [ $total_functions -gt 0 ]; then
        local documented_functions=$((total_functions - undocumented_functions))
        local doc_percentage=$(( documented_functions * 100 / total_functions ))
        echo -e "📊 Function documentation: $doc_percentage% ($documented_functions/$total_functions functions documented)"
        
        if [ $doc_percentage -lt 80 ]; then
            echo -e "${YELLOW}⚠️  Low documentation coverage for functions${NC}"
        else
            echo -e "${GREEN}✅ Good function documentation coverage${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  No functions found or unable to analyze${NC}"
    fi
    
    # Summary for this module
    echo -e "\n${BLUE}Summary for $module_name:${NC}"
    echo -e "Found docs: ${#found_docs[@]}/${#REQUIRED_DOCS[@]}"
    
    if [ ${#missing_docs[@]} -eq 0 ]; then
        echo -e "${GREEN}✅ All required documentation files present${NC}"
        return 0
    else
        echo -e "${RED}❌ Missing ${#missing_docs[@]} required documentation files:${NC}"
        for missing in "${missing_docs[@]}"; do
            echo -e "   - $missing"
        done
        return 1
    fi
}

# Function to check all modules
check_all_modules() {
    echo -e "${BLUE}Checking documentation for all modules...${NC}\n"
    
    local modules_dir="modules"
    local total_modules=0
    local compliant_modules=0
    
    if [ ! -d "$modules_dir" ]; then
        echo -e "${RED}❌ Modules directory does not exist: $modules_dir${NC}"
        exit 1
    fi
    
    # Get list of module directories (excluding __pycache__ and hidden directories)
    local modules=$(find "$modules_dir" -maxdepth 1 -type d -not -name ".*" -not -name "__pycache__" -not -name "modules" | sed 's|modules/||' | sort)
    
    if [ -z "$modules" ]; then
        echo -e "${YELLOW}⚠️  No modules found in $modules_dir${NC}"
        exit 0
    fi
    
    for module in $modules; do
        total_modules=$((total_modules + 1))
        echo -e "\n============================================================"
        
        if check_module_docs "$module"; then
            compliant_modules=$((compliant_modules + 1))
        fi
    done
    
    # Overall summary
    echo -e "\n============================================================"
    echo -e "${BLUE}OVERALL DOCUMENTATION STATUS${NC}"
    echo -e "============================================================"
    echo -e "Total modules checked: $total_modules"
    echo -e "Fully documented modules: $compliant_modules"
    echo -e "Compliance rate: $(( compliant_modules * 100 / total_modules ))%"
    
    if [ $compliant_modules -eq $total_modules ]; then
        echo -e "${GREEN}🎉 All modules have complete documentation!${NC}"
        exit 0
    else
        echo -e "${RED}❌ $(( total_modules - compliant_modules )) modules need documentation updates${NC}"
        exit 1
    fi
}

# Function to generate documentation templates for a module
generate_module_templates() {
    local module_name=$1
    local module_path="modules/$module_name"
    
    echo -e "${BLUE}Generating documentation templates for: $module_name${NC}"
    
    if [ ! -d "$module_path" ]; then
        echo -e "${RED}❌ Module directory does not exist: $module_path${NC}"
        return 1
    fi
    
    # Copy templates and customize them
    for doc in "${REQUIRED_DOCS[@]}"; do
        local template_file="docs/templates/${doc%%.md}_TEMPLATE.md"
        local target_file="$module_path/$doc"
        
        if [ ! -f "$target_file" ]; then
            if [ -f "$template_file" ]; then
                echo -e "${GREEN}📝 Creating $doc from template${NC}"
                cp "$template_file" "$target_file"
                
                # Replace template placeholders
                if command -v sed &> /dev/null; then
                    sed -i.bak "s/\[Module Name\]/$module_name/g" "$target_file" 2>/dev/null || true
                    sed -i.bak "s/\[module_name\]/$module_name/g" "$target_file" 2>/dev/null || true
                    rm -f "$target_file.bak" 2>/dev/null || true
                fi
            else
                echo -e "${YELLOW}⚠️  Template not found: $template_file${NC}"
                echo -e "Creating basic $doc file..."
                cat > "$target_file" << EOF
# $module_name $(echo ${doc%%.md} | tr '[:upper:]' '[:lower:]')

## Overview
Documentation for the $module_name module.

## TODO
Please update this documentation file with appropriate content.
Refer to the documentation standards: docs/DOCUMENTATION_STANDARDS.md
EOF
            fi
        else
            echo -e "${BLUE}ℹ️  File already exists: $doc${NC}"
        fi
    done
}

# Function to show help
show_help() {
    echo "Documentation Completeness Checker"
    echo ""
    echo "Usage:"
    echo "  $0                    Check all modules"
    echo "  $0 [module_name]      Check specific module"
    echo "  $0 --generate [module_name]  Generate doc templates for module"
    echo "  $0 --help            Show this help"
    echo ""
    echo "Required documentation files:"
    for doc in "${REQUIRED_DOCS[@]}"; do
        echo "  - $doc"
    done
    echo ""
    echo "Examples:"
    echo "  $0                           # Check all modules"
    echo "  $0 user_management          # Check user_management module"
    echo "  $0 --generate user_management # Generate templates for user_management"
}

# Main script logic
main() {
    # Change to repository root
    cd "$(dirname "$0")/.."
    
    case "${1:-}" in
        "--help"|"-h")
            show_help
            exit 0
            ;;
        "--generate")
            if [ -z "${2:-}" ]; then
                echo -e "${RED}❌ Module name required for --generate option${NC}"
                echo "Usage: $0 --generate [module_name]"
                exit 1
            fi
            generate_module_templates "$2"
            ;;
        "")
            check_all_modules
            ;;
        *)
            check_module_docs "$1"
            ;;
    esac
}

# Run main function with all arguments
main "$@"