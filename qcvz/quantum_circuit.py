"""Minimal QuantumCircuit data structure extracted from qcs.common.

Only a subset of the original functionality is retained: enough to model
qubits, classical bits, and gate placement for visualization.
"""

from __future__ import annotations

from enum import Enum, auto
from typing import Dict, Iterable, List, Set


class GateType(Enum):
    CNOT = auto()
    CZ = auto()
    Tof = auto()
    HAD = auto()
    S = auto()
    T = auto()
    Tdg = auto()
    X = auto()
    Z = auto()
    CCZ = auto()
    MEASURE = auto()
    CONDITIONAL = auto()


class QuantumCircuit:
    """Simplified quantum circuit container."""

    def __init__(self):
        self.n_qubits: int = 0
        self.n_classical_bits: int = 0
        self.gates: List[Dict[str, object]] = []

    # ------------------------------------------------------------------
    # Allocation helpers
    def request_qubit(self) -> int:
        self.n_qubits += 1
        return self.n_qubits - 1

    def request_qubits(self, n: int) -> List[int]:
        return [self.request_qubit() for _ in range(n)]

    def request_classical_bit(self) -> int:
        self.n_classical_bits += 1
        return self.n_classical_bits - 1

    def request_classical_bits(self, n: int) -> List[int]:
        return [self.request_classical_bit() for _ in range(n)]

    # ------------------------------------------------------------------
    # Circuit composition
    def append(self, other: "QuantumCircuit") -> None:
        if not isinstance(other, QuantumCircuit):
            raise TypeError("Can only append another QuantumCircuit")

        classical_offset = self.n_classical_bits
        qubit_offset = self.n_qubits
        self.n_qubits = max(self.n_qubits, other.n_qubits + qubit_offset)
        self.n_classical_bits += other.n_classical_bits

        for gate in other.gates:
            adjusted = gate.copy()
            if gate["type"] is GateType.MEASURE:
                adjusted["classical_bit"] = int(adjusted["classical_bit"]) + classical_offset
                adjusted["qubit"] = int(adjusted["qubit"]) + qubit_offset
            elif gate["type"] is GateType.CONDITIONAL:
                adjusted["classical_bit"] = int(adjusted["classical_bit"]) + classical_offset
                adjusted["target"] = int(adjusted["target"]) + qubit_offset
                if "ctrl" in adjusted:
                    adjusted["ctrl"] = int(adjusted["ctrl"]) + qubit_offset
            elif gate["type"] in {GateType.CNOT, GateType.CZ}:
                adjusted["ctrl"] = int(adjusted["ctrl"]) + qubit_offset
                adjusted["target"] = int(adjusted["target"]) + qubit_offset
            elif gate["type"] is GateType.Tof:
                adjusted["ctrl1"] = int(adjusted["ctrl1"]) + qubit_offset
                adjusted["ctrl2"] = int(adjusted["ctrl2"]) + qubit_offset
                adjusted["target"] = int(adjusted["target"]) + qubit_offset
            elif "target" in adjusted:
                adjusted["target"] = int(adjusted["target"]) + qubit_offset
            self.gates.append(adjusted)

    def extend(self, gates: Iterable[Dict[str, object]]) -> None:
        for gate in gates:
            self.add_gate(gate)

    def copy(self) -> "QuantumCircuit":
        new_circuit = QuantumCircuit()
        new_circuit.n_qubits = self.n_qubits
        new_circuit.n_classical_bits = self.n_classical_bits
        new_circuit.gates = [gate.copy() for gate in self.gates]
        return new_circuit

    # ------------------------------------------------------------------
    # Gate insertion helpers
    def add_gate(self, gate: Dict[str, object]) -> None:
        if "type" not in gate:
            raise ValueError("Gate dictionary must include a 'type' field of GateType.")
        self.gates.append(gate.copy())

    @staticmethod
    def deps_of(gate: Dict[str, object]) -> Set[int]:
        deps: Set[int] = set()
        match gate["type"]:
            case GateType.CNOT | GateType.CZ:
                deps.add(int(gate["ctrl"]))
                deps.add(int(gate["target"]))
            case GateType.Tof:
                deps.update({int(gate["ctrl1"]), int(gate["ctrl2"]), int(gate["target"])})
            case GateType.MEASURE:
                deps.add(int(gate["qubit"]))
            case GateType.CONDITIONAL:
                deps.add(int(gate["target"]))
            case _:
                if "target" in gate:
                    deps.add(int(gate["target"]))
        return deps

    # 1- and 2-qubit gate shorthand helpers ---------------------------------
    def add_cnot(self, ctrl: int, target: int) -> None:
        self.gates.append({"type": GateType.CNOT, "ctrl": ctrl, "target": target})

    def add_cz(self, ctrl: int, target: int) -> None:
        self.gates.append({"type": GateType.CZ, "ctrl": ctrl, "target": target})

    def add_z(self, target: int) -> None:
        self.gates.append({"type": GateType.Z, "target": target})

    def add_x(self, target: int) -> None:
        self.gates.append({"type": GateType.X, "target": target})

    def add_h(self, target: int) -> None:
        self.gates.append({"type": GateType.HAD, "target": target})

    def add_s(self, target: int) -> None:
        self.gates.append({"type": GateType.S, "target": target})

    def add_t(self, target: int) -> None:
        self.gates.append({"type": GateType.T, "target": target})

    def add_tdg(self, target: int) -> None:
        self.gates.append({"type": GateType.Tdg, "target": target})

    def add_toffoli(self, c1: int, c2: int, target: int) -> None:
        self.gates.append({"type": GateType.Tof, "ctrl1": c1, "ctrl2": c2, "target": target})

    def add_measure(self, qubit: int, classical_bit: int) -> None:
        self.gates.append(
            {"type": GateType.MEASURE, "qubit": qubit, "classical_bit": classical_bit}
        )

    def add_conditional_x(self, classical_bit: int, target: int) -> None:
        self.gates.append(
            {
                "type": GateType.CONDITIONAL,
                "classical_bit": classical_bit,
                "target": target,
                "gate": GateType.X,
            }
        )

    def add_conditional_z(self, classical_bit: int, target: int) -> None:
        self.gates.append(
            {
                "type": GateType.CONDITIONAL,
                "classical_bit": classical_bit,
                "target": target,
                "gate": GateType.Z,
            }
        )

    def add_conditional_h(self, classical_bit: int, target: int) -> None:
        self.gates.append(
            {
                "type": GateType.CONDITIONAL,
                "classical_bit": classical_bit,
                "target": target,
                "gate": GateType.HAD,
            }
        )

    def add_conditional_cnot(self, classical_bit: int, ctrl: int, target: int) -> None:
        self.gates.append(
            {
                "type": GateType.CONDITIONAL,
                "classical_bit": classical_bit,
                "ctrl": ctrl,
                "target": target,
                "gate": GateType.CNOT,
            }
        )


