# Phase 1a Documentation Index

**Ready for Claude Code Session** ✨

All documents have been prepared and are located in `/home/claude/`. Start your Claude Code session by reviewing these files in order.

---

## 📋 Quick Start (Read in This Order)

### 1. **PROJECT_CONTEXT.md** ⭐ START HERE
   - **Purpose:** Project overview, customer context, key architectural decisions
   - **Read time:** 5 minutes
   - **What you'll learn:** Why this project exists, what problem it solves, high-level design
   - **Key decisions:** SimPy backend, local network deployment, workflow template separation

### 2. **IMPLEMENTATION_CHECKLIST.md** 
   - **Purpose:** Week-by-week task breakdown, acceptance criteria, session milestones
   - **Read time:** 10 minutes
   - **What you'll learn:** Exactly what needs to be built each week, test counts, deliverables
   - **Use during:** Implementation as a checklist to track progress

### 3. **Phase_1a_Implementation_Specification.md**
   - **Purpose:** Complete technical specification with class designs, algorithm descriptions, test cases
   - **Read time:** 20 minutes (skim sections 1-5; detailed reference for sections 6-8)
   - **What you'll learn:** System architecture, data models, Python class structure, API endpoints
   - **Reference:** Keep open while coding—Section 3 is the data model reference

### 4. **CODING_GUIDELINES.md**
   - **Purpose:** Python coding standards, project structure, testing approach, error handling
   - **Read time:** 15 minutes (skim for reference, not memorization)
   - **What you'll learn:** Code style, naming conventions, test patterns, performance considerations
   - **Reference:** Keep nearby for consistency checks during code review

### 5. **API_REFERENCE.md**
   - **Purpose:** Flask endpoint documentation with curl examples and response schemas
   - **Read time:** 10 minutes
   - **What you'll learn:** API contract, request/response formats, example usage
   - **Reference:** Use when implementing Week 3 endpoints

### 6. **EXAMPLE_WORKFLOWS.md**
   - **Purpose:** Three complete, runnable example workflows for testing
   - **Read time:** 15 minutes
   - **What you'll learn:** Real workflow examples, expected simulation outputs, test scenarios
   - **Use during:** Write tests using these examples; copy to `examples/` directory

---

## 📁 Document Map

```
PROJECT CONTEXT
├── PROJECT_CONTEXT.md          ← Start here: project overview
├── Phase_1a_Implementation_Specification.md  ← Technical spec, data models
├── CODING_GUIDELINES.md        ← Code standards & testing approach
├── API_REFERENCE.md            ← API endpoints & usage
├── EXAMPLE_WORKFLOWS.md        ← Three complete example workflows
├── IMPLEMENTATION_CHECKLIST.md ← Week-by-week task breakdown
│
REFERENCE DOCUMENTS (from project files)
├── Workflow & Scenario JSON Schema.txt
├── Intermediate_Workflow_Definition_Format__CSV-based_.md
└── Client_Workflow_Template_Format__CSV___Metadata_.md
```

---

## 🎯 What Each Document Does

### For Getting Started
- **PROJECT_CONTEXT.md:** Understand *why* and *what*—business context and high-level design
- **IMPLEMENTATION_CHECKLIST.md:** Understand the *how*—task breakdown and deliverables

### For Building Code
- **Phase_1a_Implementation_Specification.md:** Blueprint for class structure and algorithms
- **CODING_GUIDELINES.md:** Code style, patterns, and testing standards
- **API_REFERENCE.md:** Contract for Flask endpoints

### For Testing & Validation
- **EXAMPLE_WORKFLOWS.md:** Concrete workflows to test against
- **IMPLEMENTATION_CHECKLIST.md:** Acceptance criteria and test counts

---

## 🔑 Key Takeaways

### Architecture (from PROJECT_CONTEXT.md)
- **Goal:** Identify bottlenecks in novel instrument designs before physical prototyping
- **Approach:** Discrete-event simulation with customer-provided timing estimates
- **Tech Stack:** Flask + SimPy + Pandas + NumPy + Plotly (Phase 1d)
- **Workflow Model:** Separate reusable workflow templates from scenario configurations

### Implementation Phases
- **Phase 1a (this sprint):** Core simulation engine with JSON input, event logging, summary statistics
- **Phase 1b:** CSV→YAML conversion, DAG support, consumable inventory tracking
- **Phase 1c:** Web UI, database persistence, advanced analytics
- **Phase 1d:** Plotly visualization, live docs
- **Phase 1e:** Workflow canvas editor

### Success Criteria (from IMPLEMENTATION_CHECKLIST.md)
✅ 70+ tests passing, >90% code coverage  
✅ Single sample and synchronized batch simulations working  
✅ Event logs with correct timestamps, device contention, queue wait times  
✅ Statistics accurately identifying bottleneck devices  
✅ Flask API responding in <1 sec for 10-sample batch  
✅ All timing distributions (fixed, triangular, exponential) deterministic with seed  

---

## 📊 File Structure You'll Create

```
instrument-workflow-sim/
├── src/
│   └── simulation/
│       ├── __init__.py
│       ├── models.py           ← Week 1
│       ├── timing.py           ← Week 1
│       ├── validators.py       ← Week 1
│       └── core.py             ← Week 2
├── api/
│   ├── __init__.py
│   └── routes.py               ← Week 3
├── tests/
│   ├── __init__.py
│   ├── conftest.py             ← Week 1
│   ├── test_models.py          ← Week 1
│   ├── test_timing.py          ← Week 1
│   ├── test_validators.py      ← Week 1
│   ├── test_simulation_engine.py ← Week 2
│   ├── test_api_endpoints.py   ← Week 3
│   └── test_integration.py     ← Week 3
├── examples/
│   ├── single_sample_pcr.json
│   ├── synchronized_batch_analyzer.json
│   └── multi_device_immunoassay.json
├── requirements.txt
├── setup.py
├── README.md
└── main.py
```

---

## ⏱️ Time Estimates

| Section | Time | Priority |
|---------|------|----------|
| Read PROJECT_CONTEXT | 5 min | **MUST READ** |
| Read IMPLEMENTATION_CHECKLIST | 10 min | **MUST READ** |
| Skim Phase_1a_spec (sections 1-5) | 20 min | Important |
| Read CODING_GUIDELINES | 15 min | Important |
| Review API_REFERENCE | 10 min | Reference |
| Study EXAMPLE_WORKFLOWS | 15 min | Reference |
| **Total pre-coding time** | **75 minutes** | ~1 hour |

---

## 🚀 Session Startup Procedure

### Step 1: Environment Setup (5 min)
```bash
# Create project directory
mkdir instrument-workflow-sim
cd instrument-workflow-sim

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Document Review (75 min)
1. Read PROJECT_CONTEXT.md (5 min)
2. Skim IMPLEMENTATION_CHECKLIST.md weeks 1-3 (10 min)
3. Skim Phase_1a_spec sections 1-5 (20 min)
4. Review CODING_GUIDELINES.md (15 min)
5. Reference API_REFERENCE.md and EXAMPLE_WORKFLOWS.md (25 min)

### Step 3: Project Structure Setup (10 min)
- Create directories per file structure above
- Create `__init__.py` files
- Copy example workflows to `examples/`
- Create `conftest.py` with pytest fixtures

### Step 4: Week 1 Implementation Begins
- Start with Task 1.1 from IMPLEMENTATION_CHECKLIST.md
- Use Phase_1a_Implementation_Specification.md Section 4 as coding reference
- Follow CODING_GUIDELINES.md for all code
- Run tests frequently: `pytest tests/ -v`

---

## 📞 Questions During Implementation?

If stuck, check:

1. **"What should this class do?"** → Phase_1a_spec Section 4
2. **"What's the code style?"** → CODING_GUIDELINES.md
3. **"What tests do I need?"** → Phase_1a_spec Section 6
4. **"What format should this JSON have?"** → EXAMPLE_WORKFLOWS.md or API_REFERENCE.md
5. **"What's the week's task?"** → IMPLEMENTATION_CHECKLIST.md

---

## ✨ You're Ready!

All documents are prepared. When you start your Claude Code session, begin with PROJECT_CONTEXT.md and work through the checklist.

**Total build time: 3 weeks**  
**Target: 70+ tests, >90% coverage, working simulation engine**

Good luck! 💙❤️ This is a solid specification—execute it well and you'll have a powerful foundation for Phase 1b. ✨

