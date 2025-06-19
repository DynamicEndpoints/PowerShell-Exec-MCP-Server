# GitHub Issue Templates for Copilot Optimization

This directory contains GitHub issue templates specifically optimized for working with GitHub Copilot and other AI coding agents. These templates provide comprehensive context, clear specifications, and detailed guidance to help AI agents understand requirements and implement solutions effectively.

## 📁 Template Files

### Core Templates

1. **`bug_report.yml`** - 🐛 Bug Report (Copilot Optimized)
   - Comprehensive environment details
   - Step-by-step reproduction instructions
   - Structured logging and error information
   - Context hints for AI analysis

2. **`feature_request.yml`** - ✨ Feature Request (Copilot Optimized)
   - Technical specifications and API design
   - Implementation guidance and code patterns
   - Detailed acceptance criteria
   - Integration and testing requirements

3. **`copilot_task.yml`** - 🤖 Copilot Task Request
   - Specific coding tasks with clear requirements
   - Code context and implementation patterns
   - Step-by-step implementation guides
   - Quality checklists and success criteria

4. **`documentation.yml`** - 📋 Documentation Update
   - Documentation improvement requests
   - Style guides and formatting requirements
   - Example structures and templates

5. **`config.yml`** - Issue template configuration
   - Disables blank issues to encourage structured reporting
   - Provides helpful links to documentation

## 🎯 Key Features for Copilot Optimization

### 1. **Comprehensive Context**
- File structure and relevant code locations
- Existing patterns and implementations to reference
- Integration points and dependencies
- Performance and security considerations

### 2. **Clear Technical Specifications**
- Detailed function signatures and API designs
- Input/output specifications
- Error handling requirements
- Type hints and documentation standards

### 3. **Implementation Guidance**
- Step-by-step development phases
- Code quality checklists
- Testing requirements and examples
- Integration instructions

### 4. **AI-Friendly Structure**
- Structured sections that AI can easily parse
- Code examples and patterns to follow
- Clear success criteria and acceptance tests
- Reference materials and documentation links

## 🚀 Best Practices for Creating Copilot-Ready Issues

### DO: ✅

1. **Provide Complete Context**
   ```markdown
   **Primary Files to Modify:**
   - [x] `server.py` - Main MCP server implementation
   - [ ] `templates/` - PowerShell script templates
   
   **Existing Code to Reference:**
   - `execute_powershell()` - for PowerShell execution patterns
   - `run_powershell_with_progress()` - for progress reporting
   ```

2. **Include Specific Function Signatures**
   ```python
   @mcp.tool()
   async def new_feature(
       param1: str,
       param2: Optional[int] = None,
       ctx: Optional[Context] = None
   ) -> str:
       """Detailed docstring with Args and Returns"""
   ```

3. **Specify Quality Requirements**
   ```markdown
   **Code Quality Checklist:**
   - [ ] Follows existing code style and patterns
   - [ ] Has comprehensive type hints
   - [ ] Has proper error handling
   - [ ] Has complete docstrings
   ```

4. **Provide Testing Guidance**
   ```python
   async def test_new_feature():
       """Test the new functionality"""
       # Test case 1: Normal operation
       # Test case 2: Error conditions
   ```

### DON'T: ❌

1. **Vague Requirements**
   - ❌ "Add a PowerShell tool"
   - ✅ "Add a tool to list installed PowerShell modules with filtering capabilities"

2. **Missing Context**
   - ❌ "Fix the bug in the server"
   - ✅ "Fix authentication timeout in execute_powershell() function"

3. **No Implementation Guidance**
   - ❌ "Implement this feature"
   - ✅ "Follow the pattern in run_powershell_with_progress() for implementation"

## 📋 Template Usage Guide

### For Bug Reports
1. Use `bug_report.yml` for any issues with existing functionality
2. Include complete environment details and reproduction steps
3. Provide relevant log output and error messages
4. Specify which files and functions are likely involved

### For New Features
1. Use `feature_request.yml` for substantial new functionality
2. Include technical specifications and API design
3. Provide implementation guidance and acceptance criteria
4. Consider security, performance, and compatibility requirements

### For Specific Tasks
1. Use `copilot_task.yml` for focused development tasks
2. Provide step-by-step implementation guidance
3. Include quality checklists and testing requirements
4. Reference existing code patterns to follow

### For Documentation
1. Use `documentation.yml` for documentation improvements
2. Specify exact files and sections to update
3. Provide style guidelines and example formats
4. Include target audience and use cases

## 🔗 Integration with Development Workflow

### GitHub Labels
The templates automatically assign appropriate labels:
- `bug` + `needs-triage` + `copilot-ready` for bug reports
- `enhancement` + `needs-discussion` + `copilot-ready` for features
- `copilot-task` + `development` + `needs-implementation` for tasks
- `documentation` + `copilot-ready` for documentation

### Automation Opportunities
These templates support automation through:
- Structured YAML frontmatter for parsing
- Consistent section headers for content extraction
- Standardized checklists for progress tracking
- Clear acceptance criteria for automated validation

## 📖 Example Usage

See `SAMPLE_COPILOT_ISSUE.md` in the repository root for a complete example of a well-structured Copilot-optimized issue that demonstrates all best practices.

## 🤝 Contributing

When contributing new templates or improvements:

1. **Follow the established structure** with clear sections and checklists
2. **Include comprehensive context** that helps AI understand requirements
3. **Provide specific examples** rather than generic placeholders
4. **Test templates** by creating sample issues to verify clarity
5. **Update this README** to document any new templates or features

## 📚 Additional Resources

- [GitHub Issue Templates Documentation](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests)
- [GitHub Copilot Best Practices](https://docs.github.com/en/copilot/using-github-copilot)
- [MCP Python SDK Documentation](https://github.com/modelcontextprotocol/python-sdk)
- [PowerShell Documentation](https://docs.microsoft.com/powershell/)
