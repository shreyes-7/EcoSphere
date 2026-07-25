# EcoSphere - Development Tasks

# Overview

EcoSphere is an AI-powered autonomous building optimization platform built around EnergyPlus, FastAPI, SQLite, Ollama, and (later) MCP.

The project already supports:

- FastAPI backend
- SQLite database
- EnergyPlus simulation
- Ollama integration
- Simulation APIs
- Logging
- Typed schemas
- Exception handling

The goal is to transform EcoSphere into an autonomous AI Building Intelligence Platform capable of closed-loop optimization using multiple collaborating AI agents.

---

# IMPORTANT RULES

Before implementing any task:

- DO NOT rewrite existing working code.
- Extend existing architecture only.
- Preserve coding style.
- Keep modules small.
- Use SOLID principles.
- Add docstrings.
- Add type hints.
- Update imports.
- Update schemas.
- Update database migrations if required.
- Ensure the project compiles after every phase.

Every phase must be completed before moving to the next.

---

# PROJECT GOAL

Final pipeline

EnergyPlus
    ↓
Simulation Metrics
    ↓
Multi-Agent AI
    ↓
Supervisor Decision
    ↓
Modify Building
    ↓
Run EnergyPlus
    ↓
Compare Results
    ↓
Repeat Until Convergence

---

# ===========================================================
# PHASE 1
# Multi-Agent Framework
# ===========================================================

## Goal

Replace the single LLM workflow with a modular multi-agent architecture.

## Create

services/agents/

base_agent.py

energy_agent.py

comfort_agent.py

cost_agent.py

sustainability_agent.py

supervisor_agent.py

## Requirements

Create an abstract BaseAgent.

Each agent must expose

- analyze()
- reason()
- recommend()
- confidence_score()
- explanation()

Every recommendation must return

- recommendation
- confidence
- explanation
- expected_savings

Supervisor Agent should

- coordinate all agents
- merge recommendations
- resolve conflicts
- generate final optimization plan

Acceptance Criteria

✔ Agents are reusable

✔ Supervisor can aggregate all responses

✔ Existing APIs remain functional

---

# ===========================================================
# PHASE 2
# Optimization Engine
# ===========================================================

Create

services/optimization_engine.py

Responsibilities

Run complete optimization workflow

Collect metrics

Call Supervisor

Receive recommendations

Apply optimization

Track iterations

Persist results

Acceptance Criteria

✔ Optimization engine is independent

✔ Reusable from API and MCP

---

# ===========================================================
# PHASE 3
# Database Expansion
# ===========================================================

Create new models

OptimizationHistory

AgentDecision

AgentExplanation

ClosedLoopRun

MetricsHistory

Store

simulation_id

iteration

agent

recommendation

confidence

reason

expected_savings

actual_savings

timestamp

Acceptance Criteria

✔ All optimization history stored

✔ Existing database preserved

---

# ===========================================================
# PHASE 4
# Explainable AI
# ===========================================================

Every optimization decision must include

Reason

Confidence

Expected Savings

Comfort Impact

Carbon Impact

Example

Cooling Setpoint

22°C → 24°C

Reason

Outside temperature decreased

Expected Saving

11%

Confidence

94%

Acceptance Criteria

✔ Every optimization has explanation

✔ Explanations stored in database

✔ Explanations accessible via API

---

# ===========================================================
# PHASE 5
# Automatic IDF Modification
# ===========================================================

Implement

services/idf_modifier.py

Use

eppy

or

PyEnergyPlus

Never manually edit raw text.

Support

Cooling Setpoint

Heating Setpoint

Lighting Schedule

HVAC Schedule

Occupancy Schedule

Acceptance Criteria

✔ New IDF generated safely

✔ Original IDF preserved

---

# ===========================================================
# PHASE 6
# Closed Loop Optimization
# ===========================================================

Implement

Simulation

↓

Metrics

↓

Agents

↓

Optimization

↓

Modify IDF

↓

Run Simulation Again

↓

Compare

↓

Repeat

Stop Conditions

Maximum Iterations

Target Energy Reduction

Minimum Improvement Threshold

Acceptance Criteria

✔ Fully autonomous loop

✔ Configurable stopping criteria

---

# ===========================================================
# PHASE 7
# MCP Server
# ===========================================================

Create

mcp/server.py

Expose tools

run_simulation()

modify_idf()

read_results()

compare_runs()

history()

optimize_building()

Supervisor Agent should use MCP tools whenever possible.

Acceptance Criteria

✔ MCP server operational

✔ Tool calling works

---

# ===========================================================
# PHASE 8
# REST APIs
# ===========================================================

Create

POST /optimize/start

GET /optimize/status/{id}

GET /optimize/history

GET /optimize/explanation/{id}

GET /optimize/compare

GET /dashboard/summary

GET /agents/latest

Acceptance Criteria

✔ APIs documented

✔ Swagger updated

---

# ===========================================================
# PHASE 9
# Dashboard
# ===========================================================

Create modern dashboard

Pages

Overview

Optimization

Simulation History

Agent Decisions

Analytics

Charts

Energy

PMV

Carbon

HVAC

Comfort

Confidence

Timeline

Acceptance Criteria

✔ Responsive

✔ Professional UI

✔ Real-time updates

---

# ===========================================================
# PHASE 10
# Historical Analytics
# ===========================================================

Compare

Baseline

Iteration 1

Iteration N

Show

Energy

Comfort

Carbon

Cost

HVAC Runtime

PMV

Acceptance Criteria

✔ Historical comparisons

✔ Downloadable reports

---

# ===========================================================
# PHASE 11
# Logging & Monitoring
# ===========================================================

Each agent should log

Recommendation

Reason

Confidence

Execution Time

Optimization Result

Create structured logs.

Acceptance Criteria

✔ Logs searchable

✔ Consistent formatting

---

# ===========================================================
# PHASE 12
# Polish
# ===========================================================

Improve

Error handling

Validation

Documentation

Comments

Typing

Performance

Testing

README

Architecture diagrams

Acceptance Criteria

✔ Production-ready

✔ Clean architecture

✔ No duplicated code

✔ No dead code

✔ All APIs documented

✔ All modules integrated

---

# Definition of Done

The project is complete when the following pipeline works automatically:

Upload IDF

↓

Upload Weather File

↓

Run Baseline Simulation

↓

Extract Metrics

↓

Energy Agent

↓

Comfort Agent

↓

Cost Agent

↓

Sustainability Agent

↓

Supervisor Agent

↓

Generate Explainable Decision

↓

Modify IDF

↓

Run Simulation Again

↓

Measure Improvement

↓

Repeat Until Convergence

↓

Store Complete History

↓

Display Dashboard

↓

Expose Everything Through REST APIs and MCP

---

# Development Workflow

For every phase:

1. Understand existing code.
2. Identify extension points.
3. Implement feature.
4. Update database if needed.
5. Update schemas.
6. Update API.
7. Update documentation.
8. Verify project builds.
9. Run tests.
10. Commit changes.

Never start the next phase until the current phase is fully complete.