# CLAUDE Configuration v1 - Compounding Engineering

## Mission
Every interaction is an opportunity to make the next one better. Watch for inefficiencies, anti-patterns, and manual processes that slow development. Proactively suggest improvements that compound over time.

## Compounding Engineering Principles

### 1. Anti-Pattern Detection
Continuously watch for and flag:
- **Manual Copy/Paste**: Suggest abstraction into functions, constants, or templates
- **Repetitive Tasks**: Identify automation opportunities (scripts, aliases, shortcuts)
- **Configuration Drift**: Notice inconsistencies in naming, structure, or conventions
- **Technical Debt**: Highlight quick wins for code cleanup and optimization
- **Process Friction**: Identify workflow bottlenecks and suggest streamlined approaches

### 2. Continuous Improvement
After each task completion:
- **Document Learnings**: What patterns emerged? What could be automated?
- **Update This File**: Suggest additions to improve future interactions
- **Create Shortcuts**: Propose aliases, scripts, or templates for repeated workflows
- **Refine Conventions**: Notice and suggest consistency improvements

### 3. Investment Mindset
Prioritize solutions that:
- Save time in future sessions
- Reduce cognitive load
- Prevent common mistakes
- Scale across team members
- Compound in value over time

## Tech Stack
- Framework: [Add your framework and version]
- Language: [Add your language and version]
- Database: [Add your database and version]
- Package Manager: [Add your package manager]

## Project Structure
```
src/                    # Source code
├── components/         # Reusable UI components
├── lib/               # Core utilities and helpers
├── types/             # TypeScript definitions
├── hooks/             # Custom React hooks (if applicable)
└── utils/             # Helper functions
tests/                 # Test files
docs/                  # Documentation
scripts/               # Automation scripts
.claude/               # Claude-specific configurations
```

## Essential Commands
```bash
# Development
npm run dev            # Start development server
npm run build          # Production build
npm run test           # Run test suite
npm run lint           # Code linting
npm run typecheck      # Type validation

# Automation Opportunities
# TODO: Add project-specific automation scripts here
# Example: npm run setup-dev-env, npm run generate-component
```

## Code Style & Conventions
- Use ES modules (import/export)
- Prefer composition over inheritance
- Destructure imports: `import { useState } from 'react'`
- File naming: `kebab-case` for files, `PascalCase` for components
- Function naming: `camelCase` with descriptive verbs
- Constants: `UPPER_SNAKE_CASE`

## Efficiency Patterns to Promote
1. **Template Creation**: When creating similar files, generate templates
2. **Configuration as Code**: Store common setups in version-controlled configs
3. **Snippet Libraries**: Build reusable code snippets for common patterns
4. **Documentation Integration**: Keep docs close to code, update simultaneously
5. **Testing Automation**: Write tests that prevent future regressions

## Anti-Patterns to Flag & Fix
1. **Magic Numbers**: Replace with named constants
2. **Duplicate Code**: Extract into shared utilities
3. **Manual File Creation**: Create generators for common file types
4. **Inconsistent Naming**: Establish and enforce naming conventions
5. **Missing Documentation**: Add inline docs for complex logic
6. **Hard-coded Values**: Move to configuration files
7. **Copy-Paste Debugging**: Create proper debugging workflows

## Repository Workflow
- Branch naming: `feature/description` or `fix/description`
- Commit format: `type: description` (e.g., `feat: add user authentication`)
- PR requirements: Tests pass, linting clean, description includes context
- Code review: Focus on maintainability and future developer experience

## Automation Opportunities Checklist
Track and implement these efficiency multipliers:

### Development Setup
- [ ] One-command environment setup
- [ ] Automated dependency installation
- [ ] Development database seeding
- [ ] Environment variable templates

### Code Generation
- [ ] Component scaffolding scripts
- [ ] API endpoint generators
- [ ] Test file templates
- [ ] Documentation generators

### Quality Assurance
- [ ] Pre-commit hooks for linting/formatting
- [ ] Automated test running on file changes
- [ ] Continuous integration pipeline
- [ ] Dependency security scanning

### Deployment
- [ ] One-command deployment scripts
- [ ] Environment-specific configurations
- [ ] Rollback procedures
- [ ] Health check automation

## Continuous Learning Protocol
At the end of each session, consider:

1. **What was repeated?** → Can we automate it?
2. **What was confusing?** → Can we document it?
3. **What was slow?** → Can we optimize it?
4. **What was error-prone?** → Can we prevent it?
5. **What patterns emerged?** → Can we template them?

## Session Improvement Tracking
```markdown
<!-- Update after each significant session -->
## Recent Improvements
- [Date]: [What was improved and why]
- [Date]: [What efficiency was gained]

## Next Optimization Targets
- [ ] [Specific inefficiency to address]
- [ ] [Process to automate]
- [ ] [Pattern to template]
```

## Do Not
- Manually repeat tasks that could be scripted
- Copy-paste code without considering abstraction
- Accept inefficient workflows as "just how we do things"
- Skip documentation for complex or non-obvious solutions
- Ignore opportunities to reduce future cognitive load

## Remember
Every inefficiency spotted is an investment opportunity. Every manual process is automation waiting to happen. Every repeated pattern is a template in disguise. Make each session count for all future sessions.

---

*This file should evolve with each session. Update it when you discover new patterns, inefficiencies, or optimization opportunities.*