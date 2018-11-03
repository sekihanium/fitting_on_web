import os, time, glob
import pathlib
import pandas
import re
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO


def plot_all(array_x, array_y, df_fwd, df_rev, mode='normal', filename=None, show=True):
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.direction'] = 'in'
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['xtick.major.width'] = 1.0  # y軸主目盛り線の線幅
    plt.rcParams['ytick.major.width'] = 1.0  # y軸主目盛り線の線幅
    plt.rcParams['font.size'] = 10

    plt.figure(figsize=(5, 4), dpi=100)
    if mode == 'revlog':
        plt.plot(-array_x, -array_y, label='fitting')
        plt.plot(-df_rev['Sweep (V)@Temporary'], -df_rev['Measure (A)@Temporary'], label='rev')
        plt.ylim([1e-6, 1e-1])
        plt.xlim([0, 12])
        plt.title('HSMS2850_revlog')
        plt.yscale('log')

    elif mode == 'revlog_0.5':
        plt.plot(-array_x, -array_y, label='fitting')
        plt.plot(-df_rev['Sweep (V)@Temporary'], -df_rev['Measure (A)@Temporary'], label='rev')
        plt.ylim([2e-7, 1e-5])
        plt.xlim([0, 0.5])
        plt.title('HSMS2850_revlog')
        plt.yscale('log')

    elif mode == 'normal':
        plt.plot(array_x, array_y, label='fitting')
        plt.plot(df_fwd['Sweep (V)@Temporary'], df_fwd['Measure (A)@Temporary'], label='fwd')
        plt.plot(df_rev['Sweep (V)@Temporary'], df_rev['Measure (A)@Temporary'], label='rev')

        plt.xlim([-15, 2])
        plt.ylim([-0.1, 0.05])
        plt.title('HSMS2850_normal')

    elif mode == 'normal_measured':
        plt.plot(df_fwd['Sweep (V)@Temporary'], df_fwd['Measure (A)@Temporary'], label='fwd')
        plt.plot(df_rev['Sweep (V)@Temporary'], df_rev['Measure (A)@Temporary'], label='rev')

        plt.xlim([-15, 2])
        plt.ylim([-0.07, 0.02])
        plt.title('HSMS2850_normal_meas')

    elif mode == 'fwdlog':
        plt.plot(array_x, array_y, label='fitting')
        plt.plot(df_fwd['Sweep (V)@Temporary'], df_fwd['Measure (A)@Temporary'], label='fwd')
        plt.plot(df_rev['Sweep (V)@Temporary'], df_rev['Measure (A)@Temporary'], label='rev')
        plt.yscale('log')
        plt.xlim([0, 0.4])
        plt.ylim([1e-8, 1])
        plt.title('HSMS2850_fwdlog')

    plt.xlabel('Voltage [V]')
    plt.ylabel('Current [A]')
    plt.legend(shadow=True)
    plt.grid(True)

    figfile = BytesIO()
    if filename is not None:
        full_filename = os.path.join('static', str(time.time())+filename)
        plt.savefig(figfile, format='png')
        figfile.seek(0)
    if show:
        plt.show()

    return figfile.getvalue()


def merge_csv(path_to_csv):
    path = pathlib.Path(path_to_csv)
    fwd = []
    rev = []
    for p in path.iterdir():
        pattern = r"hsms2850_0to(\d+)m.csv"
        match = re.match(pattern, str(p.name))
        if match:
            fwd.append(int(match.group(1)))

        pattern = r"hsms2850_r0to(\d+)m.csv"
        match = re.match(pattern, str(p.name))
        if match:
            rev.append(int(match.group(1)))

    fwd.sort(reverse=True)
    rev.sort(reverse=True)

    # fwd
    df = pandas.read_csv(f'measurement_csv/hsms2850_0to{max(fwd)}m.csv')
    for v in fwd:
        df = df[df['Sweep (V)@Temporary'] > v / 1000]
        df_tmp = pandas.read_csv(f'measurement_csv/hsms2850_0to{v}m.csv')
        df = pandas.concat([df, df_tmp])
    df = df.sort_values('Sweep (V)@Temporary')
    df_fwd = df

    # rev
    df = pandas.read_csv(f'measurement_csv/hsms2850_r0to{max(fwd)}m.csv')
    for v in rev:
        df = df[df['Sweep (V)@Temporary'] > v / 1000]
        df_tmp = pandas.read_csv(f'measurement_csv/hsms2850_r0to{v}m.csv')
        df = pandas.concat([df, df_tmp])
    df = df.sort_values('Sweep (V)@Temporary')
    df_rev = df

    return df_fwd, df_rev


def diode4(x, NBVL, NBV, BV, IBVL, IBV, Isr, Vj, M, NR, IKF, N, Is):
    q = 1.60218e-19
    k = 1.3807e-23
    T = 300
    Vt = (k*T)/q  # this is trivial because it's constant
    Inrm = Is * (np.exp(x/(N*Vt)) - 1)
    Kinj = (IKF/(IKF+Inrm))**0.5
    Irec = Isr*(np.exp(x/(NR*Vt)) - 1)
    Kgen = ((1-x/Vj)**2+0.005)**(M/2)

    Irev_l = IBVL*np.exp(-1*(x+BV)/(NBVL*Vt))
    Irev_h = IBV*np.exp(-1*(x+BV)/(NBV*Vt))

    Ifwd = Inrm*Kinj + Irec*Kgen
    Irev = Irev_h #+ Irev_l

    #return -Irev_h
    return Ifwd - Irev


def main():
    fwd, rev = merge_csv('measurement_csv')
    parameters_old = {'Is': 2.81654e-6,
                  'Rs': 46.2,
                  'N': 1.06,
                  'NBVL': 60.1,
                  'NBV': 0.68,
                  'BV': 4.84,
                  'IBVL': 2.9325e-4,
                  'IBV': 1.381e-165,
                  'IKF': 40.5,
                  'Isr': 4e-6,
                  'Vj': 0.35,
                  'M': 0.5,
                  'NR': 2}

    parameters = {'Is': 2.81654e-6,
                  'Rs': 46.2,
                  'N': 1.06,
                  'NBVL': 30,
                  'NBV': 32,
                  'BV': 4.84,
                  'IBVL': 1e-7,
                  'IBV': 9e-5,
                  'IKF': 40.5,
                  'Isr': 1.67e-8,
                  'Vj': 0.35,
                  'M': 0.5,
                  'NR': 2}
    parameters_list = [parameters[name] for name in
                       ['NBVL', 'NBV', 'BV', 'IBVL', 'IBV', 'Isr', 'Vj', 'M', 'NR', 'IKF', 'N', 'Is']]
    array_x = np.linspace(-15, 15, 100000)
    #plot_all(array_x, diode4(array_x, *parameters_list), fwd, -rev, mode='normal')
    plot_all(array_x, diode4(array_x, *parameters_list), fwd, -rev, mode='revlog')
    plot_all(array_x, diode4(array_x, *parameters_list), fwd, -rev, mode='revlog_0.5')
    #plot_all(array_x, diode4(array_x, *parameters_list), fwd, -rev, mode='fwdlog')

    q = 1.60218e-19
    k = 1.3807e-23
    T = 300
    Vt = (k * T) / q
    print(1/(0.8915*Vt))


def make_plot(fwd, rev, diode_spice = None):
    parameters = {'Is': 2.81654e-6,
                  'Rs': 46.2,
                  'N': 1.06,
                  'NBVL': 30,
                  'NBV': 32,
                  'BV': 4.84,
                  'IBVL': 1e-7,
                  'IBV': 9e-5,
                  'IKF': 40.5,
                  'Isr': 1.67e-8,
                  'Vj': 0.35,
                  'M': 0.5,
                  'NR': 2}
    if diode_spice is not None:
        parameters = diode_spice
    parameters_list = [parameters[name] for name in
                       ['NBVL', 'NBV', 'BV', 'IBVL', 'IBV', 'Isr', 'Vj', 'M', 'NR', 'IKF', 'N', 'Is']]

    r_s = 45
    voltage = np.linspace(-15, 15, 100000)
    current = diode4(voltage, *parameters_list)
    v_r = r_s * current
    voltage_meas = voltage + v_r

    if not os.path.isdir('static'):
        os.mkdir('static')
    else:
        # Remove old plot files
        for filename_old in glob.glob(os.path.join('static', '*.png')):
            os.remove(filename_old)

    import base64
    fig_list = list()
    fig_list.append(base64.b64encode(plot_all(voltage_meas, current, fwd, -rev, mode='normal', filename='normal.png', show=False)))
    fig_list.append(base64.b64encode(plot_all(voltage_meas, current, fwd, -rev, mode='revlog', filename='revlog.png', show=False)))
    fig_list.append(base64.b64encode(plot_all(voltage_meas, current, fwd, -rev, mode='revlog_0.5', filename='revlog_0.5.png', show=False)))
    fig_list.append(base64.b64encode(plot_all(voltage_meas, current, fwd, -rev, mode='fwdlog', filename='fwdlog.png', show=False)))
    str_fig_list = list()
    for i in fig_list:
        str_fig_list.append(i.decode())
    return str_fig_list


if __name__ == '__main__':
    main()