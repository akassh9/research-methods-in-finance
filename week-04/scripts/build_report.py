from pathlib import Path
import csv, math, json, hashlib, textwrap
import numpy as np
def t_pvalue(t, df):
    z=abs(float(t)); n=20000; h=z/n
    c=math.exp(math.lgamma((df+1)/2)-math.lgamma(df/2))/math.sqrt(df*math.pi)
    v=np.linspace(0,z,n+1); density=c*(1+v*v/df)**(-(df+1)/2)
    integral=h/3*(density[0]+density[-1]+4*density[1:-1:2].sum()+2*density[2:-1:2].sum())
    return 1-2*integral
from pypdf import PdfReader
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, Preformatted
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors
import pypdfium2 as pdfium
root=Path(__file__).resolve().parents[1]
rows=list(csv.DictReader(open(root/'output/industry_data.csv')))
y=np.array([float(r['dividend_yield']) for r in rows]); x=np.array([float(r['debt_capital']) for r in rows]); beta=np.array([float(r['market_beta']) for r in rows]); growth=np.array([float(r['eps_growth']) for r in rows])
coef=list(csv.DictReader(open(root/'output/coefficients.csv'))); modelstats={r['model']:r for r in csv.DictReader(open(root/'output/model_statistics.csv'))}
verified={}
for model,cols in [('linear',[x]),('quadratic',[x,x*x]),('cubic',[x,x*x,x*x*x]),('multiple',[x,beta,growth])]:
 X=np.column_stack(cols+[np.ones(len(y))]); b=np.linalg.lstsq(X,y,rcond=None)[0]; resid=y-X@b; df=len(y)-X.shape[1]; sse=resid@resid
 se=np.sqrt(np.diag(np.linalg.inv(X.T@X))*sse/df); t=b/se; p=np.array([t_pvalue(v,df) for v in t]); r2=1-sse/((y-y.mean())@(y-y.mean()))
 rr=[r for r in coef if r['model']==model]
 for i,r in enumerate(rr):
  for k,v in [('coefficient',b[i]),('se',se[i]),('t',t[i]),('p',p[i])]: assert math.isclose(float(r[k]),v,rel_tol=2e-6,abs_tol=1e-8),(model,k)
 assert math.isclose(float(modelstats[model]['r2']),r2,abs_tol=1e-7)
 verified[model]={'sse':sse,'df':df,'r2':r2}
print('PASS: independently verified all coefficients, SEs, t statistics, p values and R-squared values.')
# Verify joined input values against each preserved raw worksheet export.
for f,col,var,start in [('divfund',5,'dividend_yield',9),('dbtfund',5,'debt_capital',9),('betas',2,'market_beta',11),('pedata',8,'eps_growth',9)]:
 raw=list(csv.reader(open(root/f'data/{f}_raw.csv'))); lookup={r[0].strip():r[col] for r in raw[start:]}
 for r in rows: assert math.isclose(float(r[var]),float(lookup[r['industry']])*(1 if var=='market_beta' else 100),rel_tol=1e-12,abs_tol=1e-12)
print('PASS: all 364 analysis inputs agree with raw source exports.')
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='HeaderA',fontName='Times-Bold',fontSize=14,leading=17,alignment=TA_CENTER))
styles.add(ParagraphStyle(name='BodyA',fontName='Times-Roman',fontSize=12,leading=15,spaceAfter=10))
styles.add(ParagraphStyle(name='QuestionA',parent=styles['BodyA'],leftIndent=-15,spaceBefore=8))
styles.add(ParagraphStyle(name='NoteA',fontName='Times-Roman',fontSize=10,leading=12,spaceAfter=8))
styles.add(ParagraphStyle(name='TableA',fontName='Times-Roman',fontSize=11,leading=13,spaceAfter=0))
styles.add(ParagraphStyle(name='EquationA',parent=styles['BodyA'],alignment=TA_CENTER))
styles.add(ParagraphStyle(name='CodeA',fontName='Times-Roman',fontSize=10,leading=13))
story=[]
def p(t,s='BodyA'): story.append(Paragraph(t,styles[s]))
def question(n,t): p(f'{n}. {t}','QuestionA')
def table(data,widths):
 data=[[Paragraph(str(v),styles['TableA']) for v in r] for r in data]
 t=Table(data,colWidths=widths,repeatRows=1)
 t.setStyle(TableStyle([('GRID',(0,0),(-1,-1),.5,colors.black),('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),3)]));story.append(t);story.append(Spacer(1,10))
p('Department of Finance<br/>Olin Business School<br/>Washington University in St. Louis<br/>Research Methods in Finance','HeaderA'); story.append(Spacer(1,15)); p('Stata Group Assignment 3 - Group 10','HeaderA'); story.append(Spacer(1,22))
question(1,'Download industry-level data for the dividend yield or dividend payout ratio for the United States, Europe, Japan, or Emerging Markets from the current data page on Aswath Damodaran\'s website. Also download industry-level data for the debt-to-capital ratio, market beta, and expected growth in earnings per share (EPS) over the next five years for the same country or country group.')
p('We selected <b>United States industries</b> and <b>dividend yield</b>. The four source workbooks are dated January 5, 2026 and were downloaded on September 29, 2026. Industries are matched by name, with each industry receiving equal weight.')
p('- Dividend yield: total dividends / market capitalization of equity (divfund.xls).<br/>- Debt-to-capital: market debt-to-capital, adjusted for leases (dbtfund.xls).<br/>- Market beta: levered Beta column (betas.xls).<br/>- Expected EPS growth: expected annual growth over the next five years (pedata.xls).')
p('The matched data contain 94 industries. We exclude the two aggregate Total Market rows and use a common sample of <b>91 industries</b> for all regressions. Chemical (Diversified), Real Estate (General/Diversified), and Reinsurance lack EPS-growth forecasts and are omitted. Yield, debt-to-capital, and growth are measured in percentage points; beta is unitless. No outliers are removed.')
question(2,'Estimate a linear regression with the dividend yield or dividend payout ratio (debt-to-capital ratio) serving as the dependent (explanatory) variable. In addition, estimate quadratic and cubic regression specifications. Do you find evidence of nonlinearities in the relationship between the dividend yield or dividend payout ratio and the debt-to-capital ratio? Create a scatterplot for the dependent and explanatory variables that includes the fitted linear, quadratic, and cubic regressions.')
story.append(PageBreak())
p('Question 2 (continued)')
p('Let Y be dividend yield (%) and D be debt-to-capital (%). The fitted OLS equations are:')
p('Linear: Y = 0.91860 + 0.02636D<br/>Quadratic: Y = -0.17621 + 0.11728D - 0.001359D<super>2</super><br/>Cubic: Y = 0.36860 + 0.04223D + 0.001153D<super>2</super> - 0.00002251D<super>3</super>')
table([['Specification','N','R-squared','Adjusted R-squared']]+[[m.capitalize(),'91',f"{float(modelstats[m]['r2']):.4f}",f"{float(modelstats[m]['adj_r2']):.4f}"] for m in ['linear','quadratic','cubic']],[145,45,125,145])
story.append(Image(str(root/'output/dividend_debt_fits.png'),width=460,height=276));story.append(Spacer(1,12))
p('Figure 1. Dividend yield against lease-adjusted market debt-to-capital for 91 U.S. industries, with fitted linear, quadratic, and cubic OLS regressions. Source: Aswath Damodaran, January 2026 industry data.','NoteA')
story.append(PageBreak())
p('Question 2 (continued)')
p('There is evidence of <b>nonlinearity</b>. In the quadratic model, the squared-debt coefficient is negative and statistically significant (t = -3.7862; p = 0.000279). Testing the squared term gives F(1, 88) = 14.34. R-squared increases from 0.1024 in the linear model to 0.2281 in the quadratic model.')
p('The quadratic fit has an inverted-U shape: dividend yield rises with debt-to-capital up to roughly <b>43.15%</b>, then declines. This turning point is computed as -0.117283 / (2 x -0.00135898). It describes the fitted cross-sectional relationship; it is not an optimal debt ratio or evidence that changing leverage causes dividend yield to change.')
p('The cubic model raises R-squared only modestly, to 0.2435. Its cubic term is not significant (t = -1.3299; p = 0.1870; F(1, 87) = 1.77). A joint test of the squared and cubic terms rejects a purely linear relationship (F(2, 87) = 8.11; p = 0.0006), but there is no strong evidence that the cubic term adds to the quadratic specification. The quadratic model therefore provides the more parsimonious description of the curvature.')
p('All tests use conventional OLS standard errors. Polynomial predictions are interpreted only within the observed debt-to-capital range; the sparse high-debt observations can influence the fitted curvature.')
story.append(PageBreak())
question(3,'Estimate a multiple linear regression with the dividend yield or dividend payout ratio serving as the dependent variable and the debt-to-capital ratio, market beta, and expected earnings growth serving as the explanatory variables. Report the results (coefficient estimates, standard errors, t-statistics, R-squared statistic) in a table. Discuss the results.')
p('We estimate Y = a + b<sub>1</sub>D + b<sub>2</sub>Beta + b<sub>3</sub>Growth + error using the same 91 industries. The following table reports conventional OLS standard errors.')
labels={'debt_capital':'Debt-to-capital (%)','market_beta':'Market beta','eps_growth':'Expected EPS growth (%)','_cons':'Constant'}
table([['Variable','Coefficient','Standard error','t-statistic','p-value']]+[[labels[r['term']],f"{float(r['coefficient']):.6f}",f"{float(r['se']):.6f}",f"{float(r['t']):.4f}",f"{float(r['p']):.6f}"] for r in coef if r['model']=='multiple'],[140,83,88,75,74])
p('<b>N = 91; R-squared = 0.2157; adjusted R-squared = 0.1887.</b> The overall regression is significant: F(3, 87) = 7.98, p = 0.0001.')
p('Holding beta and expected growth constant, a 10-percentage-point increase in debt-to-capital is associated with a <b>0.1620-percentage-point increase</b> in dividend yield. This coefficient is significant at 10% but not 5% (p = 0.0565). Its size and significance are lower than in the simple linear regression.')
p('Market beta is negatively associated with dividend yield. A one-unit increase in beta is associated with a <b>1.7528-percentage-point decrease</b> in yield, holding the other variables constant (p = 0.000636). This is consistent with higher market-risk industries tending to pay lower dividend yields, although the regression does not establish a causal explanation.')
p('The expected EPS-growth coefficient is small and positive: a 10-percentage-point increase in expected growth is associated with a 0.0604-percentage-point increase in yield. It is not statistically significant (p = 0.4895), so the sample provides no clear evidence of a conditional growth-yield relationship.')
p('The model explains about 21.6% of the cross-industry variation in dividend yield. Most variation remains unexplained. These are industry-level associations, not firm-level causal estimates. The multiple model is linear as requested; the curvature found in Question 2 suggests a possible limitation of this specification.')
p('Source: <link href="https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datacurrent.html" color="#aa0000">Aswath Damodaran current data page</link>. Original XLS files, analysis datasets, regression tables, graph, and executed Stata log are preserved with the runnable do-file.')
story.append(PageBreak())
question(4,'Provide the Stata code in an appendix.')
p('Appendix: Stata code')
p('The complete executed do-file follows. Run it from the week-04 folder. The original XLS workbooks must remain in the data subfolder.')
code=(root/'assignment3.do').read_text().splitlines()
wrapped=[]
for line in code:
 if len(line)>93:
  if line.startswith('*'): wrapped+=textwrap.wrap(line,93,subsequent_indent='* ')
  else:
   # Printed continuation preserves Stata syntax when copied.
   parts=textwrap.wrap(line,width=88,break_long_words=False,break_on_hyphens=False,replace_whitespace=False)
   wrapped += [part+' ///' for part in parts[:-1]]+[parts[-1]]
 else: wrapped.append(line)
story.append(Preformatted('\n'.join(wrapped),styles['CodeA']))
out=root/'output/pdf/assignment3_report.pdf'
SimpleDocTemplate(str(out),pagesize=(612,792),leftMargin=76,rightMargin=76,topMargin=55,bottomMargin=50).build(story)
pdf=pdfium.PdfDocument(str(out))
for i,page in enumerate(pdf):page.render(scale=1.2).to_pil().save(str(root/f'tmp/report_page_{i+1}.png'))
print('PDF pages',len(pdf))
(root/'output/verification.txt').write_text('All four model outputs independently verified using NumPy and numerical Student-t integration.\nAll 364 joined input values verified against preserved Stata raw exports.\n')
(root/'data/SOURCE.txt').write_text('Downloaded 2026-09-29; workbook update dates 2026-01-05.\nSource: https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datacurrent.html\n'+ '\n'.join('https://pages.stern.nyu.edu/~adamodar/pc/datasets/'+f+'\nSHA256 '+hashlib.sha256((root/'data'/f).read_bytes()).hexdigest() for f in ['divfund.xls','dbtfund.xls','betas.xls','pedata.xls']))
