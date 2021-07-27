{
 "cells": [
  {
   "cell_type": "markdown",
   "id": "56425542",
   "metadata": {},
   "source": [
    "# Benchmarking Different Methods 2\n",
    "\n",
    "In this task we will benchmark a number of different methods evaluating both performance and quality \n",
    "of solutions. \n",
    "\n",
    "Here we continue exploration of methods."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 11,
   "id": "c46e714e",
   "metadata": {},
   "outputs": [],
   "source": [
    "import numpy as np\n",
    "import matplotlib.pyplot as plt\n",
    "import pandas as pd\n",
    "\n",
    "import strawberryfields as sf\n",
    "from strawberryfields.ops import *\n",
    "import matplotlib\n",
    "\n",
    "font = {'family' : 'Dejavu Sans',\n",
    "        'weight' : 'bold',\n",
    "        'size'   : 22}\n",
    "matplotlib.rc('font', **font)\n"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "5260b26b",
   "metadata": {},
   "source": [
    "## Simple QAOA with STRAWBERRY FIELDS"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 12,
   "id": "327e195b",
   "metadata": {},
   "outputs": [],
   "source": [
    "import flatnetwork_simple as fns"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 67,
   "id": "009d1e43",
   "metadata": {},
   "outputs": [],
   "source": [
    "#Setup\n",
    "K = 20\n",
    "dt = 1.0\n",
    "\n",
    "#Parameters\n",
    "mu = lambda t,i: 1.0\n",
    "rho = 1.0\n",
    "\n",
    "#Annealing params\n",
    "J = 1.0\n",
    "theta = -J*dt/k"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 92,
   "id": "0080c26b",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Max MPO dim:  6\n"
     ]
    }
   ],
   "source": [
    "L = [1,3,1]\n",
    "d = 3\n",
    "fnet = fns.FlatNetwork(L,d)\n",
    "fnet.loadParams(mu, rho)\n",
    "fnet.make_mpos()\n",
    "\n",
    "S, D = fnet.getHamiltonian()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 93,
   "id": "1a2805d9",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "{(0, 0): -1.0, (1, 1): -1.0, (2, 2): -1.0}\n",
      "{(0, 0): 0.1111111111111111, (0, 1): 0.2222222222222222, (0, 2): 0.2222222222222222, (1, 1): 0.1111111111111111, (1, 2): 0.2222222222222222, (2, 2): 0.1111111111111111}\n",
      "3\n"
     ]
    }
   ],
   "source": [
    "print(S)\n",
    "print(D)\n",
    "print(np.prod(L))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 113,
   "id": "51caac30",
   "metadata": {},
   "outputs": [],
   "source": [
    "nmodes = int(np.prod(L))\n",
    "ham_simulation = sf.Program(nmodes)\n",
    "\n",
    "with ham_simulation.context as q:\n",
    "    #Prepare the initial state\n",
    "    Fock(3) | q[0] #Max particles allowed in system also upper bound on particle coun\n",
    "    \n",
    "    for i in range(K):\n",
    "        BSgate(theta, np.pi/2) | (q[0], q[1])\n",
    "                        \n",
    "        for pair in S:\n",
    "            Rgate(-1j*S[pair]/K*dt) | q[pair[0]]\n",
    "        for pair in D:\n",
    "            if(pair[0] == pair[1]):\n",
    "                Kgate(-1j*D[pair]/K*dt) | q[pair[0]]\n",
    "            else:\n",
    "                CKgate(-1j*D[pair]/K*dt) | (q[pair[0]], q[pair[1]])\n",
    "        "
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 117,
   "id": "5e246ca8",
   "metadata": {},
   "outputs": [],
   "source": [
    "eng = sf.Engine(backend=\"bosonic\", backend_options={\"cutoff_dim\": 5})"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 115,
   "id": "c71c9378",
   "metadata": {},
   "outputs": [],
   "source": [
    "results = eng.run(ham_simulation)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 116,
   "id": "cc12d98b",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "P(|0, 0>) =  0.0\n",
      "P(|0, 1>) =  0.0\n",
      "P(|0, 1>) =  0.0\n",
      "P(|0, 1>) =  0.0\n",
      "P(|0, 2>) =  0.0\n",
      "P(|0, 2>) =  0.0\n",
      "P(|0, 2>) =  0.0\n"
     ]
    }
   ],
   "source": [
    "state = results.state\n",
    "print(\"P(|0, 0>) = \", state.fock_prob([0, 1, 2]))\n",
    "print(\"P(|0, 1>) = \", state.fock_prob([0, 2, 1]))\n",
    "print(\"P(|0, 1>) = \", state.fock_prob([1, 2, 0]))\n",
    "print(\"P(|0, 1>) = \", state.fock_prob([1, 0, 2]))\n",
    "print(\"P(|0, 2>) = \", state.fock_prob([1, 2, 0]))\n",
    "print(\"P(|0, 2>) = \", state.fock_prob([2, 0, 1]))\n",
    "print(\"P(|0, 2>) = \", state.fock_prob([2, 1, 0]))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "5c65c454",
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.8.10"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
