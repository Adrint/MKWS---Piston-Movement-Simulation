
import matplotlib.pyplot as plt
import cantera as ct
import sys
import os
import csv
import pandas as pd

temp_cisnienie = pd.read_excel("mkws_1.xlsx",sheet_name="mkws")
print(temp_cisnienie)
for x in range(len(temp_cisnienie)):

    # gaz_1 - argon
    argon = ct.Solution('air.yaml')
    argon.TPX = temp_cisnienie['T_4'][x], temp_cisnienie['P_4'][x]*ct.one_atm, "O2:1"

    # zbiornik na powietrze
    r1 = ct.IdealGasReactor(argon)

    # gaz_2 mieszanina gazow metan/powietrze
    gas = ct.Solution('gri30.yaml')
    gas.TP = temp_cisnienie['T_5'][x], temp_cisnienie['P_5'][x]*ct.one_atm
    gas.set_equivalence_ratio(1.1, 'CH4:1.0', 'O2:2, N2:7.52')

    # zbiornik metan/powietrze
    r2 = ct.IdealGasReactor(gas)

    # zbiornik dla srodowiska na powietrze
    env = ct.Reservoir(ct.Solution('air.yaml'))

    # sciana pomiedzy tłokami
    w = ct.Wall(r2, r1, A=2, K=0.5e-4, U=100.0)

    print(r1)

    #druga sciana przez ktora uchodzi cieplo do otoczenia
    w2 = ct.Wall(r2, env, A=3, U=500.0)

    #polaczenie zbiornikow
    sim = ct.ReactorNet([r1, r2])

    time = 0.0
    n_steps = 300
    output_data = []
    states1 = ct.SolutionArray(argon, extra=['t', 'V']) #stan argonu
    states2 = ct.SolutionArray(gas, extra=['t', 'V'])   #stan mieszaniny

    for n in range(n_steps):
        time += 4.e-4
        #print(n, time, r2.T)
        sim.advance(time)
        states1.append(r1.thermo.state, t=time, V=r1.volume)
        states2.append(r2.thermo.state, t=time, V=r2.volume)
        output_data.append(
            [time, r1.thermo.T, r1.thermo.P, r1.volume, r2.thermo.T,
             r2.thermo.P, r2.volume]
        )


    plt.clf()
    plt.subplot(2, 2, 1)
    h = plt.plot(states1.t, states1.T, 'g-', states2.t, states2.T, 'b-')
    plt.legend([temp_cisnienie['Legend T_4'][x],temp_cisnienie['Legend T_5'][x]], loc='lower right')
    plt.xlabel('Time (s)')
    plt.ylabel('Temperature (K)')

    plt.subplot(2, 2, 2)
    plt.plot(states1.t, states1.P / 1e5, 'g-', states2.t, states2.P / 1e5, 'b-')
    plt.xlabel('Time (s)')
    plt.ylabel('Pressure (Bar)')

    plt.subplot(2, 2, 3)
    plt.plot(states1.t, states1.V, 'g-', states2.t, states2.V, 'b-')
    plt.xlabel('Time (s)')
    plt.ylabel('Volume (m$^3$)')

    plt.figlegend(h, ['Argon', 'Mixture methane/air'], loc='lower right')
    plt.tight_layout()
    plt.show()

