from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
import numpy as np,json,csv
B=Path(__file__).resolve().parent.parent/'docs/img/research'
B.mkdir(parents=True,exist_ok=True)
font=Path(__file__).resolve().parent.parent/'brand/Pretendard-Regular.otf'
font_manager.fontManager.addfont(str(font));plt.rcParams.update({'font.family':font_manager.FontProperties(fname=font).get_name(),'font.size':15,'axes.unicode_minus':False,'svg.fonttype':'path'})
import sys
dark='--dark' in sys.argv
green='#F3D66B';grey='#8A8073' if not dark else '#847B6E';ink='#23211E' if not dark else '#EDE7DB';paper='#FCFAF4' if not dark else '#221F1B'
suffix='-dark' if dark else ''
D={'kim_webb_2022':{'doi':'10.1111/lang.12479','source_location':'Results, pp. 288–289; spaced vs. massed','metric':'Hedges g','rows':[{'test':'학습 직후','estimate':.58,'lo':.16,'hi':1.00},{'test':'시간이 지난 뒤','estimate':.80,'lo':.44,'hi':1.17}]},'nakata_2021':{'doi':'10.1002/tesq.596','source_location':'Table 1, posttest; 3 weeks after last treatment','metric':'mean percent correct, unadjusted','noncumulative_n':33,'cumulative_n':34,'rows':[{'direction':'영어 → 뜻','group':'최근 단어만','mean':26.4,'lo':21.7,'hi':31.1},{'direction':'영어 → 뜻','group':'이전 단어도','mean':50.9,'lo':43.1,'hi':58.6},{'direction':'뜻 → 영어','group':'최근 단어만','mean':12.1,'lo':8.8,'hi':15.5},{'direction':'뜻 → 영어','group':'이전 단어도','mean':38.5,'lo':29.9,'hi':47.2}]}}
(B/'research-data.json').write_text(json.dumps(D,ensure_ascii=False,indent=2))
for name,info in D.items():
 with (B/(name+'.csv')).open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(info['rows'][0]),lineterminator='\n');w.writeheader();w.writerows(info['rows'])
def finish(fig,ax,name):
 fig.patch.set_facecolor(paper);ax.set_facecolor(paper)
 for sp in ax.spines.values():sp.set_visible(False)
 ax.tick_params(length=0,colors=ink,labelsize=13);ax.set_axisbelow(True);ax.grid(axis='x',color='#E6DECF' if not dark else '#302C27',lw=.8)
 fig.text(.12,.025,'출처: Kim & Webb (2022), pp. 288–289 · 단숙이 제작' if name=='spacing-effect' else '출처: Nakata 외 (2021), Table 1 · 단숙이 제작',fontsize=9,color=ink)
 fig.savefig(B/(name+suffix+'.png'),dpi=180,facecolor=paper);fig.savefig(B/(name+suffix+'.svg'),facecolor=paper,metadata={'Date':None})
 svg=B/(name+suffix+'.svg')
 svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
 plt.close(fig)
fig,ax=plt.subplots(figsize=(6.4,4.5));fig.subplots_adjust(left=.12,right=.96,bottom=.22,top=.94)
for i,r in enumerate(D['kim_webb_2022']['rows']):
 y=1-i;ax.errorbar(r['estimate'],y,xerr=[[r['estimate']-r['lo']],[r['hi']-r['estimate']]],fmt='o',color=ink,markerfacecolor=green,markersize=11,capsize=6,lw=2)
 ax.text(.02,y+.26,r['test'],fontsize=17,color=ink)
 ax.text(.02,y-.28,f"g = {r['estimate']:.2f}   ·   95% CI {r['lo']:.2f}–{r['hi']:.2f}",fontsize=13,color=ink)
ax.axvline(0,color=grey,lw=1);ax.set_yticks([]);ax.set_ylim(-.55,1.6);ax.set_xlim(0,1.4);ax.set_xticks([0,.4,.8,1.2]);ax.set_xlabel('몰아서 연습한 경우 대비 효과 크기 (Hedges’ g)',fontsize=13,labelpad=15)
finish(fig,ax,'spacing-effect')
fig,ax=plt.subplots(figsize=(6.4,6.5));fig.subplots_adjust(left=.12,right=.96,bottom=.17,top=.96)
for i,r in enumerate(D['nakata_2021']['rows']):
 y=[4.1,3.2,1.3,.4][i];color=grey if i%2==0 else green
 ax.barh(y,r['mean'],height=.4,color=color)
 ax.errorbar(r['mean'],y,xerr=[[r['mean']-r['lo']],[r['hi']-r['mean']]],fmt='none',ecolor=ink,capsize=4,lw=1.2)
 ax.text(0,y+.31,r['group'],fontsize=14,color=ink)
 ax.text(r['hi']+2,y,f"{r['mean']:.1f}%",va='center',fontsize=17,fontweight='bold',color=ink)
ax.text(0,4.98,'영어 → 뜻',fontsize=19,fontweight='bold',color=ink);ax.text(0,2.18,'뜻 → 영어',fontsize=19,fontweight='bold',color=ink)
ax.set_xlim(0,100);ax.set_ylim(-.35,5.45);ax.set_yticks([]);ax.set_xticks([0,25,50,75,100]);ax.set_xlabel('最後 학습 3주 뒤 평균 정답률 (%)'.replace('最後','마지막'),fontsize=14,labelpad=14)
finish(fig,ax,'cumulative-results')
print('Generated 2 charts as PNG/SVG, source JSON and 2 CSV files.')
