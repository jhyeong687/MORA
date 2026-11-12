"""A* over the actual SLAM occupancy grid plus explicit table keep-out priors."""
import heapq
import math
import numpy as np
from scipy.ndimage import distance_transform_edt


def plan_grid(message,start,goal,table_rectangles=(),radius=.18):
    grid=np.asarray(message.data).reshape(message.info.height,message.info.width)
    res=message.info.resolution
    origin=np.array([message.info.origin.position.x,message.info.origin.position.y])
    blocked=(grid<0)|(grid>=65)
    ys,xs=np.mgrid[:grid.shape[0],:grid.shape[1]]
    xx=origin[0]+(xs+.5)*res;yy=origin[1]+(ys+.5)*res
    for cx,cy,w,h in table_rectangles:
        blocked|=(np.abs(xx-cx)<w/2)&(np.abs(yy-cy)<h/2)
    blocked=distance_transform_edt(~blocked)*res < radius
    def cell(p):
        col,row=np.floor((np.asarray(p)-origin)/res).astype(int)
        return int(row),int(col)
    def point(c):return (origin+np.array([c[1]+.5,c[0]+.5])*res).tolist()
    begin,end=cell(start),cell(goal)
    def valid(c):return 0<=c[0]<grid.shape[0] and 0<=c[1]<grid.shape[1] and not blocked[c]
    if not valid(begin):raise RuntimeError(f'SLAM start cell is unknown or inflated: {start}')
    if not valid(end):raise RuntimeError(f'SLAM goal cell is unknown or inflated: {goal}')
    queue=[(0.0,begin)];cost={begin:0.0};parent={}
    moves=[(i,j) for i in [-1,0,1] for j in [-1,0,1] if i or j]
    while queue:
        _,here=heapq.heappop(queue)
        if here==end:break
        for dr,dc in moves:
            nxt=(here[0]+dr,here[1]+dc)
            if not valid(nxt):continue
            if dr and dc and (not valid((here[0]+dr,here[1])) or not valid((here[0],here[1]+dc))):continue
            total=cost[here]+math.hypot(dr,dc)
            if total<cost.get(nxt,float('inf')):
                cost[nxt]=total;parent[nxt]=here
                heapq.heappush(queue,(total+math.dist(nxt,end),nxt))
    if end not in cost:raise RuntimeError('No collision-free route in the observed SLAM map')
    path=[end]
    while path[-1]!=begin:path.append(parent[path[-1]])
    path.reverse()
    def visible(a,b):
        count=max(abs(a[0]-b[0]),abs(a[1]-b[1]))*3+1
        return all(valid((int(round(r)),int(round(c)))) for r,c in zip(np.linspace(a[0],b[0],count),np.linspace(a[1],b[1],count)))
    simplified=[path[0]];i=0
    while i<len(path)-1:
        j=len(path)-1
        while j>i+1 and not visible(path[i],path[j]):j-=1
        simplified.append(path[j]);i=j
    return [point(c) for c in simplified[1:]]+[list(goal)]
