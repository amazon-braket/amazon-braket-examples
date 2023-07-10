from braket.pulse import PulseSequence

from openqasm3.visitor import QASMVisitor
import openqasm3.ast as ast
import re


class _PhaseExtractor(QASMVisitor[dict]):
    """
    Tree Walkers that inspects the pulse sequence and extracts the phase value for
    all the the shift_phase instructions on an RF frame.
    """

    def visit_FunctionCall(self, node: ast.FunctionCall, context: dict):
        if node.name.name == "shift_phase":
            frame = self.visit(node.arguments[0], context)
            phase = self.visit(node.arguments[1], context)
            if m := re.search(r"q(\d+)_rf_frame", frame):
                context |= {int(m.group(1)): phase}

    def visit_Identifier(self, node: ast.Identifier, context: dict):
        return node.name

    def visit_FloatLiteral(self, node: ast.FloatLiteral, context: dict):
        return float(node.value)

    def visit_UnaryExpression(self, node: ast.UnaryExpression, context: dict) -> bool:
        if node.op == ast.UnaryOperator["-"]:
            return -1 * self.visit(node.expression, context)
        else:
            raise NotImplementedError


def extract_phases(pulse_sequence: PulseSequence):
    """
    Extract the hardcoded phases from the pulse program.
    """
    phases = {"null": None}
    _PhaseExtractor().visit(pulse_sequence._program.to_ast(), phases)
    phases.pop(
        "null"
    )  # {"null": None} is needed to avoid wrong test outcome in openqasm
    return phases
