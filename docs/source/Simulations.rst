

Simulations of Photo-Induced Properties using LITESOPH
========================================================

Photophysical processes are initiated by the absorption of light by the molecules. 
After light irradiation molecules get promoted to the electronic excited state. 
In the excited state, molecules can undergo a reaction on the same PES or they can 
deactivate to a ground electronic state via radiative channels like `fluorescence <https://en.wikipedia.org/wiki/Fluorescence>`_ and 
`phosphorescence <https://en.wikipedia.org/wiki/Phosphorescence>`_ or nonradiative channels like internal conversion ( IC_ ), and intersystem
crossing (`ISC <https://en.wikipedia.org/wiki/Intersystem_crossing>`_). To understand the photophysics and photochemistry of a system,
we have to first perform an :ref:`absorption spectrum` to get an idea about the optically accessible bright
and inaccessible dark states respectively. Then the state of interest can be targeted to understand the
photo dynamics in the excited state.
 
.. _IC : https://en.wikipedia.org/wiki/Internal_conversion#:~:text=Internal%20conversion%20is%20a%20non,(ejected)%20from%20the%20atom

.. _absorption spectrum:

Absorption Spectrum 
---------------------

The absorption spectrum provides information about the energies of the electronic excited state and
their transition probabilities. The absorption spectrum can be calculated using different theories like
TDDFT_, CASPT2_, CCSD_, and ADC_ (2) [1]_. Among all methods, TDDFT_ offers a good compromise
between accuracy and computational cost for a large system  [2]_ [3]_ [4]_ [5]_ [6]_ . Thus TDDFT_ is widely used to compute
the absorption spectrum. Both linear response (LR)-TDDFT and real time (RT)-TDDFT can be used
to calculate spectrum in frequency and time domain respectively. In our tools, we have only
incorporated the RT-TDDFT_ approach to compute the absorption spectrum as well as other properties
because this method is more rigorous and applicable to all kinds of systems.

##########################

.. _TDDFT : https://en.wikipedia.org/wiki/Time-dependent_density_functional_theory#:~:text=Time%2Ddependent%20density%2Dfunctional%20theory,as%20electric%20or%20magnetic%20fields.
.. _CASPT2 : https://pubs.acs.org/doi/10.1021/acs.jctc.2c00368
.. _RT-TDDFT : https://nwchemgit.github.io/RT-TDDFT.html
.. _ADC : https://adc-connect.org/v0.15.13/theory.html
.. _CCSD : https://en.wikipedia.org/wiki/Coupled_cluster#:~:text=For%20example%2C%20the%20CCSD(T,many%2Dbody%20perturbation%20theory%20arguments.

##########################


Calculations of Absorption Spectrum
#########################################
The :ref:`absorption spectrum` is calculated based on these three :ref:`engines`. Here are the results of some molecular systems using LITESOPH-GUI.

   
* :doc:`./GPAW/GPAW_Calculation` 

Kohn-Sham Decomposition (KSD)
-----------------------------------
Time-dependent density functional theory (TDDFT_) built on top of Kohn-Sham (KS) density functional theory (DFT) is a
powerful tool in computational physics and chemistry for accessing the light-matter interaction. Starting from the seminal work
on jellium nanoparticles, TDDFT_ has become an important tool for modelling plasmonic response from a quantum mechanical
perspective and proven to be useful for calculating the response of individual nanoparticles and their compounds as well as other
plasmonic materials. Additionally, a number of models and concepts have been developed for quantifying and understanding
plasmonic character within the TDDFT approach. TDDFT in the linear-response regime is often formulated in frequency space
in terms of the Casida matrix expressed in the Kohn-Sham electron-hole space.The Casida approach directly enables a decomposition of the electronic excitations into the underlying KS electron-hole transitions, which easily provides quantum-mechanical
understanding of the plasmonic response. By contrast, real-time TDDFT_ (RT-TDDFT) (an alternative but computationally efficient approach with favorable scaling with respect to system size and is also applicable to the nonlinear regime) results are often
limited to absorption spectra or the analysis of the induced densities or fields. However, recently, Rossi et al. have developed KS
decomposition ( KSD_ ) tool based on the RT-TDDFT code that is available in the free GPAW code. The underlying RT-TDDFT
code uses the linear combination of atomic orbitals ( LCAO_ ) method and enable calculations involving hundreds of noble metal
atoms.

In order to analyze the response in terms of the KSD, the decomposition is presented as a transition contribution map ( TCM_ ),
which is an especially useful representation for plasmonic systems in which resonances are typically superpositions of many
electron-hole excitations. The TCM represents the KSD weight at a fixed energy of excitation in the two-dimensional plane
spanned by the energy axes for occupied and unoccupied states. For more details, refer to [7]_.

More specifically, the 2D plot is defined by

.. math::
    \begin{equation}
    M^{TCM}_{\omega}(\varepsilon_o, \varepsilon_u) = \sum_{ia}w_{ia}(\omega)g_{ia}(\varepsilon_o, \varepsilon_u)
    \tag{1}
    \label{eq:1}
    \end{equation}
    
where indices `i` and `a` correspond to the occupied and unoccupied states, respectively. The function `g_{ia}` is a 
2D broadening function for the discrete KS `i \rightarrow a` transition contributions. By employing the 2D Gaussian 
function, it is written as

.. math::
    \begin{equation}
    g_{ia}(\varepsilon_o, \varepsilon_u) = \frac{1}{2\pi\sigma^2}\exp{\bigg [-\frac{(\varepsilon_o - \varepsilon_i)^2 + (\varepsilon_u - \varepsilon_a)^2}{2\sigma^2}\bigg ]}
    \tag{2}
    \label{eq:2}
    \end{equation}

where `\sigma` is the broadening parameter, which is generally taken to be the same as used for the spectral broadening.

The weight `w_{ia}(\omega)` in Eq. :math:`\ref{eq:1}` is obtained from the absorption decomposition normalized by the total absorption, i.e.

.. math::
    \begin{equation}
    w_{ia}(\omega) = S^x_{ia}(\omega)/S_x(\omega)
    \label{eq:3}
    \tag{3}
    \end{equation}


We  note here is that the above equation is given particularly for the x-polarized light. However, the same thing can also be evaluated for y or z-polarized light.

The KS decomposition of the absorption spectrum in Eq. :math:`\ref{eq:3}`  is defined as

.. math::
    \begin{equation}
    S^x_{ia}(\omega) = -\frac{4\omega}{\pi}Im[\mu^{x^\star}_{ia}\delta\rho^x_{ia}(\omega)]
    \label{eq:Sx_ia}
    \tag{4}
    \end{equation}


where  the dipole matrix element is obtained as

.. math::
    \begin{equation}
    \mu^{x}_{ia} = \int \psi_i^{(0)*}( r)x\psi_a^{(0)}( r)d\bf r
    \label{eq:mux_ia}
    \tag{5}
    \end{equation}


where `\psi_j^{(0)}` corresponds to the KS wave function for `j = i,a`.

The linear response of the real part of the KS density matrix in the electron-hole space is written as

.. math::
    \begin{equation}
    \delta\rho^x_{ia}(\omega) = \frac{1}{K_x}\int_0^\infty Re[\rho^x_{ia}(t) - \rho_{ia}(0^{0-})]e^{i\omega t}dt + O(K_x)
    \label{eq:delta}
    \tag{6}
    \end{equation}


where `K_x` is the laser strength and `\rho_{ia}(0^{0-})` is the initial density matrix before the `\delta`-pulse perturbation, 
and the superscript `x` indicates the direction of the perturbation.

Transition contribution map for the photoabsorption decomposition of Au55 metallic nanoparticle at 3.02 eV resonance 
energy calculated using LCAO TDDFT_ approach in GPAW code is shown in :ref:`Fig.1 <au55_tcm>`.

.. _au55_tcm:

.. figure:: ./Image_laser/Au55_tcm_3.02.png
    :width: 500px
    :align: center
    :height: 400px
    :alt: alternate text
    :figclass: align-center

    **Fig.1: Transition contribution map for the photoabsorption decomposition of Au55 metallic nanoparticle 
    at 3.02 eV resonance energy calculated using LCAO TDDFT approach in GPAW code. The KS eigenvalues are 
    given with respect to the Fermi level. The constant transition energy line** `\varepsilon_u - \varepsilon_o = \omega` 
    **is the analysis energy (solid line). Red and blue colors indicate positive and negative values of the 
    photoabsorption, respectively. The density of states (DOS) are also shown.**



Molecular Orbital (MO) Population
-----------------------------------

The Kohn-Sham (`KS <https://pubs.acs.org/doi/10.1021/ja9826892>`_) orbital can be expanded using gaussian basis function `\phi_\mu` as:

.. math::

    \psi_i (\mathbf r, \mathbf t) = \sum_{\mu = 1}^{N_{AO}} \mathbf {C_{\mu i}} (\mathbf t) \phi_\mu (\mathbf r) 
    \label{Eq:psi_i}
    \tag{7}

`Density matrix <https://en.wikipedia.org/wiki/Density_matrix>`_ can be obtained from the products of time-dependent coefficient:
 
.. math::

    \mathbf {P_{\mu \nu}} = \sum_i^{N_{MO}}  \mathbf {C_{\mu i}^*}(\mathbf t) \mathbf C_{i \nu}(\mathbf t)
    \label{Eq:P_nu}
    \tag{8}

Time dependent orbital population computed by projecting the density matrix on to the ground state
orbitals:

.. math::

    n_{\bf k} (\bf t) = \mathbf {C_k^*} \mathbf P (\mathbf t)\mathbf C_k(\mathbf t)
    \label{Eq:n_k}
    \tag{9}



#####################
.. _TDDFT : https://en.wikipedia.org/wiki/Time-dependent_density_functional_theory#:~:text=Time%2Ddependent%20density%2Dfunctional%20theory,as%20electric%20or%20magnetic%20fields.
.. _CASPT2 : https://pubs.acs.org/doi/10.1021/acs.jctc.2c00368
.. _RT-TDDFT : https://nwchemgit.github.io/RT-TDDFT.html
.. _ADC : https://adc-connect.org/v0.15.13/theory.html
.. _CCSD : https://en.wikipedia.org/wiki/Coupled_cluster#:~:text=For%20example%2C%20the%20CCSD(T,many%2Dbody%20perturbation%20theory%20arguments.
.. _LCAO : https://en.wikipedia.org/wiki/Linear_combination_of_atomic_orbitals#:~:text=A%20linear%20combination%20of%20atomic,atoms%20are%20described%20as%20wavefunctions.


LASER Simulation
-------------------
Once we have the photoabsorption spectrum of any system, we get an information about the excitation frequencies 
present in the system. Using any frequency of excitation, we can hit the system with a laser and study the time 
dynamics of any physical observable of our interest. 
 
The Gaussian light pulse is defined as


.. math::
    \begin{equation}
    \varepsilon(t) = \varepsilon_0\sin(\omega_0t)e^{-(t-t_0)^2/2\sigma^2}
    \label{eq:laser_pulse}
    \tag{10}
    \end{equation}


 
that induces a real time dynamics in the system. The pulse frequency `\omega_0` 
is tuned to the frequency of excitation of interest, the pulse duration is determined 
by `\sigma`, and the pulse is centered at `t_0`. The pulse strength `\varepsilon_0` is 
generally kept weak, to ensure that the system is in the linear response regime. In the 
frequency space, the pulse should be wide enough to cover the whole frequency of excitation.
  
The determination of the pulse width and its center is crucial for the light-matter interaction. 
However, these quantities can be evaluated from the envelope_ function in Eq. :math:`\ref{eq:laser_pulse}`, 
which is defined as
 
.. math::
    \begin{equation}
    G(t) = \exp(-(t-t_0)^2)/2\sigma^2)
    \label{eq:gaussian_envelope}
    \tag{11}
    \end{equation}


 
The Gaussian envelope in time will also yield the Gaussian envelope in frequency (Gaussians are eigenfunctions of a
Fourier transform), with width equal to the inverse of the width in time. 
The full width at half maximum ( FWHM_ ) of Gaussian pulse is given as

.. math::
    \begin{equation}
    \text{FWHM} = 2\sqrt{2\ln 2}\sigma_\omega
    \label{eq:fwhm}
    \tag{12}
    \end{equation}

The center of the pulse is obtained as

.. math::
    \begin{equation}
    t_0 = t-\sqrt{-2\sigma^2\ln G(t)}
    \label{eq:t_0}
    \tag{13}
    \end{equation}


LASER Masking  **to study energy transfer using RT-TDDFT approach**
#############
Energy transfer is one of the most fundamental processes on the molecular scale, governing light-harvesting in biological
systems and energy conversion in electronic devices such as organic solar cells or light-emitting diodes. The design principles
of natural light-harvesting complexes have found considerable interest, as scientists believe that the principles realized in nature
can be mimicked in the design of artificial organic devices.One standard method to interpret experimental data of excitation energy transfer between a donor (D) and an acceptor (A)
molecule separated by the distance R is the so-called Forster resonance energy transfer ( FRET_ ) theory. `Forster` theory describes ¨
the nonradiative energy transfer mediated by a (quantum-mechanical) coupling between the transition dipoles of the donor and
acceptor molecules. One of the central assumptions in FRET is that the coupling between D and A
can be described by a (point)-dipole-dipole interaction, falling as 1/R3.
Furthermore, FRET_ theory is formulated for the weak
coupling regime (i.e., the isolated D and A excited states do not change significantly on coupling).

The energy transfer rate is written as


.. math::
    \mathbf K^\text{ET} = 2\pi {\lvert V\rvert}^2\int_{0}^\infty\!\mathrm{d}\varepsilon {\mathbf J(\varepsilon)}
    \label{Eq:K^ET}
    \tag{14}

where `\mathbf J(\varepsilon)` is the spectral overlap between the normalized donor emission and acceptor absorption spectra.

The factor V in Eq. :math:`\ref{Eq:K^ET}` is the electronic coupling matrix element which is obtained using
Davydov splitting. In the case two same molecules, the
Davydov splitting `\Delta\Omega` equals the energy splitting `\Delta E` of the (nearly) degenerate excitation energies of the monomers 
in the supermolecule.

.. math::
    \begin{equation}
    V = \frac{\Delta\Omega}{2}
    \label{eq:Davydov_splitting}
    \tag{15}
    \end{equation}

There is however, an another alternative way of evaluating the required information by observing the `D` and `A` dipole moments separately. 
It significantly reduces the computational cost. We note that the Davydov splitting and consequently also the coupling matrix element `V` 
manifests itself as a frequency `\omega_{beat}` in the time-dependent `D` (and `A`) dipole moment. This frequency can be extracted as 
a beat frequency `\omega_{beat}` of an oscillation between `D` and `A`.

.. math::
    \begin{equation}
    V = \omega_{beat}
    \label{eq:V_beat}
    \tag{16}
    \end{equation}



##############################
.. _TDDFT : https://en.wikipedia.org/wiki/Time-dependent_density_functional_theory#:~:text=Time%2Ddependent%20density%2Dfunctional%20theory,as%20electric%20or%20magnetic%20fields.
.. _CASPT2 : https://pubs.acs.org/doi/10.1021/acs.jctc.2c00368
.. _RT-TDDFT : https://nwchemgit.github.io/RT-TDDFT.html
.. _ADC : https://adc-connect.org/v0.15.13/theory.html
.. _CCSD : https://en.wikipedia.org/wiki/Coupled_cluster#:~:text=For%20example%2C%20the%20CCSD(T,many%2Dbody%20perturbation%20theory%20arguments.
.. _LCAO : https://en.wikipedia.org/wiki/Linear_combination_of_atomic_orbitals#:~:text=A%20linear%20combination%20of%20atomic,atoms%20are%20described%20as%20wavefunctions.
.. _FRET : https://en.wikipedia.org/wiki/F%C3%B6rster_resonance_energy_transfer
.. _KSD : https://materialsmodeling.org/publications/2017-Kohn-Sham-decomposition-in-real-time-time-dependent-density-functional-theory-An-efficient-tool-for-analyzing-plasmonic-excitations/
.. _FWHM : https://en.wikipedia.org/wiki/Full_width_at_half_maximum
.. _envelope : https://en.wikipedia.org/wiki/Envelope_(waves)
.. _TCM : http://allie.dbcls.jp/pair/TCM;transition+contribution+map.html



.. _ref:

References
-----------
.. [1] González, L.; Escudero, D.; Serrano-Andrés, L. Progress and Challenges in the Calculation of
       Electronic Excited States. Chem. Phys. Chem. 2012, 13, 28-51.

.. [2] Varsano, D.; Di Felice, R.; Marques, M. A.; Rubio, A. A TDDFT study of the excited states
       of DNA bases and their assemblies. J. Phys. Chem. B. 2006, 110, 7129–7138.

.. [3] Lopata, K.; Govind, N. Modelling fast electron dynamics with real-time time-dependent
       density functional theory: application to small molecules and chromophore. J. Chem. Theory
       Comput. 2011, 7, 1344–1355.

.. [4] Lange, A. W.; Rohrdanz, M. A.; Herbert, J. M. Charge-transfer excited states in a π-stacked
       adenine dimer, as predicted using long-range-corrected time-dependent density functional
       theory. J. Phys. Chem. B. 2008,112, 6304–6308.

.. [5] Provorse, M. R.; Isborn, C. M. Electron dynamics with real-time time-dependent density
       functional theory. Int. J. Quantum Chem. 2016,116, 739–749.

.. [6] Tussupbayev, S.; Govind, N.; Lopata, K.; Cramer, C. J. Comparison of real-time and linear-
       response time-dependent density functional theories for molecular chromophores ranging
       from sparse to high densities of states. J. Chem. Theory Comput. 2015, 11, 1102–1109.

.. [7] T. P. Rossi, M. Kuisma, M. J. Puska, R. M. Nieminen, and P. Erhart, Kohn–sham decomposition in real-time time-dependent densityfunctional
       theory: An efficient tool for analyzing plasmonic excitations, Journal of Chemical Theory and Computation 13, 4779 (2017),
       pMID: 28862851, `https://doi.org/10.1021/acs.jctc.7b00589 <https://doi.org/10.1021/acs.jctc.7b00589>`_ .





