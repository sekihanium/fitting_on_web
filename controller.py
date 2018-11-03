from model import InputForm
from flask import Flask, render_template, request
from compute import compute
from merge import merge_csv

app = Flask(__name__)
fwd, rev = merge_csv('measurement_csv')

@app.route('/vib1', methods=['GET', 'POST'])
def index():
    form = InputForm(request.form)
    if request.method == 'POST' and form.validate():
        diode_spice = dict(NBVL=float(form.NBVL.data),
                           NBV=float(form.NBV.data),
                           BV=float(form.BV.data),
                           IBVL=float(form.IBVL.data),
                           IBV=float(form.IBV.data),
                           Isr=float(form.Isr.data),
                           Vj=float(form.Vj.data),
                           M=float(form.M.data),
                           NR=float(form.NR.data),
                           IKF=float(form.IKF.data),
                           N=float(form.N.data),
                           Is=float(form.Is.data))
        result = compute(fwd, rev, diode_spice)
    else:
        result = None

    return render_template('view.html', form=form, result=result)


if __name__ == '__main__':
    app.run(debug=True)