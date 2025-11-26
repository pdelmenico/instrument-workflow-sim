# Instrument Workflow Simulation - Project Context

## Project Overview

Building an in-house discrete-event simulation application for timing analysis of complex instrument workflows in diagnostic and clinical chemistry instruments. The application helps systems engineers identify bottlenecks, resource constraints, and scheduling challenges during initial system definition phases.

**Customer Base:** Consultancy with ~200 engineers serving medical device clients from startups to Fortune 500 companies.

**Novel Challenge:** No historical data exists for new instrument designs. Simulation must work with customer-provided timing estimates (fixed, triangular, exponential distributions) rather than empirical data fitting.

## Phase 1a Scope

Deliver a working discrete-event simulation engine that:
- Accepts workflow definitions as JSON (schema-validated)
- Simulates single-sample and synchronized batch scenarios
- Generates detailed event logs showing device contention and queue wait times
- Produces summary statistics (device utilization, bottleneck identification)
- Uses SimPy as the simulation engine with Flask API wrapper

**Timeline:** 3 weeks to completion

## Key Architectural Decisions

1. **Separation of Concerns**
   - Base workflow templates (reusable device and operation definitions)
   - Scenario configurations (parameterize sample flow through system)
   - This allows engineers to define an instrument once, test multiple "what-if" scenarios

2. **Modular Backend**
   - SimPy is Phase 1a default but architecture supports pluggable alternatives
   - Enables future experimentation with other simulation engines

3. **Local Network Deployment**
   - Faster development iteration than cloud hosting
   - Team accesses via centralized internal server
   - Can migrate to cloud later if needed

4. **Timing Models Supported**
   - Phase 1a: fixed, triangular, exponential
   - Phase 1b/1c: add normal, lognormal, uniform
   - Stochastic models essential because engineers make educated estimates, not measurements

5. **Event Logging Architecture**
   - Every state change recorded with timestamp, device, sample, operation
   - Enables post-simulation analysis, bottleneck detection, throughput calculation
   - Foundation for visualization in Phase 1d

## Workflow Progression Model

Engineering teams typically follow this analysis pattern:
1. **Single sample** - Understand basic workflow structure
2. **Synchronized batch** - Identify resource contention
3. **Staggered/async** - Explore scheduling optimizations
4. **Steady-state** - Calculate continuous throughput

Phase 1a supports steps 1-2. Steps 3-4 deferred to Phase 1b/1c.

## Technology Stack

- **Backend:** Flask (Python web framework)
- **Simulation Engine:** SimPy (discrete-event simulation)
- **Data Analysis:** Pandas (event log processing)
- **Statistics:** NumPy (distribution sampling)
- **Validation:** jsonschema (JSON schema compliance)
- **Database:** SQLite (Phase 1a), upgrade to PostgreSQL in Phase 1c if needed

## Development Constraints

- **No external dependencies beyond listed above**
- **Code must be testable** - unit tests for validators, integration tests for end-to-end workflows
- **API must be RESTful** - GET/POST operations on /api/simulate, /api/simulation/{run_id}/events, etc.
- **Deterministic when seeded** - same workflow + scenario + random_seed must produce identical event logs
- **Performance target:** 100-sample × 20-operation workflows complete in <2 seconds

## Known Limitations (Phase 1a)

- **DAG handling:** Only linear sequences (each operation has ≤1 predecessor). Phase 1b will support arbitrary DAGs.
- **Resource constraints:** No consumable inventory tracking or conditional cleaning. Phase 1b feature.
- **Arrival patterns:** Only synchronized and single. Staggered/continuous in Phase 1c.
- **No visualization:** Raw events + statistics only. Plotly integration Phase 1d.

## Success Criteria

Phase 1a is complete when:

1. ✅ WorkflowValidator rejects workflows with circular dependencies, missing device references, invalid timing
2. ✅ ScenarioValidator accepts synchronized and single patterns, rejects invalid configs
3. ✅ SimulationEngine produces event logs with correct timestamps, device contention, queue wait times
4. ✅ Statistics accurately identify bottleneck device and queue delays
5. ✅ Flask API accepts JSON, returns event log + summary in <1 sec for 10-sample batch
6. ✅ All timing distributions sample correctly and deterministically with seed
7. ✅ Comprehensive test suite covering single/multi-device, sync batch, validation failures
8. ✅ Documentation and example workflows for team adoption

## Next Steps Before Coding

Answer these questions:

1. **Database:** SQLite locally for Phase 1a, or proper database?
2. **Random seed:** Allow user-provided seed for reproducibility, or always random?
3. **Event filtering:** Should API support filtering by sample_id/operation_id/device_id in Phase 1a?
4. **Performance targets:** Any specific timing requirements?
5. **Error handling:** For infinite waits, use max_simulation_time timeout?

## References

- Phase 1a Specification: `Phase_1a_Implementation_Specification.md`
- Workflow JSON Schema: `Workflow & Scenario JSON Schema.txt`
- Intermediate Format Docs: `Intermediate_Workflow_Definition_Format__CSV-based_.md`
- Client Template Format: `Client_Workflow_Template_Format__CSV___Metadata_.md`
