"""Visualization utilities for :mod:`qcvz` quantum circuits."""

from __future__ import annotations

import matplotlib.pyplot as plt
import matplotlib.transforms as mtrans

from .quantum_circuit import GateType, QuantumCircuit


class QuantumCircuitVisualizer:
    """Class for visualizing quantum circuits with measurement support."""

    DEFAULT_XC = 0.4
    DEFAULT_YC = 0.5
    DEFAULT_XM = 0.25
    DEFAULT_YM = 0.25
    DEFAULT_MS = 16

    DEFAULT_COLORS = {
        GateType.CNOT: "b",
        GateType.CZ: "purple",
        GateType.Tof: "g",
        GateType.T: "r",
        GateType.Tdg: "r",
        GateType.X: "b",
        GateType.Z: "black",
        GateType.S: "m",
        GateType.HAD: "g",
        GateType.MEASURE: "orange",
    }
    GATE_LABELS = {
        GateType.X: "X",
        GateType.S: "S",
        GateType.HAD: "H",
        GateType.T: "T",
        GateType.Tdg: "T",
        GateType.Z: "Z",
    }

    DEFAULT_LINE_WIDTH = 1
    DEFAULT_CLASSICAL_LINE_OFFSET = 0.02
    DEFAULT_MEASUREMENT_LINE_OFFSET = 0.02
    DEFAULT_FONT_SIZE = 8
    DEFAULT_GATE_FONT_SIZE = 10
    DEFAULT_QUANTUM_LINE_COLOR = "gray"
    DEFAULT_CLASSICAL_LABEL_COLOR = "red"
    DEFAULT_MEASUREMENT_CONNECTION_COLOR = "black"
    DEFAULT_GATE_EDGE_COLOR = "black"
    DEFAULT_GATE_EDGE_WIDTH = 1

    def __init__(
        self,
        xc: float | None = None,
        yc: float | None = None,
        xm: float | None = None,
        ym: float | None = None,
        ms: int | None = None,
        colors: dict | None = None,
        remove_overlap: bool = True,
        line_width: int | None = None,
        classical_line_offset: float | None = None,
        measurement_line_offset: float | None = None,
        font_size: int | None = None,
        gate_font_size: int | None = None,
        quantum_line_color: str | None = None,
        classical_label_color: str | None = None,
        measurement_connection_color: str | None = None,
        gate_edge_color: str | None = None,
        gate_edge_width: int | None = None,
    ):
        self.xc = xc if xc is not None else self.DEFAULT_XC
        self.yc = yc if yc is not None else self.DEFAULT_YC
        self.xm = xm if xm is not None else self.DEFAULT_XM
        self.ym = ym if ym is not None else self.DEFAULT_YM
        self.ms = ms if ms is not None else self.DEFAULT_MS
        self.colors = colors.copy() if colors is not None else self.DEFAULT_COLORS.copy()
        self.remove_overlap = remove_overlap
        self.line_width = line_width if line_width is not None else self.DEFAULT_LINE_WIDTH
        self.classical_line_offset = (
            classical_line_offset
            if classical_line_offset is not None
            else self.DEFAULT_CLASSICAL_LINE_OFFSET
        )
        self.measurement_line_offset = (
            measurement_line_offset
            if measurement_line_offset is not None
            else self.DEFAULT_MEASUREMENT_LINE_OFFSET
        )
        self.font_size = font_size if font_size is not None else self.DEFAULT_FONT_SIZE
        self.gate_font_size = (
            gate_font_size if gate_font_size is not None else self.DEFAULT_GATE_FONT_SIZE
        )
        self.quantum_line_color = (
            quantum_line_color if quantum_line_color is not None else self.DEFAULT_QUANTUM_LINE_COLOR
        )
        self.classical_label_color = (
            classical_label_color
            if classical_label_color is not None
            else self.DEFAULT_CLASSICAL_LABEL_COLOR
        )
        self.measurement_connection_color = (
            measurement_connection_color
            if measurement_connection_color is not None
            else self.DEFAULT_MEASUREMENT_CONNECTION_COLOR
        )
        self.gate_edge_color = (
            gate_edge_color if gate_edge_color is not None else self.DEFAULT_GATE_EDGE_COLOR
        )
        self.gate_edge_width = (
            gate_edge_width if gate_edge_width is not None else self.DEFAULT_GATE_EDGE_WIDTH
        )

    @staticmethod
    def schedule_gates(circuit: QuantumCircuit, remove_overlap: bool = True) -> dict[int, int]:
        gate_loc: dict[int, int] = {}
        total_bits = circuit.n_qubits + circuit.n_classical_bits
        level = [-1] * total_bits

        for i, gate in enumerate(circuit.gates):
            deps: set[int] = QuantumCircuit.deps_of(gate)
            gate_type = gate["type"]

            if gate_type is GateType.MEASURE and "classical_bit" in gate:
                deps.add(circuit.n_qubits + int(gate["classical_bit"]))

            if gate_type is GateType.CONDITIONAL and "classical_bit" in gate:
                deps.add(circuit.n_qubits + int(gate["classical_bit"]))

            if remove_overlap:
                quantum_deps = [d for d in deps if d < circuit.n_qubits]
                if quantum_deps:
                    min_idx, max_idx = min(quantum_deps), max(quantum_deps)
                    deps.update(range(min_idx, max_idx + 1))

                classical_deps = [d for d in deps if d >= circuit.n_qubits]
                if classical_deps:
                    min_idx, max_idx = min(classical_deps), max(classical_deps)
                    deps.update(range(min_idx, max_idx + 1))

            max_level = 1 + max([level[d] for d in deps], default=-1)
            for dep in deps:
                level[dep] = max_level
            gate_loc[i] = max_level
        return gate_loc

    def _setup_figure(self, circ: QuantumCircuit, gloc: dict[int, int]) -> tuple:
        cols = max(gloc.values()) + 1 if gloc else 1
        total_lines = circ.n_qubits + circ.n_classical_bits

        w, h = cols * self.xc + 2 * self.xm, (total_lines - 1) * self.yc + 2 * self.ym
        fig, ax = plt.subplots(figsize=(w, h))

        ax.set_xlim(-self.xm, cols * self.xc + self.xm)
        ax.set_ylim(-self.ym, (total_lines - 1) * self.yc + self.ym)
        ax.axis("off")

        return fig, ax, cols, total_lines

    def _draw_lines(self, ax, circ: QuantumCircuit, total_lines: int):
        y = {q: (total_lines - 1 - q) * self.yc for q in range(total_lines)}
        tr = mtrans.blended_transform_factory(ax.transAxes, ax.transData)

        for q in range(circ.n_qubits):
            ax.axhline(y[q], lw=self.line_width, c=self.quantum_line_color)
            ax.text(
                -0.02,
                y[q],
                f"q{q}",
                ha="right",
                va="center",
                transform=tr,
                fontsize=self.font_size,
            )

        for c in range(circ.n_classical_bits):
            classical_line_y = y[circ.n_qubits + c]
            line_spacing = self.classical_line_offset / 2
            ax.axhline(
                classical_line_y - line_spacing,
                lw=self.line_width,
                c=self.quantum_line_color,
            )
            ax.axhline(
                classical_line_y + line_spacing,
                lw=self.line_width,
                c=self.quantum_line_color,
            )
            ax.text(
                -0.02,
                classical_line_y,
                f"c{c}",
                ha="right",
                va="center",
                transform=tr,
                fontsize=self.font_size,
                color=self.classical_label_color,
            )

        return y

    def _draw_cnot_gate(self, ax, p: float, y: dict, gate: dict):
        half_ms = self.ms // 2
        color = self.colors.get(GateType.CNOT, "b")
        ax.plot([p, p], [y[gate["ctrl"]], y[gate["target"]]], color, linewidth=self.line_width)
        ax.plot([p], [y[gate["ctrl"]]], "o", color=color, ms=half_ms)
        ax.plot([p], [y[gate["target"]]], "x", color=color, ms=half_ms)

    def _draw_cz_gate(self, ax, p: float, y: dict, gate: dict):
        color = self.colors.get(GateType.CZ, "purple")
        ax.plot([p, p], [y[gate["ctrl"]], y[gate["target"]]], color, linewidth=self.line_width)
        ax.plot([p], [y[gate["ctrl"]]], "o", color=color, ms=self.ms)
        ax.plot([p], [y[gate["target"]]], "o", color=color, ms=self.ms)

    def _draw_toffoli_gate(self, ax, p: float, y: dict, gate: dict):
        half_ms = self.ms // 2
        color = self.colors.get(GateType.Tof, "g")
        tgt = y[gate["target"]]
        for c in ("ctrl1", "ctrl2"):
            ax.plot([p, p], [y[gate[c]], tgt], color, linewidth=self.line_width)
            ax.plot([p], [y[gate[c]]], "o", color=color, ms=half_ms)
        ax.plot([p], [tgt], "x", color=color, ms=half_ms)

    def _draw_single_qubit_gate(self, ax, p: float, y: dict, gate: dict, gate_type: GateType):
        qt = y[gate["target"]]
        color = self.colors.get(gate_type, "purple")
        label = self.GATE_LABELS.get(gate_type, gate_type.name)
        ax.plot(
            [p],
            [qt],
            "s",
            ms=self.ms,
            markerfacecolor=color,
            markeredgecolor=self.gate_edge_color,
            markeredgewidth=self.gate_edge_width,
        )
        ax.text(
            p,
            qt,
            label,
            ha="center",
            va="center",
            fontsize=self.gate_font_size,
            color="white",
        )

    def _draw_measurement_gate(self, ax, p: float, y: dict, gate: dict, circ: QuantumCircuit):
        qt = y[gate["qubit"]]
        color = self.colors.get(GateType.MEASURE, "orange")
        ax.plot(
            [p],
            [qt],
            "o",
            ms=self.ms,
            markerfacecolor=color,
            markeredgecolor=self.gate_edge_color,
            markeredgewidth=self.gate_edge_width,
        )
        ax.text(p, qt, "M", ha="center", va="center", fontsize=self.gate_font_size, color="black")

        classical_y = y[circ.n_qubits + gate["classical_bit"]]
        ax.plot(
            [p, p],
            [qt, classical_y],
            color=self.measurement_connection_color,
            linewidth=self.line_width,
        )
        ax.plot(
            [p + self.measurement_line_offset, p + self.measurement_line_offset],
            [qt, classical_y],
            color=self.measurement_connection_color,
            linewidth=self.line_width,
        )

    def _draw_conditional_gate(self, ax, p: float, y: dict, gate: dict, circ: QuantumCircuit):
        qt = y[gate["target"]]
        inner_type = gate.get("gate")
        gate_color = self.colors.get(inner_type, "purple") if inner_type else "purple"
        label = (
            self.GATE_LABELS.get(inner_type, inner_type.name if inner_type else "?")
            if isinstance(inner_type, GateType)
            else (inner_type or "?")
        )
        ax.plot(
            [p],
            [qt],
            "s",
            ms=self.ms,
            markerfacecolor=gate_color,
            markeredgecolor=self.gate_edge_color,
            markeredgewidth=self.gate_edge_width,
        )
        ax.text(
            p,
            qt,
            label,
            ha="center",
            va="center",
            fontsize=self.gate_font_size,
            color="white",
        )

        if "classical_bit" in gate:
            classical_ctrl = gate["classical_bit"]
            classical_y = y[circ.n_qubits + classical_ctrl]
            line_spacing = self.classical_line_offset / 2

            ax.plot(
                [p, p],
                [qt, classical_y - line_spacing],
                color=self.measurement_connection_color,
                linewidth=self.line_width,
            )
            ax.plot(
                [p + self.measurement_line_offset, p + self.measurement_line_offset],
                [qt, classical_y + line_spacing],
                color=self.measurement_connection_color,
                linewidth=self.line_width,
            )

    def _draw_unknown_gate(self, ax, p: float, y: dict, gate: dict, gate_type):
        qt = y.get(gate.get("target", 0), 0)
        color = self.colors.get(gate_type, "black")
        label = (
            gate_type.name if isinstance(gate_type, GateType) else str(gate_type)
        )
        ax.plot(
            [p],
            [qt],
            "s",
            ms=self.ms,
            markerfacecolor=color,
            markeredgecolor=self.gate_edge_color,
            markeredgewidth=self.gate_edge_width,
        )
        ax.text(
            p,
            qt,
            label,
            ha="center",
            va="center",
            fontsize=self.gate_font_size,
            color="white",
        )

    def _draw_gates(self, ax, circ: QuantumCircuit, gloc: dict[int, int], y: dict):
        x = {i: c * self.xc for i, c in gloc.items()}

        for i, gate in enumerate(circ.gates):
            p = x[i]
            gate_type = gate["type"]

            if gate_type is GateType.CNOT:
                self._draw_cnot_gate(ax, p, y, gate)
            elif gate_type is GateType.CZ:
                self._draw_cz_gate(ax, p, y, gate)
            elif gate_type is GateType.Tof:
                self._draw_toffoli_gate(ax, p, y, gate)
            elif gate_type in {GateType.T, GateType.Tdg, GateType.X, GateType.S, GateType.HAD, GateType.Z}:
                self._draw_single_qubit_gate(ax, p, y, gate, gate_type)
            elif gate_type is GateType.MEASURE:
                self._draw_measurement_gate(ax, p, y, gate, circ)
            elif gate_type is GateType.CONDITIONAL:
                self._draw_conditional_gate(ax, p, y, gate, circ)
            else:
                self._draw_unknown_gate(ax, p, y, gate, gate_type)

    def plot_circuit(self, circ: QuantumCircuit, fn: str | None = None):
        gloc = self.schedule_gates(circ, self.remove_overlap)
        fig, ax, _, total_lines = self._setup_figure(circ, gloc)
        y = self._draw_lines(ax, circ, total_lines)
        self._draw_gates(ax, circ, gloc, y)

        try:
            if fn:
                plt.savefig(fn, bbox_inches="tight")
            else:
                plt.show()
        finally:
            plt.close(fig)


def plot_circuit(circ: QuantumCircuit, fn: str | None = None):
    visualizer = QuantumCircuitVisualizer()
    visualizer.plot_circuit(circ, fn)


