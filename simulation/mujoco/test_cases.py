"""Scenarios. SI units, seconds. 100 g is rigidly fixed at TCP, not a grasp simulation."""
CASES=[
 dict(id='flat_drive',mode='drive',duration=7),
 dict(id='stow_brake',mode='drive',speed=.18,brake_time=.04,duration=7),
 dict(id='tight_turn',mode='turn',yaw=1.8,speed=.035,duration=7),
 dict(id='pick_empty',mode='pick',duration=11.5),
 dict(id='pick_100g',mode='pick',load=.1,duration=11.5),
 dict(id='extend_100g',mode='extend',load=.1,duration=8),
 dict(id='downhill_brake',mode='extbrake',slope=3,load=.1,duration=9),
 dict(id='downhill_estop',mode='extbrake',slope=3,load=.1,brake_time=.02,duration=9),
 dict(id='side_reach',mode='extend',slope=3,downhill=90,load=.1,q_deg=[-90,74,-69,0,0,10.5],duration=8),
 dict(id='step_10mm',mode='drive',speed=.15,step_height=.010,step_x=.29,duration=8),
 dict(id='step_20mm',mode='drive',speed=.15,step_height=.020,step_x=.29,duration=8),
 dict(id='edge_30mm',mode='drive',speed=.15,drop=.030,duration=8),
 dict(id='edge_80mm',mode='drive',speed=.15,drop=.080,duration=8),
 dict(id='edge_120mm',mode='drive',speed=.15,drop=.120,duration=8),
 dict(id='balls_disabled',mode='extbrake',load=.1,slope=3,guards=False,duration=9),
 dict(id='balls_and_cups_disabled',mode='extbrake',load=.1,slope=3,guards=False,housings=False,duration=9),
 dict(id='positive_control',mode='control',pulse_nm=7.5,load=.1,duration=8)]
def variants():
 import itertools
 for c in CASES:yield c
 for slope,mu,gap,shift in itertools.product((0,3,5),(.4,.85),(.0005,.003),(-1,1)):
  yield dict(id=f'sweep_s{slope}_mu{mu}_gap{gap}_cg{shift}',mode='extbrake',load=.1,slope=slope,mu=mu,gap=gap,cg_shift=[shift*.015,shift*.012,.020],brake_time=.06,duration=9)
 for voltage,cap in [(7.4,False),(7.4,True),(12,True)]:
  yield dict(id=f'servo_{voltage}_{cap}',mode='extbrake',load=.1,slope=3,arm_voltage=voltage,rated_cap=cap,duration=9)
 for h in [.0005,.0015,.003]:
  yield dict(id=f'front_ball_gap_{h}',mode='extbrake',load=.1,slope=3,gap=h,duration=9)
 for dt in [.001,.0005]:
  for base in ('flat_drive','downhill_brake','step_10mm','edge_80mm','positive_control'):
   c=next(c for c in CASES if c['id']==base)
   yield {**c,'id':f"convergence_{base}_{dt}",'dt':dt}
