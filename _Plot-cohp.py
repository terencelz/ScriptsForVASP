#!/usr/bin/env python
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import mpltools.style
mpltools.style.use('ggplot')
import re
import argparse
import warnings


def plot_helper():
    plt.axhline(y=0, c='k')
    plt.axvline(x=0, ls='--', c='k')
    if args.axis_range:
        plt.axis([args.axis_range[0], args.axis_range[1], args.axis_range[2], args.axis_range[3]])
    plt.xlabel('Energy (eV)')
    plt.ylabel('-pCOHP (Arbituary Unit / Unit Cell / eV)')
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        plt.legend(loc=0,  fontsize='small')
    plt.tight_layout()

parser = argparse.ArgumentParser(description='''Plot the -COHP, with consideration of spin-polarization.''')
parser.add_argument('bond_to_plot', type=int, help='No. of bond to plot')
parser.add_argument('-a', '--axis-range', type=eval, help='''the x and y range of axis in the form of
            '[Xmin,Xmax,Ymin,Ymax]'. If ISPIN=2, this option specifies the combined spin.''')
parser.add_argument('--ISPIN', type=int, help="manually override ISPIN detection")
parser.add_argument('-i', '--COHPCAR', default='COHPCAR.lobster', help="the input COHPCAR.lobster file name")
parser.add_argument('-o', '--output-prefix', default='COHP', help="the output files' prefix")
args = parser.parse_args()
n_bond_to_plot = args.bond_to_plot
ISPIN = args.ISPIN

with open(args.COHPCAR, 'r') as f:
    COHPCAR = f.readlines()

for N_headerlines, line in enumerate(COHPCAR):
    if re.match(r'No\.\d*:.*\(.*\)', line):
        break
for N_bonds, line in enumerate(COHPCAR[N_headerlines:]):
    if not re.match(r'No\.\d*:.*\(.*\)', line):
        break
data_start_line = N_headerlines + N_bonds

for i in range(len(COHPCAR)):
    COHPCAR[i] = COHPCAR[i].split()

N_steps = int(COHPCAR[1][2])

if args.ISPIN:
    print "Using user specified ISPIN."
else:
    try:
        with open('OUTCAR', 'r') as f:
            for line in f:
                if 'ISPIN' in line:
                    ISPIN = int(line.split()[2])
    except IOError:
        try:
            with open('INCAR', 'r') as f:
                for line in f:
                    m = re.match(r'\s*ISPIN\s*=\s*(\d)\s*', line)
                    if m:
                        ISPIN = int(m.group(1))
        except IOError:
            raise IOError("Can't determine ISPIN! Either manually specify it, or provide OUTCAR or INCAR")

if 'ISPIN' not in globals():
    try:
        with open('OUTCAR', 'r') as f:
            for line in f:
                if 'ISPIN' in line:
                    ISPIN = int(line.split()[2])
    except IOError:
        try:
            with open('INCAR', 'r') as f:
                for line in f:
                    if 'ISPIN' in line:
                        ISPIN = int(line.split()[-1])
        except IOError:
            raise IOError('No ISPIN value determined!')

if ISPIN == 2:
    col_names = ['E', 'avg_up', 'avg_integrated_up']
    for n_bond in range(1, N_bonds + 1):
        col_names.extend(['No.{0}_up'.format(n_bond), 'No.{0}_integrated_up'.format(n_bond)])
    col_names.extend(['avg_down', 'avg_integrated_down'])
    for n_bond in range(1, N_bonds + 1):
        col_names.extend(['No.{0}_down'.format(n_bond), 'No.{0}_integrated_down'.format(n_bond)])
    COHP_data = np.array(COHPCAR[data_start_line:data_start_line + N_steps], dtype=float)

    col_up_to_plot = n_bond_to_plot * 2 + 1
    col_down_to_plot = (n_bond_to_plot + N_bonds + 1) * 2 + 1

    # Plot the separated COHP
    plt.plot(COHP_data[:, 0], -COHP_data[:, col_up_to_plot], label=col_names[col_up_to_plot])
    plt.plot(COHP_data[:, 0], -COHP_data[:, col_down_to_plot], label=col_names[col_down_to_plot])
    plot_helper()
    if args.axis_range:
        plt.axis([args.axis_range[0], args.axis_range[1], args.axis_range[2]/2., args.axis_range[3]/2.])
    plt.savefig(args.output_prefix + '-spin-separated.png')
    plt.close()

    # Plot the combined COHP
    plt.plot(COHP_data[:, 0], -COHP_data[:, col_up_to_plot] - COHP_data[:, col_down_to_plot])
    plot_helper()
    plt.savefig(args.output_prefix + '-spin-combined.png')
    plt.close()

elif ISPIN == 1:
    col_names = ['E', 'avg', 'avg_integrated']
    for n_bond in range(1, N_bonds + 1):
        col_names.extend(['No.{0}'.format(n_bond), 'No.{0}_integrated'.format(n_bond)])

    COHP_data = np.array(COHPCAR[data_start_line:data_start_line + N_steps], dtype=float)

    col_to_plot = n_bond_to_plot * 2 + 1
    plt.plot(COHP_data[:, 0], -COHP_data[:, col_to_plot], label=col_names[col_to_plot])
    plot_helper()
    plt.savefig(args.output_prefix + '.png')
    plt.close()