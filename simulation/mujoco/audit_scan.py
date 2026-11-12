from engine import *
from test_cases import CASES
import csv
def sectors(mask):
 if np.all(mask):return [('all',len(mask))]
 runs=[]
 for i in range(len(mask)):
  if mask[i] and not mask[(i-1)%len(mask)]:
   j=i
   while mask[(j+1)%len(mask)]:j=(j+1)%len(mask)
   runs.append((i,j))
 return runs
def names(model,ids):return np.array([model.geom(int(i)).name if i>=0 else 'no_hit' for i in ids])
if __name__=='__main__':
 out=ROOT/'results';out.mkdir(exist_ok=True);s=Sim();s.reset({})
 m=s.m;d=s.d;baseline=set(('burger_frame','tire_left','tire_right'))
 geomgroups=m.geom_group.copy()
 for i in range(m.ngeom):
  if m.geom_group[i]==2 and m.geom(i).name not in baseline:m.geom_group[i]=1
 ids0,ref,vec=s.lasers();bare=names(m,ids0);assert np.all(np.char.startswith(bare,'wall_')),np.unique(bare)
 origin=d.site_xpos[m.site('laser_origin').id];vals=np.minimum(np.where(vec[:,0]>1e-9,(2-origin[0])/np.maximum(vec[:,0],1e-10),(-2-origin[0])/np.minimum(vec[:,0],-1e-10)),np.where(vec[:,1]>1e-9,(2-origin[1])/np.maximum(vec[:,1],1e-10),(-2-origin[1])/np.minimum(vec[:,1],-1e-10)))
 wall_error=float(np.max(np.abs(ref-vals)));assert wall_error<.0001,wall_error
 m.geom_group[:]=geomgroups;ids,dist,dirs=s.lasers();tags=names(m,ids)
 mask=np.char.startswith(tags,'R4_post');assert mask.sum()>0 and np.all(dist[mask]<.16)
 with (out/'lidar_360.csv').open('w',newline='') as h:
  w=csv.writer(h);w.writerow(['azimuth_deg','bare_wall_m','R4_first_hit_m','R4_first_geom','valid_LDS02_range','wall_hidden'])
  for i in range(360):w.writerow([i,round(ref[i],5),round(dist[i],5),tags[i],.16<=dist[i]<=8.,not tags[i].startswith('wall_')])
 detail={str(k):{'azimuth_deg':np.flatnonzero(tags==k).tolist(),'nearest_mm':round(min(dist[tags==k])*1000,2)} for k in np.unique(tags[mask])}
 rows=[]
 for case in CASES:
  if case['id'] in ['positive_control','balls_disabled','balls_and_cups_disabled','edge_30mm','edge_80mm','edge_120mm']:continue
  path=out/(case['id']+'_poses.npz')
  if not path.exists():continue
  s.reset(case);poses=np.load(path)['qpos']
  for frame in range(0,len(poses),5):
   d.qpos[:]=poses[frame];mj.mj_forward(m,d)
   ids,rng,_=s.lasers();hits=names(m,ids)
   posts=np.char.startswith(hits,'R4_post');external=np.array([z.startswith('wall_') or z in ('floor','step','approach_deck','no_hit') for z in hits])
   notwalls=(~external);valid=notwalls&(rng>=.16)&(rng<=8.)
   rows.append(dict(case=case['id'],t=round((frame+1)*.04,2),self_hit=int(notwalls.sum()),post=int(posts.sum()),other_self=int((notwalls&~posts).sum()),valid_self_echo=int(valid.sum())))
 with (out/'lidar_5Hz.csv').open('w',newline='') as h:
  w=csv.DictWriter(h,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
 audits=dict(version=mj.__version__,actuators=[m.actuator(int(x)).name for x in s.motor],sensors=[m.sensor(i).name for i in range(m.nsensor)],freejoint=str(m.joint('floating_base').type[0]),r4_beams=int(mask.sum()),pct=round(mask.mean()*100,2),sectors=detail,calibration_wall_max_abs_error_mm=round(wall_error*1000,5),cases={c:{k:[min(t[k] for t in rows if t['case']==c),max(t[k] for t in rows if t['case']==c)] for k in ['self_hit','post','other_self','valid_self_echo']} for c in sorted(set(t['case'] for t in rows))})
 (out/'lidar_audit.json').write_text(json.dumps(audits,ensure_ascii=False,indent=2));print(json.dumps(audits,ensure_ascii=False))
