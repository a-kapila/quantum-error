from qiskit import Aer, IBMQ, execute
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
import numpy as np
from qiskit.providers.aer.noise import NoiseModel
from qiskit.test.mock import FakeYorktown
import os
import csv
device_backend = FakeYorktown()
coupling_map = device_backend.configuration().coupling_map
noise_model = NoiseModel.from_backend(device_backend)
basis_gates = noise_model.basis_gates
shots = 200000
def fresh_circuit(theta):
    # Construct quantum circuit
    circ = QuantumCircuit(4, 4)
    circ.ry(theta[0], 0)
    circ.ry(theta[1], 1)
    circ.ry(theta[2], 2)
    circ.ry(theta[3], 3)
    circ.cx(0, 1)
    circ.cx(1, 2)
    circ.cx(2, 3)
    circ.ry(theta[4], 0)
    circ.ry(theta[5], 1)
    circ.ry(theta[6], 2)
    circ.ry(theta[7], 3)
    return circ
def get_sigma(basis, index, result_noise):
    if basis == 'x':
        result = result_noise[0]
    elif basis == 'y':
        result = result_noise[1]
    elif basis == 'z':
        result = result_noise[2]
    vec = np.array([(-1) ** (sum([int(n[i]) for i in index])) for n in result.keys()])
    result = np.array(list(result.values()))
    return (np.dot(result, vec) / shots)
def calc_H(i, w):
    # Select the QasmSimulator from the Aer provider
    circ_z = fresh_circuit(params[i])
    circ_z.measure(list(range(4)), list(range(4)))
    circ_x = fresh_circuit(params[i])
    circ_x.h([0, 1, 2, 3])
    circ_x.measure(list(range(4)), list(range(4)))
    circ_y = fresh_circuit(params[i])
    circ_y.sdg([0, 1, 2, 3])
    circ_y.h([0, 1, 2, 3])
    circ_y.measure(list(range(4)), list(range(4)))
    # Execute noisy simulation and get counts
    simulator = Aer.get_backend('qasm_simulator')
    result_noise = execute([circ_x, circ_y, circ_z], simulator,
                           noise_model=noise_model,
                           coupling_map=coupling_map,
                           basis_gates=basis_gates,
                           shots=shots).result().get_counts()
    # reverse the order of qubits to something that makes sense
    rn = list(map(lambda x: dict(zip(list(map(lambda y: y[::-1], x.keys())), x.values())), result_noise))
    H = get_sigma('z', [0, 2], rn) + 0.372678 * (get_sigma('x', [0, 1], rn) + get_sigma('y', [0, 1], rn) + get_sigma('x', [2, 3], rn) + get_sigma('y',[2, 3],rn))
    try:
        w.writerow(np.append(deltas[i], [H]))
    except:
        print("Didn't add " + params[i])
deg = np.pi / 180
lb = -1.6 * deg
ub = 1.6 * deg
deltas = np.mgrid[lb:ub:7j, lb:ub:7j, lb:ub:7j, lb:ub:7j, lb:ub:7j, lb:ub:7j, lb:ub:7j, lb:ub:7j].reshape(8, -1).T
params = deltas + [-np.pi / 2, 0, -0.979924, -np.pi, 0, np.pi, np.pi, np.pi]
with open('no_spam_results.csv', "w") as f:
    csv_writer = csv.writer(f)
    csv_writer.writerow(['dth' + str(i) for i in range(1, 9)] + ['H'])
    for i in range(len(params)):
        calc_H(i, csv_writer)