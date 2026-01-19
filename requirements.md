---
product: "CrewAI News Manager (Supabase)"
version: "0.0.1"
author: "Product Team"
date: "2026-01-13"
status: "Draft"
---

# 0. TL;DR
A multi-agent CrewAI system that manages Sing for Hope news articles stored in Supabase. The agent can read, draft, validate, enrich, and propose updates to news records, but **cannot publish without Human-in-the-Loop (HITL) approval**. The system exposes a simple **2-column chat interface** (chat + agent logs), supports **LLM switching via OpenRouter**, and follows a **test-first (TDD) development strategy** where all tests initially fail and must pass to mark completion.

---

# 1. Executive Summary

## 1.1 Product Overview
The CrewAI News Manager is a Python-based AI system built using CrewAI that interfaces directly with a Supabase PostgreSQL database containing news articles. It accepts instructions through a chat interface, delegates tasks to specialized micro-agents, and compiles outputs through an orchestrator agent.

The system is designed to assist editors and internal staff in safely managing news content by automating drafting, validation, and enrichment—while enforcing editorial control via mandatory HITL approval.

## 1.2 Key Objectives
- Enable safe AI-assisted updates to Supabase news records
- Improve content quality and consistency
- Reduce factual and editorial errors before publishing
- Enforce a strict HITL workflow for all write operations
- Provide transparency through detailed agent/tool execution logs
- Enable rapid iteration and reliability via test-driven development

## 1.3 Key Features
- **Supabase Read/Write (No Delete)** with schema awareness
- **Multi-Agent Architecture** with orchestrator + micro-agents
- **Human-in-the-Loop Approval Gate** before any overwrite
- **Grammar, Tone, Policy, and PII Scanning**
- **External Fact Verification**
- **SEO & Metadata Generation**
- **LLM Model Switching (OpenRouter)**
- **2-Column Chat UI (Chat + Logs)**
- **Test-First Development as Definition of Done**

## 1.4 Stakeholders & Roles
- **Product Owner**: Defines workflows, constraints, success criteria
- **Developer**: Implements agents, tools, UI, and tests
- **Editor / Reviewer (HITL)**: Approves or rejects proposed changes
- **Content Team**: Uses the system to manage news content

## 1.5 Risks & Mitigations
- **Accidental Overwrites** → Mitigated by proposal staging + HITL
- **Hallucinated Content** → Mitigated by fact-check tools + reviewer flags
- **Schema Drift** → Mitigated by Supabase Schema Explorer agent
- **Silent Failures** → Mitigated by mandatory logs + failing tests

---

# 2. Goals, Context & Problem Statement

## 2.1 Goals & Objectives
Create a reliable AI system that can safely assist with managing Supabase-based news content while preserving human editorial control and providing full transparency.

## 2.2 Background & Target Audience
**Primary Users**
- Editors
- Content managers
- Internal operations staff

**Secondary Users**
- Developers
- QA reviewers

## 2.3 Current State
News content exists in Supabase with fields such as `news_title`, `tiny` (HTML), `news_url`, and image metadata. Updates are manual, error-prone, and lack automated validation or review support.

## 2.4 Problem Statement
How might we automate content drafting and updating for Supabase news articles without compromising accuracy, safety, or editorial oversight?

## 2.5 Impact
- Faster editorial workflows
- Reduced errors and inconsistencies
- Improved auditability
- Clear AI-assisted but human-approved publishing flow

---

# 3. Scope Definition

## 3.1 In Scope
- Chat-based task intake
- Reading existing Supabase news records
- Proposing updates (not auto-publishing)
- Multi-agent orchestration
- Validation, verification, and enrichment
- HITL approval workflow
- Logging and traceability
- Test-driven development enforcement

## 3.2 Out of Scope
- Automatic publishing without approval
- Deleting news records
- Full CMS replacement
- Multi-language support (for MVP)

## 3.3 Assumptions
- Supabase schema is accessible
- HTML content is primarily stored in `tiny`
- OpenRouter API is available
- Team members act as HITL reviewers

## 3.4 Key Dependencies & Decisions
- **Backend**: Supabase
- **AI Framework**: CrewAI
- **LLM Routing**: OpenRouter
- **UI**: Streamlit (MVP)
- **Verification**: External search APIs (e.g., Tavily)

---

# 4. Success Metrics & KPIs

## 4.1 Primary Metrics
- Time from request → proposal
- Approval rate without revisions
- Number of errors caught pre-approval
- Zero unauthorized overwrites

## 4.2 Secondary Metrics
- Editor satisfaction
- Reduction in manual editing steps
- Test coverage completeness

## 4.3 Targets
- 50%+ reduction in drafting time
- 0 delete operations
- 100% test pass rate at completion

---

# 5. Requirements

## 5.1 Functional Requirements

### 5.1.1 Chat Task Intake
- Accept natural language instructions
- Ask clarifying questions when intent or target is ambiguous

### 5.1.2 Supabase Schema Explorer
- Inspect table structure
- Validate fields before read/write

### 5.1.3 Article Fetcher
- Fetch by `id` or `news_url`
- Return structured summaries for editing

### 5.1.4 Draft & Enrichment
- Update content fields (`tiny`, excerpt, title)
- Generate human-readable change summaries

### 5.1.5 Validation Pipeline
- Grammar & syntax checks
- Policy & safety scanning
- PII detection
- Tone & bias analysis

### 5.1.6 Fact Verification
- Detect claims requiring verification
- Run external searches
- Attach confidence notes

### 5.1.7 HITL Workflow
- Block writes without approval
- Support approve / reject / revise
- Log reviewer decision

### 5.1.8 Supabase Write Rules
- Allow updates only after approval
- Deletion is permanently disabled

### 5.1.9 Logs & Observability
- Display agents and tools used
- Show step-by-step execution summaries
- Redact sensitive data

### 5.1.10 LLM Switching
- Allow model selection per session or task
- Apply consistently across agents

## 5.2 Non-Functional Requirements
- Secure secret handling
- Clear audit trail
- Graceful error handling
- Predictable execution behavior

## 5.3 User Stories
- As an editor, I want AI-drafted updates I can safely approve.
- As a reviewer, I want to see exactly what changed and why.
- As a developer, I want deterministic behavior verified by tests.

## 5.4 Technical Requirements

### 5.4.1 Observed Supabase Fields
Includes but is not limited to:
`id`, `news_title`, `tiny`, `news_url`, `news_excerpt`, `news_image`, `news_status`, `draft`, `featured`, `news_image_caption`

### 5.4.2 Agent Architecture
- **Orchestrator Agent**
- **Micro-Agents**
  - Schema Explorer
  - Article Fetcher
  - SQL/Supabase Executor
  - Grammar Validator
  - Hallucination Checker
  - SEO Generator
  - Policy Scanner
  - PII Detector
  - Tone/Bias Analyzer
  - Image Prompt Generator
  - Article Status Updater

---

# 6. User Flows

## 6.1 Update Existing Article
Chat → Clarify → Fetch → Draft → Validate → Verify → Propose → HITL Approve → Commit → Log

## 6.2 Draft From Title
Chat → Generate Skeleton → Validate → Propose → Approve → Commit

## 6.3 Reject & Revise
Reject → Feedback → Redraft → Revalidate → Re-approve

---

# 7. Design & User Experience

## 7.1 Interface
- **Left Column**: Chat interaction
- **Right Column**: Logs, agents used, tools invoked, summaries

## 7.2 UX Principles
- Transparency over opacity
- Explicit approval over automation
- Minimal UI, maximal clarity

---

# 8. Risks & Mitigations

## 8.1 Technical Risks
- LLM inconsistency → mitigated by HITL + tests
- Schema changes → mitigated by schema explorer

## 8.2 Operational Risks
- Over-trust in AI → mitigated by mandatory review
- Silent failures → mitigated by failing tests and logs

---

# 9. Roadmap

## 9.1 MVP
- Core agents
- Supabase integration
- HITL workflow
- Streamlit UI
- Initial test suite (failing first)

## 9.2 Post-MVP
- Versioning
- Diff UI
- Reviewer roles
- CI integration

## 9.3 Long-Term Vision
A reliable editorial AI assistant that augments—not replaces—human judgment, with auditable, test-backed behavior.

---

# 10. Development & Quality Assurance Strategy

## 10.1 Test-Driven Development (TDD)
All behaviors must be defined by tests **before implementation**. Tests are expected to fail initially.

## 10.2 Required Test Categories
- Agent routing & behavior
- Supabase read/write constraints
- HITL enforcement
- Validation & safety
- Fact verification
- UI interaction & logging

## 10.3 Completion Criteria (Definition of Done)
The project is complete only when:
- All tests pass
- No deletes are possible
- All writes require approval
- Logs are complete and accurate
- Behavior matches tests exactly

## 10.4 Regression Policy
- New features require new tests
- Any failing test blocks completion
- CI must enforce full test pass

---
