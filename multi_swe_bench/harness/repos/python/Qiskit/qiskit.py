import json
import re
from typing import Optional, Dict, List

from multi_swe_bench.harness.image import Config, Image, SWEImageDefault, File
from multi_swe_bench.harness.instance import Instance, TestResult
from multi_swe_bench.harness.pull_request import PullRequest
from multi_swe_bench.harness.test_result import TestStatus, mapping_to_testresult


# Static PR→tests mapping (generated from /home/sunyang.46135/MSB_for_QSKIT/multi-swe-bench/pr_tests.json)
QISKIT_PR_TESTS: Dict[str, List[str]] = {
    "15156": ["test/python/transpiler/test_basis_translator.py"],
    "15150": ["test/python/transpiler/test_basis_translator.py"],
    "15143": ["test/python/transpiler/test_basis_translator.py"],
    "15141": ["test/python/transpiler/test_optimize_1q_decomposition.py"],
    "15140": ["test/python/transpiler/test_optimize_1q_decomposition.py"],
    "15137": ["test/python/compiler/test_transpiler.py"],
    "15131": ["test/python/transpiler/test_optimize_1q_decomposition.py"],
    "15119": [],
    "15117": [],
    "15076": ["test/python/transpiler/test_sabre_swap.py"],
    "15074": ["test/python/transpiler/test_sabre_swap.py"],
    "15057": [
        "test/python/converters/test_circuit_to_dag.py",
        "test/python/dagcircuit/test_dagcircuit.py",
        "test/python/transpiler/test_barrier_before_final_measurements.py",
    ],
    "15040": [
        "test/python/converters/test_circuit_to_dag.py",
        "test/python/dagcircuit/test_dagcircuit.py",
        "test/python/transpiler/test_barrier_before_final_measurements.py",
    ],
    "15029": ["test/python/quantum_info/operators/symplectic/test_sparse_pauli_op.py"],
    "15025": ["test/python/transpiler/test_preset_passmanagers.py"],
    "15024": ["test/python/transpiler/test_preset_passmanagers.py"],
    "15023": ["test/python/circuit/test_compose.py"],
    "15020": ["test/python/circuit/test_compose.py"],
    "15001": ["test/python/transpiler/test_vf2_post_layout.py"],
    "14998": ["test/python/transpiler/test_vf2_post_layout.py"],
    "14984": [],
    "14978": ["test/python/transpiler/test_commutative_inverse_cancellation.py"],
    "14961": ["test/python/transpiler/test_commutative_cancellation.py"],
    "14956": ["test/python/transpiler/test_commutative_cancellation.py"],
    "14941": ["test/python/transpiler/test_transpile_layout.py"],
    "14940": [
        "test/python/transpiler/test_vf2_layout.py",
        "test/python/transpiler/test_vf2_post_layout.py",
    ],
    "14939": ["test/python/transpiler/test_transpile_layout.py"],
    "14938": [
        "test/python/transpiler/test_vf2_layout.py",
        "test/python/transpiler/test_vf2_post_layout.py",
    ],
    "14934": [
        "test/python/circuit/library/test_evolution_gate.py",
        "test/python/transpiler/test_high_level_synthesis.py",
    ],
    "14920": ["test/python/compiler/test_transpiler.py"],
    "14919": ["test/python/compiler/test_transpiler.py"],
    "14918": ["test/python/circuit/test_control_flow.py"],
    "14905": [],
    "14897": ["test/python/qasm3/test_export.py"],
    "14896": ["test/python/qasm3/test_export.py"],
    "14895": ["test/python/qasm3/test_export.py"],
    "14882": ["test/python/transpiler/test_preset_passmanagers.py"],
    "14869": ["test/python/transpiler/test_preset_passmanagers.py"],
    "14821": ["test/python/transpiler/test_passmanager.py"],
    "14773": ["test/python/transpiler/test_target.py"],
    "14765": ["test/python/transpiler/test_target.py"],
    "14764": ["test/python/quantum_info/operators/symplectic/test_sparse_pauli_op.py"],
    "14763": ["test/python/transpiler/test_commutative_cancellation.py"],
    "14734": ["test/python/compiler/test_transpiler.py", "test/python/transpiler/test_vf2_layout.py"],
    "14730": ["test/python/compiler/test_transpiler.py", "test/python/transpiler/test_vf2_layout.py"],
    "14728": ["test/python/circuit/test_controlled_gate.py", "test/python/synthesis/test_multi_controlled_synthesis.py"],
    "14722": ["test/python/dagcircuit/test_dagcircuit.py"],
    "14716": ["test/python/dagcircuit/test_dagcircuit.py"],
    "14714": ["test/python/primitives/containers/test_observables_array.py"],
    "14692": ["test/python/transpiler/test_vf2_layout.py"],
    "14676": ["test/python/quantum_info/operators/symplectic/test_sparse_pauli_op.py"],
    "14671": ["test/python/transpiler/test_high_level_synthesis.py"],
    "14670": ["test/python/transpiler/test_high_level_synthesis.py"],
    "14667": ["test/python/transpiler/test_vf2_layout.py"],
    "14655": ["test/python/transpiler/test_commutative_inverse_cancellation.py"],
    "14642": ["test/python/circuit/test_parameter_expression.py"],
    "14641": ["test/python/circuit/test_parameter_expression.py"],
    "14636": ["test/python/circuit/library/test_phase_and_bitflip_oracles.py", "test/python/synthesis/test_boolean.py"],
    "14628": ["test/python/transpiler/test_high_level_synthesis.py"],
    "14625": ["test/python/transpiler/test_high_level_synthesis.py"],
    "14624": ["test/python/transpiler/test_high_level_synthesis.py"],
    "14623": ["test/python/transpiler/test_elide_permutations.py"],
    "14622": ["test/python/transpiler/test_elide_permutations.py"],
    "14621": ["test/python/transpiler/test_elide_permutations.py"],
    "14617": ["test/python/transpiler/test_sabre_layout.py"],
    "14616": ["test/python/transpiler/test_apply_layout.py"],
    "14615": ["test/python/transpiler/test_apply_layout.py"],
    "14613": ["test/python/transpiler/test_apply_layout.py"],
    "14606": ["test/python/transpiler/test_apply_layout.py"],
    "14488": ["test/python/transpiler/test_sabre_swap.py"],
    "14417": ["test/python/transpiler/test_consolidate_blocks.py"],
    "14363": ["test/python/circuit/library/test_iqp.py"],
    "14349": ["test/python/transpiler/test_high_level_synthesis.py"],
    "14345": [
        "test/python/transpiler/test_solovay_kitaev.py",
        "test/python/transpiler/test_unitary_synthesis.py",
    ],
    "14330": ["test/python/compiler/test_transpiler.py"],
    "14304": ["test/python/transpiler/test_solovay_kitaev.py"],
    "14217": ["test/python/transpiler/test_solovay_kitaev.py"],
}

# Extend with two new batches (excluding PRs with empty test lists)
QISKIT_PR_TESTS.update({
    # Batch 1
    "14494": ["test/python/transpiler/test_sabre_swap.py"],
    "14493": ["test/python/transpiler/test_sabre_swap.py"],
    "14425": ["test/python/quantum_info/operators/symplectic/test_sparse_pauli_op.py"],
    "14424": ["test/python/transpiler/test_consolidate_blocks.py"],
    "14406": [
        "test/python/compiler/test_transpiler.py",
        "test/python/transpiler/test_target.py",
        "test/python/transpiler/test_wrap_angles.py",
    ],
    "14405": ["test/python/transpiler/test_preset_passmanagers.py"],
    "14373": ["test/python/circuit/library/test_iqp.py"],
    "14358": ["test/python/transpiler/test_high_level_synthesis.py"],
    "14351": [
        "test/python/transpiler/test_solovay_kitaev.py",
        "test/python/transpiler/test_unitary_synthesis.py",
    ],
    "14331": ["test/python/compiler/test_transpiler.py"],
    "14324": ["test/python/visualization/test_circuit_text_drawer.py"],
    "14312": ["test/python/transpiler/test_solovay_kitaev.py"],
    "14311": ["test/python/transpiler/test_solovay_kitaev.py"],
    "14325": ["test/python/circuit/test_circuit_load_from_qpy.py"],
    "14295": ["test/python/transpiler/test_solovay_kitaev.py"],
    "14294": ["test/python/transpiler/test_solovay_kitaev.py"],
    "14282": ["test/python/visualization/test_circuit_text_drawer.py"],
    "14278": ["test/python/visualization/test_circuit_text_drawer.py"],
    "14190": ["test/python/transpiler/test_preset_passmanagers.py"],
    "14137": ["test/python/result/test_result.py"],
    "14118": ["test/python/circuit/test_circuit_load_from_qpy.py"],
    "14112": [
        "test/python/qasm2/test_structure.py",
        "test/python/transpiler/test_split_2q_unitaries.py",
    ],
    "14096": ["test/python/circuit/test_circuit_load_from_qpy.py"],
    "14093": [
        "test/python/circuit/test_circuit_qasm.py",
        "test/python/qasm2/test_export.py",
        "test/python/synthesis/test_multi_controlled_synthesis.py",
    ],
    "14092": ["test/python/transpiler/test_basis_translator.py"],
    "14091": ["test/python/transpiler/test_basis_translator.py"],
    # Batch 2
    "13780": ["test/python/visualization/test_circuit_text_drawer.py"],
    "13785": ["test/python/transpiler/test_remove_identity_equivalent.py"],
    "13789": ["test/python/visualization/test_circuit_text_drawer.py"],
    "13790": ["test/python/transpiler/test_sabre_swap.py"],
    "13803": ["test/python/quantum_info/test_sparse_observable.py"],
    "13804": [
        "test/python/circuit/test_commutation_checker.py",
        "test/python/transpiler/test_commutative_inverse_cancellation.py",
    ],
    "13825": ["test/python/transpiler/test_remove_identity_equivalent.py"],
    "13833": ["test/python/transpiler/test_sabre_layout.py"],
    "13835": ["test/python/transpiler/test_sabre_layout.py"],
    "13843": ["test/python/circuit/test_scheduled_circuit.py"],
    "13847": [
        "test/python/quantum_info/operators/symplectic/test_sparse_pauli_op.py",
        "test/python/quantum_info/test_sparse_observable.py",
    ],
    "13888": ["test/python/circuit/test_scheduled_circuit.py"],
    "13890": [
        "test/python/qpy/test_serialize_value_objects.py",
        "test/qpy_compat/test_qpy.py",
    ],
    "13920": [
        "test/python/compiler/test_transpiler.py",
        "test/python/transpiler/test_preset_passmanagers.py",
    ],
    "13921": ["test/python/converters/test_circuit_to_instruction.py"],
    "13936": ["test/python/circuit/test_circuit_operations.py"],
})

# New batch (exclude empty test lists)
QISKIT_PR_TESTS.update({
    "13496": ["test/python/transpiler/test_inverse_cancellation.py"],
    "13482": [
        "test/python/circuit/library/test_nlocal.py",
        "test/python/circuit/test_parameters.py",
    ],
    "13454": ["test/python/transpiler/test_inverse_cancellation.py"],
    "13441": ["test/python/transpiler/test_high_level_synthesis.py"],
    "13417": ["test/python/transpiler/test_high_level_synthesis.py"],
    "13440": [],
    "13439": [],
    "13436": ["test/python/quantum_info/states/test_statevector.py"],
    "13385": [],
    "13358": [
        "test/python/quantum_info/operators/channel/test_kraus.py",
        "test/python/quantum_info/operators/channel/test_stinespring.py",
        "test/python/quantum_info/operators/symplectic/test_sparse_pauli_op.py",
        "test/python/quantum_info/operators/test_operator.py",
    ],
    "13345": ["test/python/quantum_info/states/test_statevector.py"],
    "13340": ["test/python/qasm2/test_structure.py"],
    "13337": [],
    "13319": ["test/python/quantum_info/operators/test_operator.py"],
    "13311": ["test/python/transpiler/test_decompose.py"],
    "13259": [
        "test/qpy_compat/get_versions.py",
        "test/qpy_compat/run_tests.sh",
    ],
    "13251": [],
    "13186": ["test/python/transpiler/test_elide_permutations.py"],
    "13184": ["test/python/compiler/test_transpiler.py"],
    "13181": ["test/python/transpiler/test_high_level_synthesis.py"],
    "13148": ["test/python/qasm3/test_export.py"],
    "13133": [],
    "13121": ["test/python/circuit/test_rust_equivalence.py"],
    "13114": ["test/python/transpiler/test_sabre_layout.py"],
    "13095": ["test/python/transpiler/test_split_2q_unitaries.py"],
    "13086": ["test/python/quantum_info/operators/symplectic/test_clifford.py"],
    "13083": ["test/python/transpiler/test_hoare_opt.py"],
    "13070": [],
    "13067": ["test/python/circuit/test_rust_equivalence.py"],
    "13015": ["test/python/transpiler/test_split_2q_unitaries.py"],
    "13014": ["test/python/synthesis/test_synthesis.py"],
    "12986": [
        "test/python/circuit/library/test_linear_function.py",
        "test/python/circuit/library/test_permutation.py",
        "test/python/circuit/test_diagonal_gate.py",
        "test/python/circuit/test_gate_definitions.py",
        "test/python/circuit/test_hamiltonian_gate.py",
        "test/python/circuit/test_initializer.py",
        "test/python/circuit/test_isometry.py",
        "test/python/circuit/test_uc.py",
        "test/python/circuit/test_unitary.py",
    ],
    "12980": ["test/python/transpiler/test_preset_passmanagers.py"],
    "12979": [],
    "12976": ["test/python/circuit/test_initializer.py"],
    "12952": ["test/python/transpiler/test_dynamical_decoupling.py"],
    "12945": ["test/python/qasm3/test_export.py"],
    "12898": [
        "test/python/compiler/test_transpiler.py",
        "test/python/transpiler/test_consolidate_blocks.py",
    ],
    "12884": ["test/python/quantum_info/operators/symplectic/test_sparse_pauli_op.py"],
    "12848": ["test/python/visualization/test_dag_drawer.py"],
    "12842": ["test/python/primitives/test_statevector_sampler.py"],
    "12820": ["test/python/primitives/containers/test_bit_array.py"],
    "12800": ["test/python/primitives/containers/test_bit_array.py"],
    "12774": ["test/python/qasm2/test_structure.py"],
    "12755": ["test/python/primitives/containers/test_bit_array.py"],
    "12752": [
        "test/python/circuit/test_annotated_operation.py",
        "test/python/circuit/test_controlled_gate.py",
    ],
    "12686": ["test/python/primitives/containers/test_bit_array.py"],
    "12511": ["test/python/transpiler/test_basis_translator.py"],

    "12396": ["test/python/circuit/test_compose.py"],
    "12392": [],
    "12385": [
        "test/python/quantum_info/operators/symplectic/test_pauli.py",
        "test/python/quantum_info/operators/symplectic/test_sparse_pauli_op.py",
    ],
    "12375": [
        "test/python/quantum_info/operators/symplectic/test_pauli.py",
        "test/python/quantum_info/operators/symplectic/test_sparse_pauli_op.py",
    ],
    "12369": [],
    "12291": [
        "test/python/primitives/test_backend_estimator_v2.py",
        "test/python/primitives/test_backend_sampler_v2.py",
    ],
    "12183": [],
    "12170": ["test/python/transpiler/test_stage_plugin.py"],
    "12140": ["test/python/qasm2/test_expression.py"],
    "12137": ["test/python/transpiler/test_swap_strategy_router.py"],
    "12098": [
        "test/python/circuit/test_compose.py",
        "test/python/circuit/test_parameters.py",
    ],
    "12095": [
        "test/python/quantum_info/operators/symplectic/test_pauli.py",
        "test/python/quantum_info/operators/symplectic/test_pauli_list.py",
    ],
    "12061": ["test/python/circuit/test_commutation_checker.py"],
    "12057": ["test/python/quantum_info/operators/test_operator.py"],
    "12042": ["test/python/compiler/test_transpiler.py"],
    "12029": ["test/python/pulse/test_builder.py"],
    "12016": [
        "test/visual/mpl/circuit/test_circuit_matplotlib_drawer.py",
    ],
    # Added older PRs requested by user
    "1011": [
        "test/python/aer/test_extensions_simulator.py",
        "test/python/test_circuit.py",
        "test/python/test_compiler.py",
    ],
    "1013": [
        "test/python/common.py",
        "test/python/ibmq/test_ibmq_qobj.py",
        "test/python/ibmq/test_ibmqjob.py",
    ],
    "1014": [
        "test/python/ibmq/test_registration.py",
    ],
    "1017": [
        "test/python/ibmq/test_ibmq_qasm_simulator.py",
    ],
    "1028": [
        "test/python/test_compiler.py",
    ],
    "1200": [
        "test/python/test_circuit_text_drawer.py",
        "test/python/test_visualization_output.py",
    ],
    "1214": [
        "test/python/test_util.py",
    ],
})


# Ensure mapping type is compatible across Python versions
QISKIT_PR_TESTS: Dict[str, List[str]] = QISKIT_PR_TESTS  # type: ignore

# Append additional PR→tests provided by user (new batch)
QISKIT_PR_TESTS.update({
  '1028': ['test/python/test_compiler.py'],
  '1200': ['test/python/test_circuit_text_drawer.py', 'test/python/test_visualization_output.py'],
  '1214': ['test/python/test_util.py'],
  '1011': [
    'test/python/aer/test_extensions_simulator.py',
    'test/python/test_circuit.py',
    'test/python/test_compiler.py'
  ],
  '1013': [
    'test/python/common.py',
    'test/python/ibmq/test_ibmq_qobj.py',
    'test/python/ibmq/test_ibmqjob.py'
  ],
  '1014': [
    'test/python/ibmq/test_registration.py'
  ],
  '1017': [
    'test/python/ibmq/test_ibmq_qasm_simulator.py'
  ],
  '1043': ['test/python/test_dagcircuit.py'],
  '1054': [
    'test/python/references/text_ref.txt',
    'test/python/test_circuit_text_drawer.py',
    'test/python/test_visualization_output.py'
  ],
  '1059': ['test/python/test_dagcircuit.py'],
  '1084': ['test/python/test_parallel.py', 'test/python/test_qi.py'],
  '1086': ['test/python/transpiler/test_pass_scheduler.py'],
  '1107': [
    'test/python/common.py',
    'test/python/ibmq/test_ibmq_qobj.py',
    'test/python/ibmq/test_ibmqjob.py'
  ],
  '1115': ['test/python/test_circuit_text_drawer.py'],
  '1117': [
    'test/python/notebooks/test_jupyter.ipynb',
    'test/python/test_parallel.py',
    'test/python/test_pubsub.py'
  ],
  '1121': ['test/python/test_backends.py'],
  '1141': [
    'test/python/test_layout.py',
    'test/python/test_mapper_coupling.py',
    'test/python/test_transpiler.py'
  ],
  '1154': [
    'test/python/notebooks/test_jupyter.ipynb',
    'test/python/test_notebooks.py'
  ],
  '1166': ['test/python/test_pauli.py', 'test/python/test_qi.py'],
  '1172': ['test/python/test_circuit.py'],
  '1174': ['test/python/ibmq/test_ibmqjob.py'],
  '1178': ['test/python/test_circuit_text_drawer.py'],
  '1181': [
    'test/python/test_circuit_text_drawer.py',
    'test/python/test_visualization_output.py'
  ],
  '1184': ['test/python/test_apps.py'],
  '1185': ['test/python/test_result.py'],
  '1187': ['test/python/test_dagcircuit.py', 'test/python/test_visualization.py'],
  '1189': ['test/python/test_dagcircuit.py'],
  '1198': [
    'test/python/ibmq/test_ibmq_connector.py',
    'test/python/ibmq/test_ibmqjob_states.py',
    'test/python/test_util.py'
  ],
  '1199': [
    'test/python/test_circuit_text_drawer.py',
    'test/python/test_visualization_output.py'
  ],
  '1204': ['test/python/aer/test_aerjob.py'],
  '1205': ['test/python/test_wrapper.py'],
  '1208': [
    'test/python/circuit/__init__.py',
    'test/python/circuit/test_circuit_from_qasm.py',
    'test/python/test_circuit.py',
    'test/python/test_circuit_text_drawer.py'
  ],
  '1209': [
    'test/python/circuit/test_circuit_from_qasm.py',
    'test/python/test_circuit.py'
  ],
  '1216': ['test/python/test_notebooks.py'],
  '1217': ['test/python/notebooks/test_jupyter.ipynb', 'test/python/test_notebooks.py'],
  '1232': ['test/python/ibmq/test_ibmq_connector.py'],
  '1249': ['test/python/test_validation.py']
})


# Append PR→tests provided by user (batch: 11864..11972)
QISKIT_PR_TESTS.update({
  '11864': ['test/python/passmanager/test_passmanager.py'],
  '11868': ['test/python/primitives/containers/test_observables_array.py'],
  '11871': ['test/python/primitives/containers/test_estimator_pub.py'],
  '11874': ['test/visual/mpl/circuit/test_circuit_matplotlib_drawer.py'],
  '11876': ['test/python/primitives/containers/test_observables_array.py'],
  '11913': ['test/python/primitives/containers/test_sampler_pub.py'],
  '11914': ['test/visual/mpl/circuit/test_circuit_matplotlib_drawer.py'],
  '11920': ['test/python/primitives/containers/test_sampler_pub.py'],
  '11940': ['test/python/circuit/test_instruction_repeat.py'],
  '11972': ['test/python/pulse/test_parameter_manager.py'],
  # '12016': ['test/visual/mpl/circuit/test_circuit_matplotlib_drawer.py'],  # already present above
})


# Append PR→tests (batch: 11730, 11731, 11750, 11812, 11787, 11800)
QISKIT_PR_TESTS.update({
    '11730': ['test/python/qpy/test_circuit_load_from_qpy.py'],
    '11731': ['test/python/qpy/test_circuit_load_from_qpy.py'],  # backport of #11730
    '11750': ['test/python/visualization/test_circuit_drawer.py'],
    '11812': ['test/python/visualization/test_circuit_drawer.py'],  # backport of #11750
    '11787': ['test/python/passmanager/test_passmanager.py'],
    '11800': ['test/python/primitives/containers/test_bindings_array.py'],
})


# Append PR→tests (batch: 11995..11041)
QISKIT_PR_TESTS.update({
    '11995': ['test/python/circuit/test_scheduled_circuit.py'],
    '11993': ['test/python/circuit/test_controlled_gate.py'],
    '11972': ['test/python/pulse/test_parameter_manager.py'],
    '11959': ['test/python/circuit/test_equivalence.py'],
    '11940': ['test/python/circuit/test_instruction_repeat.py'],
    '11907': ['test/python/compiler/test_transpiler.py'],
    '11884': ['test/python/providers/test_fake_backends.py'],  # backport of #11877
    '11883': ['test/python/providers/test_fake_backends.py'],  # backport of #11877
    '11877': ['test/python/providers/test_fake_backends.py'],
    '11829': ['test/python/compiler/test_assembler.py'],
    '11811': ['test/python/transpiler/test_optimize_annotated.py'],
    '11787': ['test/python/passmanager/test_passmanager.py'],
    '11782': ['test/python/circuit/test_scheduled_circuit.py'],
    '11682': ['test/python/circuit/library/test_evolved_op_ansatz.py'],
    '11669': ['test/python/circuit/test_circuit_operations.py'],
    '11655': ['test/python/compiler/test_transpiler.py'],
    '11652': ['test/python/circuit/test_parameters.py'],
    '11651': ['test/python/circuit/test_circuit_load_from_qpy.py', 'test/qpy_compat/test_qpy.py'],
    '11646': ['test/python/qasm2/test_structure.py', 'test/python/circuit/test_circuit_load_from_qpy.py'],
    '11641': ['test/python/circuit/test_parameters.py'],
    '11608': ['test/python/primitives/containers/test_bindings_array.py', 'test/python/primitives/containers/test_observables_array.py'],
    '11466': ['test/python/visualization/test_circuit_text_drawer.py'],
    '11455': ['test/python/circuit/test_circuit_operations.py'],
    '11451': ['test/python/circuit/test_compose.py'],
    '11447': ['test/python/circuit/test_delay.py'],
    '11367': ['test/python/transpiler/test_stage_plugin.py'],
    '11351': ['test/python/transpiler/test_optimize_1q_decomposition.py'],
    '11333': ['test/python/providers/test_fake_backends.py'],
    '11272': ['test/python/circuit/test_circuit_operations.py'],
    '11247': ['test/python/circuit/test_hamiltonian_gate.py'],
    '11206': ['test/python/circuit/test_circuit_load_from_qpy.py'],
    '11181': ['test/python/circuit/library/test_blueprintcircuit.py'],
    '11175': ['test/python/qasm2/test_structure.py'],
    '11097': ['test/python/circuit/test_scheduled_circuit.py'],
    '11096': ['test/visual/mpl/circuit/test_circuit_matplotlib_drawer.py'],
    '11041': ['test/python/quantum_info/operators/symplectic/test_sparse_pauli_op.py'],
})


class ImageDefault(Image):
    def __init__(self, pr: PullRequest, config: Config):
        self._pr = pr
        self._config = config
        # Build summary from static mapping and print all PR→tests pairs as JSON
        self._pr_summary = {k: {"test_directory": v} for k, v in QISKIT_PR_TESTS.items()}
        try:
            print(json.dumps(QISKIT_PR_TESTS, ensure_ascii=False))
        except Exception:
            # Fallback simple print
            print(QISKIT_PR_TESTS)

    @property
    def pr(self) -> PullRequest:
        return self._pr

    @property
    def config(self) -> Config:
        return self._config

    def dependency(self) -> str:
        return "python:3.10"

    def image_prefix(self) -> str:
        return "envagent"

    def image_tag(self) -> str:
        return f"pr-{self.pr.number}"

    def workdir(self) -> str:
        return f"pr-{self.pr.number}"

    def files(self):
        # Use PR-to-test mapping; default to Qiskit's main test dir if missing.
        test_dirs = self._pr_summary.get(str(self.pr.number), {}).get(
            "test_directory", []
        )
        if not test_dirs:
            test_dirs = ["test/python"]

        pytest_file_cmd = " ".join(test_dirs)
        print(f"Test directories for PR #{self.pr.number}: {test_dirs}")

        return [
            File(
                ".",
                "fix.patch",
                f"{self.pr.fix_patch}",
            ),
            File(
                ".",
                "test.patch",
                f"{self.pr.test_patch}",
            ),
            File(
                ".",
                "check_git_changes.sh",
                """#!/bin/bash
set -e

if ! git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
  echo "check_git_changes: Not inside a git repository"
  exit 1
fi

if [[ -n $(git status --porcelain) ]]; then
  echo "check_git_changes: Uncommitted changes"
  exit 1
fi

echo "check_git_changes: No uncommitted changes"
exit 0

""".format(),
            ),
            File(
                ".",
                "prepare.sh",
                """#!/bin/bash
set -e

cd /home/{pr.repo}
git reset --hard
bash /home/check_git_changes.sh
git checkout {pr.base.sha}
# pip install -e . --no-build-isolation
bash /home/check_git_changes.sh

""".format(pr=self.pr),
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}


# 让 Python 能自动加载 /home/qiskit/sitecustomize.py
export PYTHONPATH=/home/qiskit

# 写入 sitecustomize.py（用 heredoc，避免转义地狱）
cat > /home/qiskit/sitecustomize.py <<'PY'
import unittest, logging
if not hasattr(unittest.case, '_AssertLogsContext'):
    class _AssertLogsContextPatch:
        def __init__(self, logger=None, level=None):
            self._tc = unittest.TestCase('__init__')
            self.logger, self.level, self._ctx = logger, level, None
        def __enter__(self):
            self._ctx = self._tc.assertLogs(self.logger, level=self.level)
            return self._ctx.__enter__()
        def __exit__(self, exc_type, exc, tb):
            return self._ctx.__exit__(exc_type, exc, tb)
    unittest.case._AssertLogsContext = _AssertLogsContextPatch

try:
    import numpy as np
    if not hasattr(np, 'float'):
        np.float = float
except Exception:
    pass
PY



# 可编辑安装
pip install -e . --no-build-isolation

# 运行测试
python -m pytest {pytest_file} --no-header -rA --tb=no -p no:cacheprovider
""".format(pr=self.pr, pytest_file=pytest_file_cmd),
            ),
            File(
                ".",
                "test-run.sh",
                """#!/bin/bash
cd /home/{pr.repo}

if ! git -C /home/{pr.repo} apply --whitespace=nowarn /home/test.patch; then
    echo "Error: git apply failed" >&2
    exit 1  
fi



# 让 Python 能自动加载 /home/qiskit/sitecustomize.py
export PYTHONPATH=/home/qiskit

# 写入 sitecustomize.py（用 heredoc，避免转义地狱）
cat > /home/qiskit/sitecustomize.py <<'PY'
import unittest, logging
if not hasattr(unittest.case, '_AssertLogsContext'):
    class _AssertLogsContextPatch:
        def __init__(self, logger=None, level=None):
            self._tc = unittest.TestCase('__init__')
            self.logger, self.level, self._ctx = logger, level, None
        def __enter__(self):
            self._ctx = self._tc.assertLogs(self.logger, level=self.level)
            return self._ctx.__enter__()
        def __exit__(self, exc_type, exc, tb):
            return self._ctx.__exit__(exc_type, exc, tb)
    unittest.case._AssertLogsContext = _AssertLogsContextPatch

try:
    import numpy as np
    if not hasattr(np, 'float'):
        np.float = float
except Exception:
    pass
PY


pip install -e . --no-build-isolation

python -m pytest {pytest_file} --no-header -rA --tb=no -p no:cacheprovider
""".format(pr=self.pr, pytest_file=pytest_file_cmd),
            ),
            File(
                ".",
                "fix-run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
if ! git -C /home/{pr.repo} apply --whitespace=nowarn  /home/test.patch /home/fix.patch; then
    echo "Error: git apply failed" >&2
    exit 1  
fi


# 让 Python 能自动加载 /home/qiskit/sitecustomize.py
export PYTHONPATH=/home/qiskit

# 写入 sitecustomize.py（用 heredoc，避免转义地狱）
cat > /home/qiskit/sitecustomize.py <<'PY'
import unittest, logging
if not hasattr(unittest.case, '_AssertLogsContext'):
    class _AssertLogsContextPatch:
        def __init__(self, logger=None, level=None):
            self._tc = unittest.TestCase('__init__')
            self.logger, self.level, self._ctx = logger, level, None
        def __enter__(self):
            self._ctx = self._tc.assertLogs(self.logger, level=self.level)
            return self._ctx.__enter__()
        def __exit__(self, exc_type, exc, tb):
            return self._ctx.__exit__(exc_type, exc, tb)
    unittest.case._AssertLogsContext = _AssertLogsContextPatch

try:
    import numpy as np
    if not hasattr(np, 'float'):
        np.float = float
except Exception:
    pass
PY


pip install -e . --no-build-isolation

python -m pytest {pytest_file} --no-header -rA --tb=no -p no:cacheprovider

""".format(pr=self.pr, pytest_file=pytest_file_cmd),
            ),
        ]

    def dockerfile(self) -> str:

        image_name = self.dependency()
        if isinstance(image_name, Image):
            image_name = image_name.image_full_name()
        
        if self.config.need_clone:
            code = f"RUN git clone https://github.com/{self.pr.org}/{self.pr.repo}.git /home/{self.pr.repo}"
        else:
            code = f"COPY {self.pr.repo} /home/{self.pr.repo}"

        template = """
FROM {image_name}

{global_env}

WORKDIR /home/

# Install system dependencies and Rust
RUN apt-get update && \\
    apt-get install -y curl build-essential && \\
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y && \\
    apt-get clean && rm -rf /var/lib/apt/lists/*

ENV PATH="/root/.cargo/bin:${{PATH}}"

# Install Qiskit in editable mode
RUN pip install --upgrade pip
RUN pip install "setuptools>=77.0" setuptools-rust pytest pytest-xdist hypothesis ddt pillow matplotlib

{code}

"""

        
        file_text = template.format(
            image_name=image_name,
            global_env=self.global_env,
            code=code,
        )



        copy_commands = """"""

        for file in self.files():
            copy_commands += f"COPY {file.name} /home/\n"

        file_text += copy_commands

        file_text += "RUN bash /home/prepare.sh\n"

        return file_text



@Instance.register("Qiskit", "qiskit")
class Qiskit(Instance):
    def __init__(self, pr: PullRequest, config: Config, *args, **kwargs):
        super().__init__()
        self._pr = pr
        self._config = config

    @property
    def pr(self) -> PullRequest:
        return self._pr

    def dependency(self) -> Optional[Image]:        
        return ImageDefault(self.pr, self._config)

    def run(self, run_cmd: str = "") -> str:
        if run_cmd:
            return run_cmd

        return "bash /home/run.sh"

    def test_patch_run(self, test_patch_run_cmd: str = "") -> str:
        if test_patch_run_cmd:
            return test_patch_run_cmd

        return "bash /home/test-run.sh"

    def fix_patch_run(self, fix_patch_run_cmd: str = "") -> str:
        if fix_patch_run_cmd:
            return fix_patch_run_cmd

        return "bash /home/fix-run.sh"

    def parse_log(self, log: str) -> TestResult:
        test_status_map = {}
        escapes = "".join([chr(char) for char in range(1, 32)])
        for line in log.split("\n"):
            line = re.sub(r"\[(\d+)m", "", line)
            translator = str.maketrans("", "", escapes)
            line = line.translate(translator)
            if any([line.startswith(x.value) for x in TestStatus]):
                if line.startswith(TestStatus.FAILED.value):
                    line = line.replace(" - ", " ")
                test_case = line.split()
                if len(test_case) >= 2:
                    test_status_map[test_case[1]] = test_case[0]
            # Support older pytest versions by checking if the line ends with the test status
            elif any([line.endswith(x.value) for x in TestStatus]):
                test_case = line.split()
                if len(test_case) >= 2:
                    test_status_map[test_case[0]] = test_case[1]

        return mapping_to_testresult(test_status_map)

# Append PR→tests (batches 1, 2, 3, 5, 7)
QISKIT_PR_TESTS.update({
    # 第一批
    '10904': ['test/python/quantum_info/operators/symplectic/test_clifford.py'],
    '10850': ['test/python/quantum_info/test_synthesis.py'],
    '10495': ['test/python/circuit/test_commutation_checker.py'],
    '10493': ['test/python/compiler/test_transpiler.py', 'test/python/transpiler/test_apply_layout.py'],
    '10537': ['test/python/circuit/test_circuit_load_from_qpy.py'],
    '10376': ['test/python/circuit/test_circuit_load_from_qpy.py'],
    '10090': ['test/python/transpiler/test_unitary_synthesis.py'],

    # 第二批
    '10859': ['test/python/transpiler/test_preset_passmanagers.py'],
    '10825': ['test/python/transpiler/test_gate_direction.py'],
    '10809': ['test/python/circuit/test_circuit_load_from_qpy.py'],
    '10633': ['test/python/transpiler/test_vf2_layout.py', 'test/python/transpiler/test_vf2_post_layout.py'],
    '10618': ['test/python/transpiler/test_commutative_cancellation.py'],
    '10602': ['test/visual/mpl/circuit/test_circuit_matplotlib_drawer.py'],
    '10476': ['test/python/pulse/test_channels.py'],
    '10126': ['test/python/quantum_info/test_synthesis.py'],
    '10031': ['test/python/quantum_info/states/test_statevector.py'],
    '10008': ['test/python/quantum_info/xx_decompose/test_decomposer.py', 'test/python/transpiler/test_unitary_synthesis.py'],
    '10007': ['test/python/compiler/test_transpiler.py', 'test/python/transpiler/legacy_scheduling/test_scheduling_pass.py', 'test/python/transpiler/test_dynamical_decoupling.py', 'test/python/transpiler/test_scheduling_padding_pass.py'],

    # 第三批
    '10849': ['test/python/quantum_info/operators/symplectic/test_pauli.py', 'test/python/quantum_info/operators/symplectic/test_pauli_list.py', 'test/python/quantum_info/operators/symplectic/test_pauli_table.py'],
    '10758': ['test/python/circuit/test_circuit_load_from_qpy.py'],
    '10786': ['test/python/compiler/test_transpiler.py', 'test/python/transpiler/test_gate_direction.py'],
    '10631': ['test/python/transpiler/test_dynamical_decoupling.py'],
    '10532': ['test/python/circuit/test_circuit_qasm.py'],
    '10521': ['test/python/circuit/test_circuit_operations.py'],
    '10469': ['test/python/circuit/test_circuit_qasm.py', 'test/python/qasm2/test_parse_errors.py'],
    '10411': ['test/python/circuit/test_bit.py'],
    '10395': ['test/python/transpiler/test_check_map.py'],
    '10279': ['test/python/algorithms/eigensolvers/test_vqd.py'],
    '10181': ['test/python/transpiler/test_passmanager_config.py'],
    '10164': ['test/python/circuit/test_compose.py'],
    '10163': ['test/python/quantum_info/states/test_densitymatrix.py'],
    '10153': ['test/python/compiler/test_transpiler.py'],
    '10000': ['test/python/compiler/test_transpiler.py', 'test/python/transpiler/test_sabre_layout.py'],

    # 第五批
    '10834': ['test/python/transpiler/test_dynamical_decoupling.py'],
    '10773': ['test/python/qasm2/test_structure.py'],
    '10591': ['test/python/compiler/test_transpiler.py'],
    '10438': ['test/python/circuit/test_circuit_qasm.py'],
    '10377': ['test/python/dagcircuit/test_compose.py'],
    '10320': ['test/python/circuit/test_controlled_gate.py', 'test/python/circuit/test_unitary.py', 'test/python/quantum_info/test_synthesis.py'],
    '10842': ['test/python/visualization/test_circuit_text_drawer.py', 'test/visual/mpl/circuit/test_circuit_matplotlib_drawer.py'],
    '10441': ['test/python/quantum_info/operators/symplectic/test_clifford.py'],

    # 第七批
    '10835': ['test/python/transpiler/test_transpile_layout.py'],
    '10466': ['test/python/compiler/test_transpiler.py', 'test/python/transpiler/test_apply_layout.py'],
    '10410': ['test/python/qpy/test_circuit_load_from_qpy.py', 'test/qpy_compat/test_qpy.py'],
    '10401': ['test/python/circuit/test_random_circuit.py'],
    '10300': ['test/python/compiler/test_transpiler.py'],
    '10034': ['test/python/providers/test_fake_backends.py'],
    '10016': ['test/python/providers/test_fake_backends.py'],
})

# Append PR→tests (第8批, 第9批, 第10批, 第11批, 后续一批)
QISKIT_PR_TESTS.update({
    # 第8批
    '10630': ['test/qpy_compat/test_qpy.py'],
    '10148': ['test/python/qpy/test_circuit_load_from_qpy.py', 'test/qpy_compat/test_qpy.py'],
    '10366': ['test/python/transpiler/test_preset_passmanagers.py', 'test/python/transpiler/test_sabre_swap.py'],
    '10355': ['test/python/transpiler/test_consolidate_blocks.py'],

    # 第9批
    '10869': ['test/python/visualization/test_circuit_text_drawer.py', 'test/visual/mpl/circuit/test_circuit_matplotlib_drawer.py'],

    # 第10批
    '10875': ['test/python/circuit/test_parameters.py'],
    '10820': ['test/python/circuit/test_circuit_load_from_qpy.py', 'test/python/qpy/test_block_load_from_qpy.py'],

    # 第11批
    '10825': ['test/python/transpiler/test_gate_direction.py'],

    # 后续一批（< 10825，偏物理）
    '10372': ['test/python/compiler/test_transpiler.py', 'test/python/transpiler/test_preset_passmanagers.py'],
    '10371': ['test/python/transpiler/test_preset_passmanagers.py'],
    '10362': ['test/python/converters/test_circuit_to_dag.py', 'test/python/dagcircuit/test_dagcircuit.py'],
    '10358': ['test/python/circuit/test_control_flow.py'],
    '10344': ['test/python/transpiler/test_setlayout.py'],
    '10271': ['test/python/quantum_info/operators/test_operator.py'],
    '10244': ['test/python/circuit/test_parameters.py'],
})

# Append PR→tests (new batch)
QISKIT_PR_TESTS.update({
    '9381': ['test/python/opflow/test_evolution.py'],
    '9353': ['test/python/quantum_info/test_sparse_z2_symmetries.py'],
    '9331': ['test/python/transpiler/aqc/test_aqc.py'],
    '9321': ['test/python/opflow/test_op_construction.py'],
    '9214': ['test/python/quantum_info/states/test_densitymatrix.py', 'test/python/quantum_info/states/test_statevector.py'],
    '9118': ['test/python/circuit/test_parameters.py'],
    '9101': ['test/python/algorithms/eigensolvers/test_numpy_eigensolver.py', 'test/python/algorithms/minimum_eigensolvers/test_numpy_minimum_eigensolver.py', 'test/python/quantum_info/operators/test_operator.py'],
    '9000': ['test/python/quantum_info/operators/symplectic/test_sparse_pauli_op.py'],
    '8900': ['test/python/quantum_info/states/test_densitymatrix.py', 'test/python/quantum_info/states/test_statevector.py'],
    '8877': ['test/python/quantum_info/operators/symplectic/test_pauli.py', 'test/python/quantum_info/operators/symplectic/test_pauli_list.py'],
})

# Append PR→tests (new batch: 8625, 8019, 8041, 7952, 8802, 8767, 7613, 8727, 8151)
QISKIT_PR_TESTS.update({
    '8625': ['test/python/transpiler/test_gate_direction.py'],
    '8019': ['test/python/providers/test_fake_backends.py'],
    '8041': ['test/python/transpiler/test_sabre_swap.py'],
    '7952': ['test/python/transpiler/test_sabre_swap.py'],
    '8802': [
        'test/python/quantum_info/operators/test_operator.py',
        'test/python/transpiler/test_bip_mapping.py',
        'test/python/transpiler/test_preset_passmanagers.py',
        'test/python/transpiler/test_sabre_layout.py',
        'test/python/visualization/test_circuit_text_drawer.py',
        'test/python/visualization/test_gate_map.py',
    ],
    '8767': [
        'test/python/transpiler/test_layout.py',
        'test/python/transpiler/test_vf2_layout.py',
    ],
    '7613': ['test/python/quantum_info/states/test_utils.py'],
    '8727': ['test/python/transpiler/test_sabre_swap.py'],
    '8151': ['test/python/pulse/test_pulse_lib.py'],
})

# Append PR→tests (new batch: 7xxx..3xxx)
QISKIT_PR_TESTS.update({
    '7551': ['test/python/circuit/library/test_evolution_gate.py'],
    '7460': ['test/python/quantum_info/states/test_stabilizerstate.py'],
    '5608': ['test/python/opflow/test_evolution.py'],
    '5925': ['test/python/circuit/test_instructions.py'],
    '5474': [
        'test/python/circuit/library/test_diagonal.py',
        'test/python/circuit/test_diagonal_gate.py',
        'test/python/quantum_info/test_synthesis.py',
        'test/randomized/test_synthesis.py',
    ],
    '6236': ['test/python/circuit/test_initializer.py'],
    '5248': [
        'test/python/circuit/test_controlled_gate.py',
        'test/python/circuit/test_unitary.py',
        'test/python/transpiler/test_decompose.py',
        'test/python/transpiler/test_unroller.py',
    ],
    '4915': [
        'test/python/basicaer/test_statevector_simulator.py',
        'test/python/circuit/test_controlled_gate.py',
        'test/python/circuit/test_extensions_standard.py',
        'test/python/transpiler/test_basis_translator.py',
        'test/python/transpiler/test_decompose.py',
        'test/python/transpiler/test_optimize_1q_gates.py',
    ],
    '4932': ['test/python/providers/test_backendconfiguration.py'],
    '4621': ['test/python/compiler/test_assembler.py'],
    '4465': [
        'test/python/quantum_info/states/test_statevector.py',
        'test/python/quantum_info/states/test_densitymatrix.py',
    ],
    '4444': ['test/python/circuit/test_controlled_gate.py'],
    '4335': ['test/python/pulse/test_schedule.py'],
    '4221': ['test/python/pulse/test_schedule.py'],
    '4156': ['test/python/transpiler/test_consolidate_blocks.py'],
    '5336': ['test/python/circuit/test_gate_definitions.py'],
    '4638': [
        'test/python/circuit/test_controlled_gate.py',
        'test/python/circuit/test_extensions_standard.py',
        'test/python/circuit/test_gate_definitions.py',
        'test/python/visualization/test_circuit_visualization_output.py',
    ],
    '5182': ['test/python/circuit/test_scheduled_circuit.py'],
    '4555': [
        'test/python/circuit/test_delay.py',
        'test/python/circuit/test_scheduled_circuit.py',
        'test/python/compiler/test_sequencer.py',
        'test/python/compiler/test_transpiler.py',
        'test/python/pulse/test_schedule.py',
        'test/python/transpiler/test_instruction_durations.py',
    ],
    '4940': ['test/python/pulse/test_instruction_schedule_map.py'],
    '4808': ['test/python/pulse/test_transforms.py'],
    '5229': ['test/python/circuit/test_initializer.py'],
    '3597': [
        'test/python/compiler/test_assembler.py',
        'test/python/qobj/test_pulse_converter.py',
    ],
    '3612': [
        'test/python/compiler/test_assembler.py',
        'test/python/providers/test_backendconfiguration.py',
    ],
    '3620': [
        'test/python/compiler/test_assembler.py',
        'test/python/pulse/test_commands.py',
        'test/python/pulse/test_discrete_pulses.py',
        'test/python/pulse/test_schedule.py',
        'test/python/qobj/test_pulse_converter.py',
        'test/python/scheduler/test_basic_scheduler.py',
        'test/python/visualization/test_pulse_visualization_output.py',
    ],
    '3694': ['test/python/compiler/test_assembler.py'],
    '3696': [
        'test/python/compiler/test_assembler.py',
        'test/python/qobj/test_pulse_converter.py',
    ],
    '3730': ['test/python/scheduler/test_utils.py'],
})

# Append PR→tests (new batch: 15216 and related older PRs)
QISKIT_PR_TESTS.update({
    '15216': ['test/python/transpiler/test_scheduling_padding_pass.py'],
    '15029': ['test/python/quantum_info/operators/symplectic/test_sparse_pauli_op.py'],
    '15020': ['test/python/circuit/test_compose.py'],
    '15001': ['test/python/transpiler/test_vf2_post_layout.py'],
    '14998': ['test/python/transpiler/test_vf2_post_layout.py'],
    '14941': ['test/python/transpiler/test_transpile_layout.py'],
    '14939': ['test/python/transpiler/test_transpile_layout.py'],
    '14882': ['test/python/transpiler/test_preset_passmanagers.py'],
    '14869': ['test/python/transpiler/test_preset_passmanagers.py'],
    '14603': ['test/python/transpiler/test_elide_permutations.py'],
    '14417': ['test/python/transpiler/test_consolidate_blocks.py'],
    '14345': ['test/python/transpiler/test_unitary_synthesis.py', 'test/python/transpiler/test_solovay_kitaev.py'],
    '14217': ['test/python/transpiler/test_solovay_kitaev.py'],
    '14078': ['test/python/transpiler/test_basis_translator.py'],
})

# Append PR→tests (new batch provided by user: 13816..13114)
QISKIT_PR_TESTS.update({
    '13816': ['test/python/circuit/test_delay.py'],
    '13825': ['test/python/transpiler/test_remove_identity_equivalent.py'],
    '13762': ['test/python/circuit/test_commutation_checker.py', 'test/python/transpiler/test_commutative_inverse_cancellation.py'],
    '13790': ['test/python/transpiler/test_sabre_swap.py'],
    '13833': ['test/python/transpiler/test_sabre_layout.py'],
    '13463': ['test/python/transpiler/test_consolidate_blocks.py'],
    '13345': ['test/python/quantum_info/states/test_statevector.py'],
    '13121': ['test/python/circuit/test_rust_equivalence.py'],
    '13114': ['test/python/transpiler/test_sabre_layout.py'],
})

# Append PR→tests (new batch provided by user)
QISKIT_PR_TESTS.update({
    '12988': ['test/python/circuit/library/test_state_preparation.py'],
    '12986': ['test/python/circuit/library/test_linear_function.py', 'test/python/circuit/library/test_permutation.py', 'test/python/circuit/test_diagonal_gate.py', 'test/python/circuit/test_gate_definitions.py', 'test/python/circuit/test_hamiltonian_gate.py', 'test/python/circuit/test_initializer.py', 'test/python/circuit/test_isometry.py', 'test/python/circuit/test_uc.py', 'test/python/circuit/test_unitary.py'],
    '12976': ['test/python/circuit/test_initializer.py'],
    '12884': ['test/python/quantum_info/operators/symplectic/test_sparse_pauli_op.py'],
    '12579': ['test/python/transpiler/test_solovay_kitaev.py'],
    '12511': ['test/python/transpiler/test_basis_translator.py'],
    '12029': ['test/python/pulse/test_builder.py'],
    '11972': ['test/python/pulse/test_parameter_manager.py'],
    '11940': ['test/python/circuit/test_instruction_repeat.py'],
    '11907': ['test/python/compiler/test_transpiler.py'],
    '11877': ['test/python/providers/test_fake_backends.py'],
    '11829': ['test/python/compiler/test_assembler.py'],
    '11782': ['test/python/circuit/test_scheduled_circuit.py'],
    '11682': ['test/python/circuit/library/test_evolved_op_ansatz.py'],
    '11655': ['test/python/compiler/test_transpiler.py'],
    '11455': ['test/python/circuit/test_circuit_operations.py'],
    '11447': ['test/python/circuit/test_delay.py'],
    '11351': ['test/python/transpiler/test_optimize_1q_decomposition.py'],
})

# Append PR→tests (new physical-correctness batch provided by user)
QISKIT_PR_TESTS.update({
    '11247': ['test/python/circuit/test_hamiltonian_gate.py'],
    '10631': ['test/python/transpiler/test_dynamical_decoupling.py'],
    '10630': ['test/qpy_compat/test_qpy.py'],
    '10591': ['test/python/compiler/test_transpiler.py'],
    '10126': ['test/python/quantum_info/test_synthesis.py'],
    '10090': ['test/python/transpiler/test_unitary_synthesis.py'],
    '9937': ['test/python/transpiler/test_unitary_synthesis.py'],
    '9843': ['test/python/transpiler/test_unitary_synthesis.py'],
    '9836': ['test/python/circuit/test_controlled_gate.py', 'test/qpy_compat/test_qpy.py'],
    '9635': ['test/python/transpiler/test_solovay_kitaev.py'],
    '9441': ['test/python/transpiler/test_solovay_kitaev.py'],
    '9388': ['test/python/opflow/test_evolution.py'],
    '9331': ['test/python/transpiler/aqc/test_aqc.py'],
    '9321': ['test/python/opflow/test_op_construction.py'],
    '10163': ['test/python/quantum_info/states/test_densitymatrix.py'],
    '9617': ['test/python/transpiler/test_unitary_synthesis.py'],
    '9538': ['test/python/algorithms/eigensolvers/test_vqd.py'],
    '9214': ['test/python/quantum_info/states/test_densitymatrix.py', 'test/python/quantum_info/states/test_statevector.py'],
    '10850': ['test/python/quantum_info/test_synthesis.py'],
})
