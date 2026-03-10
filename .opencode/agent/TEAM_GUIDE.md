# TKS Report Maker Agent Team Guide

## Overview
This document describes the multi-agent team system for developing and maintaining the TKS Report Maker application. The system uses specialized agents to manage the full-stack architecture (FastAPI + Next.js + Tauri).

## Team Structure

### Core Agents (4-Agent Architecture)

| Agent | Model | Primary Role | Key Tools |
|-------|-------|--------------|-----------|
| **orchestrator** | zai-coding-plan/glm-4.7 | Workflow coordination and task management | read, grep, todowrite, task, bash, edit |
| **reasoner** | zai-coding-plan/glm-4.7 | System design, reasoning, and analysis | read, grep, glob, bash, task, edit |
| **implementer** | deepseek/deepseek-chat | Full-stack implementation and operations | read, write, edit, grep, bash, task |
| **verifier** | deepseek/deepseek-reasoner | Quality assurance and verification | read, grep, bash, task, edit, glob |

## Agent Responsibilities

### 🎯 Orchestrator
- **Role**: Overall workflow coordination and task management
- **Responsibilities**:
  - Analyze complex project requirements and break them down into tasks
  - Create and manage TODO lists
  - Launch appropriate subagents (reasoner, implementer, verifier) based on task type
  - Monitor task completion and agent performance
  - Handle conflicts between agent activities
- **When to use**: Complex multi-step tasks, coordination across agents, project management

### 🧠 Reasoner
- **Role**: System design, reasoning, and analysis specialist
- **Responsibilities**:
  - System design and architecture decisions
  - Complex problem analysis and debugging strategies
  - Performance analysis and optimization recommendations
  - Algorithm design and data structure recommendations
  - Architectural review and evaluation
- **When to use**: New feature design, architectural decisions, performance optimization, complex debugging

### 💻 Implementer
- **Role**: Full-stack implementation and operations specialist
- **Responsibilities**:
  - Backend development (FastAPI, SQLAlchemy, PostgreSQL)
  - Frontend development (Next.js, TypeScript, Tailwind CSS)
  - Database operations and migrations
  - Documentation creation and updates
  - UX implementation and improvements
  - Build processes (Nuitka, Tauri)
  - Operations and infrastructure management
- **When to use**: Code implementation, bug fixes, feature development, database changes, builds

### ✅ Verifier
- **Role**: Quality assurance and verification specialist
- **Responsibilities**:
  - Test execution (backend, frontend, E2E)
  - Code review and analysis
  - Security auditing
  - Quality metrics tracking
  - Bug detection and reporting
  - Quality gate validation
- **When to use**: Testing, code review, security checks, quality validation

## Workflow Definitions

### Feature Development Workflow
**Trigger**: Feature request or new requirement
**Agents**: orchestrator → reasoner → implementer → verifier → orchestrator
**Process**:
1. **Orchestrator**: Analyze requirements → Create TODO list → Launch reasoner
2. **Reasoner**: Design solution architecture → Create implementation plan → Hand off to implementer
3. **Implementer**: Implement code → Write tests → Update documentation → Submit to verifier
4. **Verifier**: Execute tests → Review code → Check security → Report findings
5. **Orchestrator**: Validate completion → Close task → Report status

### Bug Fix Workflow
**Trigger**: Test failure or bug report
**Agents**: orchestrator → verifier → implementer → verifier → orchestrator
**Process**:
1. **Orchestrator**: Receive bug report → Analyze impact → Launch verifier
2. **Verifier**: Investigate issue → Identify root cause → Report to implementer
3. **Implementer**: Fix the bug → Update tests → Submit to verifier
4. **Verifier**: Verify fix → Confirm test passes → Close issue
5. **Orchestrator**: Validate resolution → Update task status

### Performance Optimization Workflow
**Trigger**: Performance concerns or requirements
**Agents**: orchestrator → reasoner → implementer → verifier → orchestrator
**Process**:
1. **Orchestrator**: Identify performance concerns → Launch reasoner
2. **Reasoner**: Analyze performance → Identify bottlenecks → Recommend optimizations
3. **Implementer**: Implement optimizations → Benchmark improvements
4. **Verifier**: Validate performance improvements → Run tests → Confirm improvements
5. **Orchestrator**: Document results → Close task

### Code Review Workflow
**Trigger**: Pull request created or updated
**Agents**: orchestrator → verifier → orchestrator
**Process**:
1. **Orchestrator**: Identify PR → Launch verifier
2. **Verifier**: Perform comprehensive review (logic, performance, security) → Report findings
3. **Orchestrator**: Aggregate feedback → Report to user

### Deployment Workflow
**Trigger**: Release preparation
**Agents**: orchestrator → implementer → verifier → implementer → orchestrator
**Process**:
1. **Orchestrator**: Prepare release → Launch implementer
2. **Implementer**: Build artifacts → Prepare deployment
3. **Verifier**: Run comprehensive tests → Perform security check
4. **Implementer**: Execute deployment → Monitor health
5. **Orchestrator**: Validate deployment → Report status

## Agent Collaboration Patterns

### Direct Activation
Primary agents can be activated directly for specific tasks:
```javascript
Task(description="Design feature", prompt="Design new reporting feature", subagent_type="reasoner")
Task(description="Implement feature", prompt="Implement API endpoint", subagent_type="implementer")
Task(description="Run tests", prompt="Execute test suite", subagent_type="verifier")
```

### Orchestrated Activation
Orchestrator manages complex multi-agent workflows:
```javascript
Task(description="Coordinate feature development", prompt="Implement new feature from design to completion", subagent_type="orchestrator")
```

### Sequential Coordination
Agents work sequentially, with each agent passing results to the next:
```
Orchestrator → Reasoner (design) → Implementer (implementation) → Verifier (validation) → Orchestrator (completion)
```

## Tool Access Control

### Permission Levels
1. **Full Access**: orchestrator, reasoner, implementer (read, write, edit, grep, bash, task)
2. **Verification Access**: verifier (read, grep, bash, task, edit, glob)

### Safety Restrictions
1. **Git safety**: Prevent force pushes, require review for main branch
2. **Secret protection**: Block commits of sensitive files (.env, credentials)
3. **Environment protection**: Restrict access to production environment variables
4. **Destructive operations**: Require confirmation for irreversible actions

## Development Standards

### Code Quality
- All code changes must pass type checking (mypy, TypeScript)
- Test coverage should not decrease
- Code must follow project-specific patterns and conventions
- Security vulnerabilities must be addressed before merging

### Documentation
- API changes must update OpenAPI specifications
- New features require updated documentation
- Configuration changes must be documented
- Design decisions require documentation

### Collaboration
- Agents should work within their defined responsibilities
- Complex tasks should be broken down and delegated appropriately
- Agents should document their work and decisions
- Issues should be escalated to appropriate specialists

## Technology Stack

### Backend
- **Framework**: FastAPI with Uvicorn
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Validation**: Pydantic models
- **Testing**: pytest with coverage
- **Build**: Nuitka for executables

### Frontend
- **Framework**: Next.js 15 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS 4
- **State Management**: Zustand, React Query
- **Forms**: React Hook Form with Zod
- **Testing**: Jest, React Testing Library, Playwright

### Desktop
- **Framework**: Tauri
- **Integration**: Native APIs for file dialogs, system integration

### Infrastructure
- **Containers**: Docker for development and deployment
- **Build Tools**: uv, npm, Tauri CLI
- **CI/CD**: GitHub Actions

## Performance Monitoring

### Agent Metrics
- Task completion time and success rate
- Tool usage patterns and efficiency
- Collaboration effectiveness
- Problem-solving accuracy

### System Metrics
- Build success rates and duration
- Test pass rates and coverage
- Deployment success and rollback frequency
- Security issue detection and resolution time

## Troubleshooting

### Common Issues
1. **Agent confusion**: Clear task definition and context provision
2. **Tool limitations**: Appropriate tool selection and fallback strategies
3. **Collaboration gaps**: Clear communication protocols and handoff procedures
4. **Performance issues**: Monitoring and optimization of agent activities

### Escalation Path
1. Specialist agent (implementer, reasoner, verifier) identifies issue
2. Escalates to orchestrator
3. Orchestrator coordinates resolution across agents
4. Critical issues are reported to human users

## Continuous Improvement

### Agent Training
- Learn from successful patterns and solutions
- Adapt to project-specific requirements
- Improve collaboration with other agents
- Optimize tool usage for efficiency

### Process Refinement
- Regularly review and optimize workflows
- Update agent roles and responsibilities as needed
- Improve tool integration and capabilities
- Enhance monitoring and reporting

---

*This guide is maintained by the orchestrator agent and should be updated when agent team configuration changes.*
