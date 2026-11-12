from pathlib import Path
import json, numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
root=Path(__file__).resolve().parent/'results'/'research_20261112'
before=json.loads((root/'carry_navigation_01/metrics.json').read_text())
after=json.loads((root/'carry_navigation_calibrated_01/metrics.json').read_text())
out=root/'carry_calibration_selected';out.mkdir(exist_ok=True)
fig,axes=plt.subplots(1,2,figsize=(11,4.8));x=np.arange(3)
for ax,key,scale,title,unit in [(axes[0],'evaluation_position_error_m',100,'Actual arrival position error','cm'),(axes[1],'evaluation_heading_error_deg',1,'Absolute arrival heading error','deg')]:
    for offset,m,label,color in [(-.18,before,'Before','#b47738'),(.18,after,'After configuration update','#247d78')]:
        y=[abs(row[key])*scale for row in m['waypoints']]
        bars=ax.bar(x+offset,y,.36,label=label,color=color);ax.bar_label(bars,fmt='%.2f',padding=3,fontsize=9)
    ax.set_xticks(x,['Pickup standby','Transit','Delivery standby']);ax.set_ylabel(unit);ax.set_title(title);ax.grid(axis='y',alpha=.2);ax.set_axisbelow(True);ax.set_ylim(top=max(ax.get_ylim()[1]*1.15,1))
fig.suptitle('Carry waypoint validation | fixed 10 g payload | simulation only',fontsize=12)
handles,labels=axes[0].get_legend_handles_labels();fig.legend(handles,labels,loc='upper center',bbox_to_anchor=(.5,.91),ncol=2,fontsize=9)
fig.text(.5,.02,'One trial per configuration; combined SLAM/encoder/controller settings changed. No claim of statistical reliability or grasp success.',ha='center',fontsize=8)
fig.tight_layout(rect=(0,.065,1,.82));fig.savefig(out/'arrival_comparison.png',dpi=200);fig.savefig(out/'arrival_comparison.pdf')
(out/'comparison_data.json').write_text(json.dumps({'before_trial':'carry_navigation_01','after_trial':'carry_navigation_calibrated_01','before':before['waypoints'],'after':after['waypoints'],'note':'Descriptive comparison of combined settings changes, one trial each.'},indent=2))
print(out)
