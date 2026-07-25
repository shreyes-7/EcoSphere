# EcoSphere Coding Rules

Version: 1.0

---

# Purpose

This document defines the coding standards, architecture rules, development guidelines, and project conventions for EcoSphere.

All future code MUST follow these rules.

Never violate these rules unless explicitly instructed.

---

# Project Philosophy

EcoSphere is designed as a production-quality AI Building Intelligence Platform.

The code should resemble software developed by an experienced engineering team.

Primary goals:

- Maintainability
- Scalability
- Readability
- Extensibility
- Testability
- Modularity

Never prioritize short code over clean architecture.

---

# Golden Rules

## DO

✅ Extend existing code

✅ Reuse existing services

✅ Create reusable modules

✅ Follow SOLID principles

✅ Use dependency injection where appropriate

✅ Use Pydantic models

✅ Write docstrings

✅ Add type hints

✅ Keep functions small

✅ Write self-documenting code

---

## DO NOT

❌ Rewrite working modules

❌ Break existing APIs

❌ Introduce duplicated logic

❌ Create God Classes

❌ Hardcode values

❌ Create giant files

❌ Ignore error handling

❌ Ignore logging

❌ Ignore typing

---

# Project Architecture

Always preserve this architecture.

backend/

routes/

services/

services/agents/

database/

models/

schemas/

utils/

config/

mcp/

frontend/

Never flatten folders.

Never place unrelated logic together.

---

# Layer Responsibilities

## Routes

Routes should ONLY

- validate requests
- call services
- return responses

Routes should NEVER

- contain business logic
- access database directly
- call EnergyPlus directly
- modify IDF directly

Maximum route length

100 lines

---

## Services

Business logic belongs here.

Examples

Simulation

Optimization

EnergyPlus

LLM

Dashboard

Services should be reusable.

Services should not depend on HTTP.

---

## Agents

Every AI agent belongs inside

services/agents/

Agents must only focus on one responsibility.

---

## Models

Database models only.

No business logic.

---

## Schemas

Pydantic models only.

No database logic.

---

## Utils

Utility functions only.

Examples

CSV parsing

File helpers

Date helpers

Logging

Validation

---

# File Size Limits

Target maximum sizes

Routes

<300 lines

Services

<400 lines

Models

<200 lines

Utilities

<250 lines

If a file becomes too large,

split it.

---

# Naming Conventions

## Files

snake_case.py

Good

energy_agent.py

optimization_engine.py

idf_modifier.py

Bad

EnergyAgent.py

MyService.py

newCode.py

---

## Classes

PascalCase

SimulationService

SupervisorAgent

OptimizationEngine

---

## Functions

snake_case

run_simulation()

modify_idf()

calculate_energy()

---

## Variables

snake_case

simulation_result

energy_metrics

comfort_score

---

## Constants

UPPER_CASE

MAX_ITERATIONS

TARGET_PMV

DEFAULT_MODEL

---

# Type Hints

Every public function must include type hints.

Example

def run_simulation(
    simulation_id: int
) -> SimulationResult:

Never omit return types.

---

# Docstrings

Every public class

Every public function

Every service

Must contain docstrings.

Example

"""
Run an EnergyPlus simulation.

Args:
    simulation_id:
        Database simulation ID.

Returns:
    Parsed simulation results.

Raises:
    SimulationError
"""

---

# Logging

Never use print()

Always use

logger

Log

Simulation start

Simulation finish

Errors

Warnings

Optimization

Agent decisions

Execution time

Example

logger.info(
    "Energy optimization completed",
    extra={
        "energy_before":120,
        "energy_after":105
    }
)

---

# Error Handling

Never silently ignore errors.

Never write

except:
    pass

Always catch specific exceptions.

Create custom exceptions where needed.

Raise meaningful messages.

---

# Configuration

Never hardcode

Paths

Thresholds

Models

Ports

Tariffs

Iteration limits

Read everything from

.env

or

config.py

Examples

MAX_ITERATIONS

TARGET_PMV

ENERGY_THRESHOLD

OLLAMA_MODEL

CARBON_FACTOR

---

# Dependency Injection

Avoid

global objects

singleton state

Instantiate services where appropriate.

Prefer constructor injection.

---

# Database Rules

Never access SQLite directly inside routes.

Use

Repository

or

Service layer.

Always use transactions.

Always rollback on failure.

---

# API Rules

Every endpoint

Must validate inputs.

Must return Pydantic schemas.

Must return proper HTTP status codes.

Must include descriptions.

Swagger should remain clean.

---

# Response Format

Never return raw dictionaries.

Always use schemas.

Bad

return {"energy":100}

Good

return SimulationResponse(...)

---

# AI Agent Rules

Every agent must implement

analyze()

reason()

recommend()

confidence_score()

explanation()

Agents must never modify IDF directly.

Agents only recommend.

Supervisor decides.

Optimization Engine applies.

---

# Supervisor Rules

Supervisor must

collect all recommendations

resolve conflicts

produce one optimization plan

store reasoning

Never allow one agent to overwrite another directly.

---

# Explainable AI

Every recommendation must include

Reason

Confidence

Expected savings

Comfort impact

Carbon impact

No recommendation may exist without an explanation.

---

# Optimization Engine

Must be independent.

Should not depend on FastAPI.

Should be callable from

REST API

MCP

CLI

Unit tests

---

# IDF Modification

Never edit IDF manually.

Always use

eppy

or

official EnergyPlus APIs

Always preserve original file.

Generate optimized copy.

---

# Closed Loop

Loop should stop when

Maximum iterations reached

OR

Improvement below threshold

Never create infinite loops.

---

# Performance

Avoid unnecessary loops.

Cache repeated values.

Reuse objects.

Avoid unnecessary database calls.

---

# Async Rules

Use async only when beneficial.

Do not mix sync and async randomly.

Keep consistency.

---

# Imports

Standard library

↓

Third-party libraries

↓

Project imports

Alphabetically sorted.

No wildcard imports.

Never use

from module import *

---

# Comments

Comment

WHY

not

WHAT

Bad

# increment i

i += 1

Good

# Prevent infinite optimization loops

---

# Testing

Every new feature should be testable.

Avoid tightly coupled code.

Write code that can be mocked.

---

# Git Rules

Every completed phase should

Compile

Pass linting

Preserve existing functionality

No broken imports

No dead code

No TODO placeholders

---

# Code Quality Checklist

Before considering any task complete:

[ ] Project builds

[ ] No syntax errors

[ ] No duplicated code

[ ] Type hints added

[ ] Docstrings added

[ ] Logging added

[ ] Exceptions handled

[ ] Configurable values moved to config

[ ] Database updated

[ ] Schemas updated

[ ] APIs updated

[ ] Swagger updated

[ ] Existing functionality preserved

---

# Development Workflow

For every task:

1. Read existing implementation.

2. Understand architecture.

3. Extend existing code.

4. Implement feature.

5. Update database models.

6. Update schemas.

7. Update services.

8. Update routes.

9. Update documentation.

10. Verify project builds.

11. Ensure backward compatibility.

12. Only then proceed to the next task.

---

# Final Principle

Every line of code should make EcoSphere more modular, more maintainable, and easier to extend.

When multiple implementation choices exist:

Choose the solution that best supports long-term scalability and clean architecture over the shortest implementation.