"""Independently verify Stata OLS against raw CSVs, then build the PDF."""
from pathlib import Path
import csv
import math
import os
import shutil
import subprocess
import numpy as np

root = Path(__file__).resolve().parents[1]
raw = list(csv.reader((root/'data/raw/Portfolios_Formed_on_OP.csv').read_text().splitlines()[25:782]))
factors = {r[0]: (float(r[1]), float(r[4])) for r in csv.reader(
    (root/'data/raw/F-F_Research_Data_Factors.csv').read_text().splitlines()[5:1206])}
rows = list(csv.DictReader((root/'output/capm_results.csv').open()))
hacrows = list(csv.DictReader((root/'output/capm_hac_results.csv').open()))
assert len(hacrows) == 10
assert len(rows) == 10 and len(raw) == 757
x = [factors[r[0]][0] for r in raw]
n = len(x)
xbar = sum(x)/n
sxx = sum((v-xbar)**2 for v in x)
df = n-2

def two_sided_p(t):
    # Direct Simpson integration of both Student-t tails (100 extra units
    # makes the omitted tail negligible for df=755).
    lo = abs(t)
    steps = 20000
    h = 100/steps
    c = math.exp(math.lgamma((df+1)/2)-math.lgamma(df/2))/math.sqrt(df*math.pi)
    def density(z):
        return c*(1+z*z/df)**(-(df+1)/2)
    return 2*h/3*(density(lo)+density(lo+100)+sum(
        (4 if k%2 else 2)*density(lo+k*h) for k in range(1,steps)))

for j, row in enumerate(rows):
    assert int(row['decile']) == j+1 and int(row['n']) == n
    y = [float(r[j+9])-factors[r[0]][1] for r in raw]
    ybar = sum(y)/n
    beta = sum((a-xbar)*(b-ybar) for a,b in zip(x,y))/sxx
    alpha = ybar-beta*xbar
    sse = sum((b-alpha-beta*a)**2 for a,b in zip(x,y))
    # Original normal-theory BP test: half the explained sum of squares
    # from regressing squared residuals/(SSE/N) on an intercept and market.
    scaled_sq = [(b-alpha-beta*a)**2/(sse/n) for a,b in zip(x,y)]
    slope_sq = sum((a-xbar)*(v-1) for a,v in zip(x,scaled_sq))/sxx
    bp = slope_sq*slope_sq*sxx/2
    bpp = math.erfc(math.sqrt(bp/2))
    seb = math.sqrt(sse/df/sxx)
    sea = math.sqrt(sse/df*(1/n+xbar*xbar/sxx))
    t1 = (beta-1)/seb
    p1 = two_sided_p(t1)
    values = dict(alpha=alpha,se_alpha=sea,t_alpha=alpha/sea,
                  beta=beta,se_beta=seb,t_beta=beta/seb,
                  r2=1-sse/sum((v-ybar)**2 for v in y),t_beta1=t1,p_beta1=p1,bp_chi2=bp,bp_p=bpp)
    for key,value in values.items():
        assert math.isclose(value,float(row[key]),rel_tol=2e-6,abs_tol=1e-8), (j+1,key,value,row[key])
    # BG LM = N*R-squared, zero-filling initial lagged residuals,
    # matching Stata's default auxiliary-regression convention.
    X = np.column_stack([np.ones(n), x])
    resid = np.array(y)-X@np.array([alpha,beta])
    lagged = np.column_stack([np.r_[np.zeros(k),resid[:-k]] for k in range(1,13)])
    Z = np.column_stack([X,lagged])
    aux_resid = resid-Z@np.linalg.lstsq(Z,resid,rcond=None)[0]
    bg = n*(1-float(aux_resid@aux_resid)/float(resid@resid))
    bgp = math.exp(-bg/2)*sum((bg/2)**k/math.factorial(k) for k in range(6))
    for key,value in [('bg_chi2',bg),('bg_p',bgp)]:
        assert math.isclose(value,float(row[key]),rel_tol=2e-6,abs_tol=1e-8), (j+1,key,value,row[key])
    # Newey-West Bartlett weights through lag 12 and Stata's N/(N-K).
    scores = X*resid[:,None]
    meat = scores.T@scores
    for lag in range(1,13):
        cross = scores[lag:].T@scores[:-lag]
        meat += (1-lag/13)*(cross+cross.T)
    bread = np.linalg.inv(X.T@X)
    cov = (n/df)*bread@meat@bread
    hsea,hseb = np.sqrt(np.diag(cov))
    ht = (beta-1)/hseb
    hp = two_sided_p(ht)
    hr = hacrows[j]
    hvals = dict(alpha=alpha,beta=beta,se_alpha=hsea,se_beta=hseb,
                 t_alpha=alpha/hsea,t_beta=beta/hseb,r2=values['r2'],t_beta1=ht,p_beta1=hp)
    assert int(hr['n']) == n and int(hr['decile']) == j+1
    for key,value in hvals.items():
        assert math.isclose(value,float(hr[key]),rel_tol=2e-6,abs_tol=1e-8), (j+1,key,value,hr[key])
    hcategory = ('Cyclical' if beta>1 else 'Defensive') if hp<.05 else 'Not distinguish.'
    assert hr['classification'] == hcategory
    category = ('Cyclical'  if beta>1 else 'Defensive') if p1<.05 else 'Not distinguish.'
    assert row['classification'] == category
print('PASS: all 220 OLS, diagnostic and HAC statistics and 20 classifications independently verified.')

# Also check all excess returns and matched market returns in the Stata data.
obs = list(csv.DictReader((root/'output/op_excess_returns.csv').open()))
assert len(obs) == n
for r,o in zip(raw,obs):
    assert r[0] == o['yyyymm']
    assert math.isclose(float(o['market']),factors[r[0]][0],abs_tol=1e-6)
    for j in range(10):
        assert math.isclose(float(o[f'excess{j+1}']),float(r[j+9])-factors[r[0]][1],abs_tol=5e-6)
print('PASS: all 7,570 monthly excess returns and matched market returns verified.')

report = root/'report'
end = ' '+chr(92)*2
(report/'regressions.tex').write_text('\n'.join(
    r['decile']+' & '+' & '.join(f"{float(r[k]):.4f}" for k in
    ['alpha','se_alpha','t_alpha','beta','se_beta','t_beta','r2'])+end for r in rows)+'\n')
(report/'tests.tex').write_text('\n'.join(
    r['decile']+' & '+f"{float(r['beta']):.4f} & {float(r['t_beta1']):.4f} & "+
    ('$<0.0001$' if float(r['p_beta1'])<.0001 else f"{float(r['p_beta1']):.4f}")+
    ' & '+('Not distinguishable from 1' if r['classification']=='Not distinguish.' else r['classification'])+end
    for r in rows)+'\n')
(report/'heteroskedasticity.tex').write_text('\n'.join(
    r['decile']+' & '+f"{float(r['bp_chi2']):.4f} & {float(r['bp_p']):.4f}"+
    ' & '+('Reject constant variance' if float(r['bp_p'])<.05 else 'Do not reject')+end
    for r in rows)+'\n')
(report/'diagnostics.tex').write_text('\n'.join(
    r['decile']+' & '+' & '.join(f"{float(r[k]):.4f}" for k in
    ['bp_chi2','bp_p','bg_chi2','bg_p'])+end for r in rows)+'\n')
(report/'hac_regressions.tex').write_text('\n'.join(
    r['decile']+' & '+' & '.join(f"{float(r[k]):.4f}" for k in
    ['alpha','se_alpha','t_alpha','beta','se_beta','t_beta','r2'])+end for r in hacrows)+'\n')
(report/'hac_tests.tex').write_text('\n'.join(
    r['decile']+' & '+f"{float(r['t_beta1']):.4f} & "+
    ('$<0.0001$' if float(r['p_beta1'])<.0001 else f"{float(r['p_beta1']):.4f}")+
    ' & '+('Not distinguishable from 1' if r['classification']=='Not distinguish.' else r['classification'])+end
    for r in hacrows)+'\n')
latexmk = shutil.which('latexmk') or '/Library/TeX/texbin/latexmk'
build = root/'tmp/latex'
build.mkdir(parents=True,exist_ok=True)
env = os.environ.copy()
env['PATH'] = str(Path(latexmk).parent)+os.pathsep+env.get('PATH','')
subprocess.run([latexmk,'-pdf','-interaction=nonstopmode','-halt-on-error',
                '-outdir='+str(build),'report.tex'],cwd=report,env=env,check=True,stdout=subprocess.DEVNULL)
shutil.copy2(build/'report.pdf',root/'output/pdf/assignment2_report.pdf')
print('Built output/pdf/assignment2_report.pdf')
