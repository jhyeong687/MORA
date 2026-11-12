#!/usr/bin/env python3
"""Independently check saved physical outcomes, not just scripted stage names."""
import argparse
import json
from pathlib import Path
import numpy as np


def main():
    parser=argparse.ArgumentParser();parser.add_argument('trial',type=Path);args=parser.parse_args()
    p=args.trial
    metrics=json.loads((p/'metrics.json').read_text())
    config=json.loads((p/'configuration.json').read_text())
    objects=json.loads((p/'object_evaluation.json').read_text())
    contacts=json.loads((p/'finger_contacts.json').read_text())
    arms=json.loads((p/'arm_samples.json').read_text())
    xyz=np.array([r['xyz'] for r in objects]);table=config['task']['tables'][1]
    final=xyz[-1];initial=xyz[0]
    cube=config['task']['object']['name'];size=np.array(config['task']['object']['size'])
    fingers={r['finger'] for r in contacts if any(cube in name for pair in r['pairs'] for name in pair)}
    checks={
        'script_completed':metrics['completed'],
        'object_lifted_at_least_5cm':float(xyz[:,2].max()-initial[2])>.05,
        'both_fingers_contacted_object':{'fixed','moving'}<=fingers,
        'object_moved_at_least_2m':float(np.linalg.norm(final[:2]-initial[:2]))>2,
        'object_inside_delivery_table_xy':bool(np.all(np.abs(final[:2]-np.array(table['center']))<(np.array(table['size'])-size[:2])*.5)),
        'object_at_tabletop_height':abs(float(final[2])-(table['top_height']+size[2]/2))<.015,
        'object_settled_speed_below_3cm_s':objects[-1]['speed']<.03,
        'gripper_open_after_release':bool(arms and arms[-1]['position'][5]>.20),
        'no_attachment_or_depth_or_learned_policy':not any(metrics[k] for k in ['grasp_attachment_used','depth_camera_used','learned_policy_used']),
    }
    output={'passed':all(checks.values()),'checks':checks,
        'object_initial_xyz_m':initial.tolist(),'object_final_xyz_m':final.tolist(),
        'maximum_object_height_m':float(xyz[:,2].max()),
        'horizontal_object_transfer_m':float(np.linalg.norm(final[:2]-initial[:2])),
        'final_object_speed_m_s':objects[-1]['speed'],
        'physical_observation_samples':len(objects),'saved_contact_samples':len(contacts),
        'scope':'One scripted simulated functional check. No learned policy or real hardware validation.'}
    (p/'verification.json').write_text(json.dumps(output,indent=2));print(json.dumps(output,indent=2))
    if not output['passed']:raise SystemExit(1)


if __name__=='__main__':main()
