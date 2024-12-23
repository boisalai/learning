"""
Qiskit

Requirements:
    - pip install -q -U qiskit pylatexenc
"""

from qiskit import QuantumCircuit
import matplotlib.pyplot as plt
from numpy import pi

#from qiskit.quantum_info import SparsePauliOp
#from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
#from qiskit_ibm_runtime import EstimatorV2 as Estimator

def demo1():
    # Create a new circuit with two qubits
    qc = QuantumCircuit(2)
    
    # Add a Hadamard gate to qubit 0
    qc.h(0)
    
    # Perform a controlled-X gate on qubit 1, controlled by qubit 0
    qc.cx(0, 1)
    
    # Return a drawing of the circuit using MatPlotLib ("mpl"). This is the
    # last line of the cell, so the drawing appears in the cell output.
    # Remove the "mpl" argument to get a text drawing.
    figure = qc.draw("mpl")
    plt.show()

def demo2():
    qc = QuantumCircuit(5)
    qc.h([0, 1, 3, 4])
    qc.ry(2*pi/3, 1)
    qc.ry(pi, 4)
    qc.ry(3*pi, 2)
    qc.cx(1, 3)
    qc.cx(4, 2)
    qc.x([3, 4])

    figure = qc.draw("mpl")
    plt.show()


if __name__ == "__main__":
    demo2()