from pathlib import Path
import csv, math, statistics, hashlib
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, Preformatted
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
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
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='TitleX',fontName='Times-Bold',fontSize=20,leading=24,spaceAfter=10))
styles.add(ParagraphStyle(name='BodyX',fontName='Times-Roman',fontSize=11,leading=14,spaceAfter=9))
styles.add(ParagraphStyle(name='HeadX',fontName='Times-Bold',fontSize=13,leading=16,spaceBefore=8,spaceAfter=8))
styles.add(ParagraphStyle(name='NoteX',fontName='Times-Roman',fontSize=9,leading=11,spaceAfter=7))
styles.add(ParagraphStyle(name='CodeX',fontName='Courier',fontSize=7,leading=9))
story=[]
def para(t,style='BodyX'):story.append(Paragraph(t,styles[style]))
para('Stata Group Assignment 1','TitleX')
para('Research Methods in Finance | Olin Business School','NoteX')
para('Operating-profitability decile portfolios','HeadX')
para('1. Data and portfolio selection','HeadX')
para('The analysis uses the ten <b>value-weighted</b> portfolios formed on operating profitability (OP) from Kenneth French\'s Data Library. Decile 1 contains the lowest-profitability stocks and decile 10 the highest. Portfolios are formed each June using NYSE breakpoints. OP is prior-year revenue minus cost of goods sold, interest expense, and selling, general and administrative expenses, divided by book equity.')
para('Monthly portfolio returns are matched by calendar month to RF from the Fama/French three-factor file. The common sample is <b>July 1963-July 2026 (757 months)</b>. Files were downloaded on September 15, 2026 and use the July 2026 CRSP database. All ten deciles and RF have complete observations in this sample. Only the monthly value-weighted return block is used.')
para('2. Excess returns and tests','HeadX')
para('For decile d in month t, excess return = portfolio return - RF. Both inputs are in percent per month, so an excess return of 0.69 denotes 0.69 percentage points. For each decile, the two-sided null is H<sub>0</sub>: mean excess return = 0. The statistic is t = mean / (s / sqrt(N)), where s is the sample standard deviation (N - 1 denominator). The p-value uses a Student t distribution with 756 degrees of freedom.')
para('3. Summary statistics and hypothesis tests','HeadX')
data=[['OP decile','N','Mean (%)','SD (%)','t statistic','p-value']]
for r in summary:
 d=int(r['decile']);label=f'{d}'+(' (low)' if d==1 else ' (high)' if d==10 else '')
 data.append([label,r['n'],f"{float(r['mean']):.4f}",f"{float(r['sd']):.4f}",f"{float(r['t']):.4f}",f"{float(r['p']):.7f}"])
table=Table(data,colWidths=[90,44,80,80,80,94],repeatRows=1)
table.setStyle(TableStyle([('FONTNAME',(0,0),(-1,0),'Times-Bold'),('FONTNAME',(0,1),(-1,-1),'Times-Roman'),('FONTSIZE',(0,0),(-1,-1),10),('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e8edf2')),('ALIGN',(1,0),(-1,-1),'RIGHT'),('BOTTOMPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),6),('LINEBELOW',(0,0),(-1,0),.7,colors.black),('LINEBELOW',(0,-1),(-1,-1),.7,colors.black)]))
story.append(table);story.append(Spacer(1,8))
para('Notes: Monthly arithmetic means and sample standard deviations; two-sided, unadjusted p-values. Calculations use Stata\'s one-sample ttest command. Source: Kenneth French Data Library.','NoteX')
story.append(PageBreak())
para('Discussion and time-series figure','TitleX')
para('All ten deciles have positive sample mean excess returns, ranging from 0.4394% to 0.7272% per month. At the 5% significance level, the zero-mean null is rejected for deciles 2-10. Decile 1 has t = 1.8327 and p = 0.0672, so it is not significant at 5%, although it is significant at 10%. Deciles 2-10 are also individually significant at 1%.')
para('Higher-profitability portfolios generally have larger mean excess returns, but the pattern is not monotonic: decile 8 has the highest mean (0.7272%), while decile 10 averages 0.6910%. Decile 1 is the most volatile (SD = 6.5959%), compared with 4.6210% for decile 10. The decile-10 minus decile-1 difference in sample means is about 0.252 percentage points per month. These individual tests do not establish that the difference itself is statistically significant.')
para('These are conventional one-sample t-tests. Their standard errors do not adjust for serial correlation, and the ten p-values are not corrected for multiple testing. Positive excess returns do not establish risk-adjusted abnormal performance or a causal effect of profitability; no asset-pricing factor adjustment is made.')
para('4. Highest-profitability decile over time','HeadX')
story.append(Image(str(root/'output/op_decile10.png'),width=504,height=302.4))
para('Figure 1. Decile 10 monthly excess returns fluctuate substantially around zero despite a positive sample mean. The largest negative observation is October 1987 (-25.17%). The plot shows monthly returns, not cumulative investment performance.','NoteX')
para('Sources and reproducibility','HeadX')
para('<link href="https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html" color="#154c79">Kenneth French Data Library</link>; <link href="https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/Data_Library/det_port_form_op.html" color="#154c79">operating-profitability portfolio definitions</link>. RF uses Ibbotson one-month Treasury bill data through May 2024 and the ICE BofA US 1-Month Treasury Bill Index thereafter, per the downloaded file. The library uses its current CIZ-based research return series.','NoteX')
para('The week-02 folder preserves the downloaded ZIP/CSV files, runnable assignment1.do, merged dataset, results table and graph. Set the Stata working directory to the repository root and run run-week-02.do. A local log is generated on each run. Row ranges refer to the preserved July 2026 files.','NoteX')
code=(root/'assignment1.do').read_text().splitlines()
# Preserve every line of the executed code, wrapping long comments for print only.
import textwrap
printed=[]
for line in code:
 if len(line)>106 and line.startswith('* '): printed.extend(textwrap.wrap(line,width=106,subsequent_indent='* '))
 else: printed.append(line)
for idx in range(0,len(printed),60):
 story.append(PageBreak());para('Appendix: Stata code'+(' (continued)' if idx else ''),'TitleX')
 story.append(Preformatted('\n'.join(printed[idx:idx+60]),styles['CodeX']))
def footer(canvas,doc):
 canvas.setFont('Times-Roman',9);canvas.setFillColor(colors.HexColor('#555555'));canvas.drawString(54,30,'Stata Group Assignment 1 | Operating profitability');canvas.drawRightString(558,30,str(doc.page))
SimpleDocTemplate(str(root/'output/pdf/assignment1_report.pdf'),pagesize=(612,792),rightMargin=54,leftMargin=54,topMargin=42,bottomMargin=45).build(story,onFirstPage=footer,onLaterPages=footer)
(root/'data/raw/SOURCE.txt').write_text('Downloaded 2026-09-15. CRSP vintage: 202607.\n'+ '\n'.join(f'{p.name}: SHA256 {hashlib.sha256(p.read_bytes()).hexdigest()}' for p in sorted((root/'data/raw').glob('*')) if p.suffix in ['.csv','.zip']))
import pypdfium2 as pdfium
pdf=pdfium.PdfDocument(str(root/'output/pdf/assignment1_report.pdf'))
for i,page in enumerate(pdf):page.render(scale=1.2).to_pil().save(str(root/f'tmp/pdfs/report_page_{i+1}.png'))
print('Report pages:',len(pdf))
