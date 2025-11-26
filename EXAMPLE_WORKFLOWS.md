# Example Workflows for Phase 1a Testing

These examples are complete, valid workflows that can be used directly for testing and development.

## Example 1: Single Sample PCR (Minimal Workflow)

**Purpose:** Simplest possible workflow for validation and basic simulation.
- 1 sample
- 2 devices (liquid handler, thermal cycler)
- 3 sequential operations
- Fixed timing only

```json
{
  "workflow_id": "single-sample-pcr-minimal",
  "workflow_name": "Single Sample PCR - Minimal",
  "workflow_version": "1.0",
  "description": "Minimal PCR workflow for Phase 1a testing. One sample, two devices, all fixed timing.",
  
  "devices": [
    {
      "device_id": "liquid_handler",
      "device_name": "Liquid Handler",
      "resource_capacity": 1,
      "scheduling_policy": "FIFO"
    },
    {
      "device_id": "thermal_cycler",
      "device_name": "Thermal Cycler",
      "resource_capacity": 1,
      "scheduling_policy": "FIFO"
    }
  ],
  
  "operations": [
    {
      "operation_id": "load_sample",
      "operation_name": "Load Sample",
      "device_id": "liquid_handler",
      "timing": {
        "type": "fixed",
        "value": 5.0
      },
      "operation_type": "setup"
    },
    {
      "operation_id": "add_reagent",
      "operation_name": "Add PCR Reagent",
      "device_id": "liquid_handler",
      "timing": {
        "type": "fixed",
        "value": 8.0
      },
      "operation_type": "processing"
    },
    {
      "operation_id": "amplify",
      "operation_name": "PCR Amplification (35 cycles)",
      "device_id": "thermal_cycler",
      "timing": {
        "type": "fixed",
        "value": 3600.0
      },
      "operation_type": "processing"
    }
  ],
  
  "base_sequence": [
    {
      "sequence_id": 1,
      "operation_id": "load_sample",
      "predecessors": []
    },
    {
      "sequence_id": 2,
      "operation_id": "add_reagent",
      "predecessors": ["load_sample"]
    },
    {
      "sequence_id": 3,
      "operation_id": "amplify",
      "predecessors": ["add_reagent"]
    }
  ]
}
```

**Expected Simulation Output (Single Sample, Single Scenario):**
- Total simulation time: ~3613 seconds (5 + 8 + 3600)
- Samples completed: 1
- Device utilization: liquid_handler ~0.36% (13 sec / 3613 sec), thermal_cycler ~99.6%
- Bottleneck device: thermal_cycler

---

## Example 2: Synchronized Batch Chemistry Analyzer

**Purpose:** Test device contention with synchronized batch.
- 3 samples entering at t=0
- 3 devices (autosampler, centrifuge, analyzer)
- Multiple operations with timing distributions (fixed + triangular)
- Demonstrates queuing effects

```json
{
  "workflow_id": "synchronized-batch-analyzer",
  "workflow_name": "Chemistry Panel - Synchronized Batch",
  "workflow_version": "1.0",
  "description": "3-sample synchronized batch on chemistry analyzer. Tests device contention and queuing.",
  
  "devices": [
    {
      "device_id": "autosampler",
      "device_name": "96-Well Autosampler",
      "resource_capacity": 1,
      "scheduling_policy": "FIFO"
    },
    {
      "device_id": "centrifuge",
      "device_name": "Centrifuge",
      "resource_capacity": 1,
      "scheduling_policy": "FIFO"
    },
    {
      "device_id": "analyzer",
      "device_name": "Chemistry Analyzer",
      "resource_capacity": 2,
      "scheduling_policy": "FIFO"
    }
  ],
  
  "operations": [
    {
      "operation_id": "position_sample",
      "operation_name": "Position Sample in Autosampler",
      "device_id": "autosampler",
      "timing": {
        "type": "fixed",
        "value": 3.0
      },
      "operation_type": "setup"
    },
    {
      "operation_id": "centrifuge_spin",
      "operation_name": "Centrifuge Sample",
      "device_id": "centrifuge",
      "timing": {
        "type": "fixed",
        "value": 120.0
      },
      "operation_type": "processing"
    },
    {
      "operation_id": "aspirate",
      "operation_name": "Aspirate Sample",
      "device_id": "analyzer",
      "timing": {
        "type": "triangular",
        "min": 10.0,
        "mode": 12.0,
        "max": 15.0
      },
      "operation_type": "processing"
    },
    {
      "operation_id": "dispense_reagent",
      "operation_name": "Dispense Reagent",
      "device_id": "analyzer",
      "timing": {
        "type": "triangular",
        "min": 8.0,
        "mode": 10.0,
        "max": 12.0
      },
      "operation_type": "processing"
    },
    {
      "operation_id": "incubate",
      "operation_name": "Incubation",
      "device_id": "analyzer",
      "timing": {
        "type": "fixed",
        "value": 180.0
      },
      "operation_type": "processing"
    },
    {
      "operation_id": "measure",
      "operation_name": "Measure Absorbance",
      "device_id": "analyzer",
      "timing": {
        "type": "triangular",
        "min": 3.0,
        "mode": 4.0,
        "max": 5.0
      },
      "operation_type": "processing"
    }
  ],
  
  "base_sequence": [
    {
      "sequence_id": 1,
      "operation_id": "position_sample",
      "predecessors": []
    },
    {
      "sequence_id": 2,
      "operation_id": "centrifuge_spin",
      "predecessors": ["position_sample"]
    },
    {
      "sequence_id": 3,
      "operation_id": "aspirate",
      "predecessors": ["centrifuge_spin"]
    },
    {
      "sequence_id": 4,
      "operation_id": "dispense_reagent",
      "predecessors": ["aspirate"]
    },
    {
      "sequence_id": 5,
      "operation_id": "incubate",
      "predecessors": ["dispense_reagent"]
    },
    {
      "sequence_id": 6,
      "operation_id": "measure",
      "predecessors": ["incubate"]
    }
  ]
}
```

**Expected Simulation Output (3 Samples Synchronized):**
- Total simulation time: ~450-500 seconds (due to queuing on analyzer with capacity=2)
- Samples completed: 3
- Autosampler: Sequential processing of 3 samples, low utilization
- Centrifuge: Sequential processing of 3 samples, ~80% utilization (120+120+120=360 sec out of ~450)
- Analyzer: Capacity 2, so samples 1-2 run in parallel, sample 3 waits; high utilization (~90-95%)
- Bottleneck: Analyzer (capacity limited to 2)
- Queue delays: Samples 2 and 3 experience wait times at analyzer

---

## Example 3: Multi-Device Workflow with Exponential Timing

**Purpose:** Test exponential distribution and more complex device topology.
- 2 samples (single scenario)
- 4 devices (preparation, heating, detection, cooling)
- Mix of fixed, triangular, and exponential timing
- Demonstrates realistic analytical workflow

```json
{
  "workflow_id": "multi-device-immunoassay",
  "workflow_name": "Immunoassay Analysis - Multi-Device",
  "workflow_version": "1.0",
  "description": "Multi-device immunoassay workflow with exponential timing. Tests complex device scheduling.",
  
  "devices": [
    {
      "device_id": "prep_station",
      "device_name": "Sample Prep Station",
      "resource_capacity": 1,
      "scheduling_policy": "FIFO"
    },
    {
      "device_id": "heating_block",
      "device_name": "Heating Block (37°C)",
      "resource_capacity": 2,
      "scheduling_policy": "FIFO"
    },
    {
      "device_id": "detector",
      "device_name": "Absorbance Detector",
      "resource_capacity": 1,
      "scheduling_policy": "FIFO"
    },
    {
      "device_id": "cooling_station",
      "device_name": "Cooling Station (4°C)",
      "resource_capacity": 2,
      "scheduling_policy": "FIFO"
    }
  ],
  
  "operations": [
    {
      "operation_id": "transfer_to_reaction_vessel",
      "operation_name": "Transfer Sample to Reaction Vessel",
      "device_id": "prep_station",
      "timing": {
        "type": "fixed",
        "value": 8.0
      },
      "operation_type": "setup"
    },
    {
      "operation_id": "add_antibody",
      "operation_name": "Add Primary Antibody",
      "device_id": "prep_station",
      "timing": {
        "type": "triangular",
        "min": 3.0,
        "mode": 4.0,
        "max": 6.0
      },
      "operation_type": "processing"
    },
    {
      "operation_id": "incubate_antibody",
      "operation_name": "Incubate with Primary Antibody",
      "device_id": "heating_block",
      "timing": {
        "type": "fixed",
        "value": 600.0
      },
      "operation_type": "processing"
    },
    {
      "operation_id": "add_secondary_antibody",
      "operation_name": "Add Secondary Antibody",
      "device_id": "prep_station",
      "timing": {
        "type": "triangular",
        "min": 3.0,
        "mode": 4.0,
        "max": 6.0
      },
      "operation_type": "processing"
    },
    {
      "operation_id": "incubate_secondary",
      "operation_name": "Incubate with Secondary Antibody",
      "device_id": "heating_block",
      "timing": {
        "type": "fixed",
        "value": 600.0
      },
      "operation_type": "processing"
    },
    {
      "operation_id": "wash",
      "operation_name": "Wash Reaction Vessel",
      "device_id": "prep_station",
      "timing": {
        "type": "triangular",
        "min": 15.0,
        "mode": 20.0,
        "max": 30.0
      },
      "operation_type": "processing"
    },
    {
      "operation_id": "add_substrate",
      "operation_name": "Add Chromogenic Substrate",
      "device_id": "prep_station",
      "timing": {
        "type": "fixed",
        "value": 4.0
      },
      "operation_type": "processing"
    },
    {
      "operation_id": "incubate_substrate",
      "operation_name": "Incubate Substrate Reaction",
      "device_id": "heating_block",
      "timing": {
        "type": "exponential",
        "mean": 420.0
      },
      "operation_type": "processing"
    },
    {
      "operation_id": "measure_absorbance",
      "operation_name": "Measure Absorbance at 450nm",
      "device_id": "detector",
      "timing": {
        "type": "triangular",
        "min": 5.0,
        "mode": 6.0,
        "max": 8.0
      },
      "operation_type": "processing"
    },
    {
      "operation_id": "cool_and_store",
      "operation_name": "Cool to 4°C and Store",
      "device_id": "cooling_station",
      "timing": {
        "type": "fixed",
        "value": 120.0
      },
      "operation_type": "teardown"
    }
  ],
  
  "base_sequence": [
    {
      "sequence_id": 1,
      "operation_id": "transfer_to_reaction_vessel",
      "predecessors": []
    },
    {
      "sequence_id": 2,
      "operation_id": "add_antibody",
      "predecessors": ["transfer_to_reaction_vessel"]
    },
    {
      "sequence_id": 3,
      "operation_id": "incubate_antibody",
      "predecessors": ["add_antibody"]
    },
    {
      "sequence_id": 4,
      "operation_id": "add_secondary_antibody",
      "predecessors": ["incubate_antibody"]
    },
    {
      "sequence_id": 5,
      "operation_id": "incubate_secondary",
      "predecessors": ["add_secondary_antibody"]
    },
    {
      "sequence_id": 6,
      "operation_id": "wash",
      "predecessors": ["incubate_secondary"]
    },
    {
      "sequence_id": 7,
      "operation_id": "add_substrate",
      "predecessors": ["wash"]
    },
    {
      "sequence_id": 8,
      "operation_id": "incubate_substrate",
      "predecessors": ["add_substrate"]
    },
    {
      "sequence_id": 9,
      "operation_id": "measure_absorbance",
      "predecessors": ["incubate_substrate"]
    },
    {
      "sequence_id": 10,
      "operation_id": "cool_and_store",
      "predecessors": ["measure_absorbance"]
    }
  ]
}
```

**Expected Simulation Output (2 Samples):**
- Total simulation time: Highly variable due to exponential incubation times (mean ~420 sec)
- Samples completed: 2
- Prep station: Sequential bottleneck; ~100 sec per sample × 2 = bottleneck
- Heating block: Capacity 2, so both samples can incubate in parallel where possible
- Detector: Single capacity, sequential measurement
- Cooling station: Capacity 2, parallel cooling
- Bottleneck: Prep station (capacity 1) or detector (capacity 1)
- Run-to-run variability: High due to exponential substrate incubation time

---

## Example Scenarios

### Scenario 1: Single Sample (with Example 1 workflow)

```json
{
  "scenario_id": "pcr-single-sample-run1",
  "scenario_name": "PCR Single Sample - Run 1",
  "workflow_id": "single-sample-pcr-minimal",
  "sample_entry_pattern": {
    "pattern_type": "single",
    "num_samples": 1
  },
  "simulation_config": {
    "random_seed": 42,
    "max_simulation_time": 7200.0
  }
}
```

### Scenario 2: Synchronized Batch (with Example 2 workflow)

```json
{
  "scenario_id": "analyzer-batch-3samples",
  "scenario_name": "Chemistry Analyzer - 3 Sample Batch",
  "workflow_id": "synchronized-batch-analyzer",
  "sample_entry_pattern": {
    "pattern_type": "synchronized",
    "num_samples": 3
  },
  "simulation_config": {
    "random_seed": 123,
    "max_simulation_time": 1800.0
  }
}
```

### Scenario 3: Larger Synchronized Batch

```json
{
  "scenario_id": "analyzer-batch-10samples",
  "scenario_name": "Chemistry Analyzer - 10 Sample Batch",
  "workflow_id": "synchronized-batch-analyzer",
  "sample_entry_pattern": {
    "pattern_type": "synchronized",
    "num_samples": 10
  },
  "simulation_config": {
    "random_seed": 456,
    "max_simulation_time": 3600.0
  }
}
```

### Scenario 4: Multi-Device with Exponential Variability

```json
{
  "scenario_id": "immunoassay-2samples-trial1",
  "scenario_name": "Immunoassay - 2 Samples, Trial 1",
  "workflow_id": "multi-device-immunoassay",
  "sample_entry_pattern": {
    "pattern_type": "synchronized",
    "num_samples": 2
  },
  "simulation_config": {
    "random_seed": 789,
    "max_simulation_time": 7200.0
  }
}
```

---

## Test Case Mapping

| Example | Test Case | Expected Behavior |
|---------|-----------|-------------------|
| Example 1 + Scenario 1 | test_single_sample_fixed_timing | Deterministic output; total time ≈ 3613 sec |
| Example 2 + Scenario 2 | test_synchronized_batch_contention | All samples complete; queue delays visible in logs |
| Example 2 + Scenario 3 | test_device_capacity_utilization | Analyzer (capacity 2) queues samples; bottleneck identified |
| Example 3 + Scenario 4 | test_exponential_distribution_variability | Run twice with same seed yields identical results |

