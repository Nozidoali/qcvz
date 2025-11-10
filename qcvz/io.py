"""Conversion helpers between qcvz circuits and pyzx circuits."""

from __future__ import annotations

from .quantum_circuit import GateType, QuantumCircuit

import pyzx as zx


def from_pyzx_circuit(pyzx_circuit: "zx.Circuit") -> QuantumCircuit:
    """Convert a :mod:`pyzx` circuit to a :class:`QuantumCircuit`."""

    circuit = QuantumCircuit()
    circuit.request_qubits(pyzx_circuit.qubits)

    for gate in pyzx_circuit.gates:
        name = gate.name
        if name == "Tof":
            circuit.add_toffoli(gate.ctrl1, gate.ctrl2, gate.target)
        elif name == "CCZ":
            circuit.add_h(gate.target)
            circuit.add_toffoli(gate.ctrl1, gate.ctrl2, gate.target)
            circuit.add_h(gate.target)
        elif name == "CNOT":
            circuit.add_cnot(gate.control, gate.target)
        elif name in {"NOT", "X"}:
            circuit.add_x(gate.target)
        elif name == "CZ":
            circuit.add_cz(gate.control, gate.target)
        elif name == "Z":
            circuit.add_z(gate.target)
        elif name in {"HAD", "H"}:
            circuit.add_h(gate.target)
        elif name == "S":
            circuit.add_s(gate.target)
        elif name == "T":
            circuit.add_t(gate.target)
        elif name in {"TDAG", "Tdg"}:
            circuit.add_tdg(gate.target)
        elif name == "MEASURE":
            raise NotImplementedError("Measurement import from pyzx is not supported yet.")
        else:
            raise NotImplementedError(f"Unsupported pyzx gate: {name}")

    return circuit


def to_pyzx_circuit(circuit: QuantumCircuit) -> "zx.Circuit":
    """Convert a :class:`QuantumCircuit` into an equivalent :mod:`pyzx` circuit."""

    pyzx_circuit = zx.Circuit(circuit.n_qubits)

    for gate in circuit.gates:
        gate_type: GateType = gate["type"]  # type: ignore[assignment]
        if gate_type is GateType.CNOT:
            pyzx_circuit.add_gate("CNOT", gate["ctrl"], gate["target"])
        elif gate_type is GateType.CZ:
            pyzx_circuit.add_gate("CZ", gate["ctrl"], gate["target"])
        elif gate_type is GateType.Tof:
            pyzx_circuit.add_gate("Tof", gate["ctrl1"], gate["ctrl2"], gate["target"])
        elif gate_type is GateType.X:
            pyzx_circuit.add_gate("NOT", gate["target"])
        elif gate_type is GateType.Z:
            pyzx_circuit.add_gate("Z", gate["target"])
        elif gate_type is GateType.HAD:
            pyzx_circuit.add_gate("HAD", gate["target"])
        elif gate_type is GateType.S:
            pyzx_circuit.add_gate("S", gate["target"])
        elif gate_type is GateType.T:
            pyzx_circuit.add_gate("T", gate["target"])
        elif gate_type is GateType.Tdg:
            pyzx_circuit.add_gate("Tdg", gate["target"])
        elif gate_type is GateType.MEASURE:
            raise NotImplementedError("Measurement export to pyzx is not supported.")
        elif gate_type is GateType.CONDITIONAL:
            raise NotImplementedError("Conditional gates are not supported in pyzx export.")
        else:
            raise NotImplementedError(f"Unsupported gate type for pyzx export: {gate_type}")

    return pyzx_circuit


def from_qasm(qasm: str) -> QuantumCircuit:
    """Create a :class:`QuantumCircuit` from a QASM string via :mod:`pyzx`."""

    return from_pyzx_circuit(zx.Circuit.from_qasm(qasm))


def from_file(path: str) -> QuantumCircuit:
    """Load a :class:`QuantumCircuit` from a file using :mod:`pyzx`'s reader."""

    return from_pyzx_circuit(zx.Circuit.load(path))


def to_qasm(circuit: QuantumCircuit) -> str:
    """Convert a :class:`QuantumCircuit` to an OpenQASM string via :mod:`pyzx`."""

    return to_pyzx_circuit(circuit).to_qasm()


__all__ = [
    "from_pyzx_circuit",
    "from_qasm",
    "from_file",
    "to_pyzx_circuit",
    "to_qasm",
]


