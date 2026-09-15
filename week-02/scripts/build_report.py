from pathlib import Path
import csv, math, statistics
root=Path(__file__).resolve().parents[1]
(root/"tmp/pdfs").mkdir(parents=True, exist_ok=True)
p=(root/'data/raw/Portfolios_Formed_on_OP.csv').read_text().splitlines()[25:782]
f=(root/'data/raw/F-F_Research_Data_Factors.csv').read_text().splitlines()[5:1206]
rf={r[0]:float(r[4]) for r in csv.reader(f)}
raw=list(csv.reader(p));a=[[float(v)-rf[r[0]] for v in r[9:19]] for r in raw]
summary=list(csv.DictReader(open(root/'output/summary_statistics.csv')))
for j,r in enumerate(summary):
 x=[row[j] for row in a];m=statistics.mean(x);sd=statistics.stdev(x);tv=m/(sd/math.sqrt(len(x)))
 df=len(x)-1;c=math.exp(math.lgamma((df+1)/2)-math.lgamma(df/2))/math.sqrt(df*math.pi)
 steps=10000;h=abs(tv)/steps
 density=lambda z:c*(1+z*z/df)**(-(df+1)/2)
 integral=h/3*(density(0)+density(abs(tv))+sum((4 if k%2 else 2)*density(k*h) for k in range(1,steps)))
 pv=1-2*integral
 for val,k in zip([m,sd,tv,pv],['mean','sd','t','p']):
  assert math.isclose(val,float(r[k]),rel_tol=1e-6,abs_tol=1e-7),(j,k,val,r[k])
print('PASS: all 40 statistics independently verified from raw data.')
minidx=min(range(len(a)),key=lambda i:a[i][9]);maxidx=max(range(len(a)),key=lambda i:a[i][9])
print('Decile 10 extremes:',raw[minidx][0],a[minidx][9],raw[maxidx][0],a[maxidx][9])

# Generate display inputs from the verified Stata outputs.
import shutil, subprocess
report = root / 'report'
rows = []
for r in summary:
    d = int(r['decile'])
    label = str(d) + (' (lowest)' if d == 1 else ' (highest)' if d == 10 else '')
    rows.append(label + ' & ' + ' & '.join(f"{float(r[k]):.4f}" for k in ['mean','sd','t']) + ' & ' + f"{float(r['p']):.7f}" + ' ' + chr(92)*2)
(report/'results.tex').write_text('\n'.join(rows)+'\n')
with (root/'output/op_excess_returns.csv').open() as f:
    observations = list(csv.DictReader(f))
plot = ['year excess']
for row in observations:
    date = int(row['yyyymm'])
    plot.append(f"{date//100 + (date%100-1)/12:.6f} {row['excess10']}")
(report/'decile10.dat').write_text('\n'.join(plot)+'\n')
latexmk = shutil.which('latexmk')
if not latexmk and Path('/Library/TeX/texbin/latexmk').exists():
    latexmk = '/Library/TeX/texbin/latexmk'
if not latexmk:
    raise SystemExit('Install a TeX distribution with latexmk, then rerun.')
import os
build = root/'tmp/latex'
build.mkdir(parents=True, exist_ok=True)
env = os.environ.copy()
env['PATH'] = str(Path(latexmk).parent) + os.pathsep + env.get('PATH','')
subprocess.run([latexmk, '-pdf', '-interaction=nonstopmode', '-halt-on-error',
                '-outdir='+str(build), 'report.tex'], cwd=report, env=env, check=True)
shutil.copy2(build/'report.pdf', root/'output/pdf/assignment1_report.pdf')
print('Built output/pdf/assignment1_report.pdf')
