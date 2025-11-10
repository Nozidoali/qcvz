from pathlib import Path

from qcvz import from_file, plot_circuit, to_qasm


def bell_pair():
    # Fallback circuit if the sample file cannot be read.
    from qcvz import QuantumCircuit

    circ = QuantumCircuit()
    q0, q1 = circ.request_qubits(2)
    circ.add_h(q0)
    circ.add_cnot(q0, q1)
    return circ


if __name__ == "__main__":
    sample_path = Path(__file__).with_name("sample.qc")
    if sample_path.exists():
        circuit = from_file(str(sample_path))
        print(f"Loaded circuit from {sample_path}")
    else:
        circuit = bell_pair()
        print("sample.qc not found; using fallback bell pair circuit")

    output_png = Path("circuit.png")
    plot_circuit(circuit, str(output_png))
    print(f"Saved {output_png}")

    print("QASM:")
    print(to_qasm(circuit))

