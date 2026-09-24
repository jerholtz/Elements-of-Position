#!/usr/bin/env python3
"""Elements of Position - measure, draw, CAD view.
python eop_set_full.py --n-max 36 --out /home/workdir/artifacts/eop_set
"""
from __future__ import annotations
import argparse, csv, json, math
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch
import numpy as np

PHI = (1.0 + math.sqrt(5.0)) / 2.0
PHI_INV = PHI - 1.0
PI = math.pi
INK, DIM, A, B, CUT = "#1a1a1a", "#6b6b6b", "#2c3e50", "#8b3a3a", "#6b4c7a"
PAPER, RULE = "#f4f1ea", "#c8c2b4"

def is_fw(n):
    if n < 2: return False
    if n < 4: return True
    if n % 2 == 0: return False
    d = 3
    while d * d <= n:
        if n % d == 0: return False
        d += 2
    return True

def radii(n):
    R = n / 2.0
    return dict(n=n, R=R, inv=1.0/n, lock=1.0, mid=R/2.0, B1=R*PHI_INV,
                B2=R*PHI_INV**2, apo=R*math.cos(PI/n) if n>=2 else float("nan"),
                side=n*math.sin(PI/n) if n>=2 else float("nan"),
                two=n*math.sin(2*PI/n) if n>=3 else float("nan"),
                twocos=2.0*math.cos(PI/n) if n>=2 else float("nan"),
                half_walk=PI*R, is_fw=int(is_fw(n)))

def write_csv(n_max, path):
    rows = [radii(n) for n in range(1, n_max+1)]
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    return rows

def title(fig, code, name, note=""):
    fig.text(0.03,0.965,"ELEMENTS OF POSITION",fontsize=8,color=DIM)
    fig.text(0.03,0.932,code,fontsize=12,color=INK,fontweight="bold")
    fig.text(0.03,0.900,name,fontsize=9,color=INK)
    fig.text(0.97,0.965,"set",fontsize=7,color=DIM,ha="right")
    if note: fig.text(0.97,0.932,note,fontsize=7,color=DIM,ha="right")

def sheet():
    fig, ax = plt.subplots(figsize=(11,8.5), facecolor=PAPER)
    ax.set_facecolor(PAPER); return fig, ax

def bare(ax):
    ax.set_aspect("equal"); ax.axis("off")

def circ(ax,c,r,**k):
    ax.add_patch(Circle(c,r,fill=False,**k))

def ngon(n,R,rot=None):
    if rot is None: rot = PI/2
    th = np.linspace(0,2*PI,n+1)+rot
    return R*np.cos(th), R*np.sin(th)

def draw_web(ax,n,origin=(0,0)):
    r=radii(n); ox,oy=origin; R=r["R"]
    circ(ax,origin,R,edgecolor=INK,lw=1.15)
    if n>=3: circ(ax,origin,r["apo"],edgecolor="#4a6fa5",lw=0.7)
    circ(ax,origin,r["B1"],edgecolor=B,lw=0.95)
    circ(ax,origin,r["mid"],edgecolor=CUT,lw=0.8)
    circ(ax,origin,r["B2"],edgecolor="#c17a6f",lw=0.7)
    if n>=3:
        xs,ys=ngon(n,R); ax.plot(xs+ox,ys+oy,color=A,lw=0.7)
    ax.plot([ox-R,ox+R],[oy,oy],color=CUT,lw=1.2)

def sheet_A0(out,n_max):
    fig,ax=sheet(); bare(ax); ax.set_xlim(0,11); ax.set_ylim(0,8.5)
    title(fig,"A0","Index",f"n = 1…{n_max}")
    ax.text(0.55,7.2,"One object. Three sights. The cut is common.",fontsize=12,color=INK)
    boxes=[(0.55,4.2,"P  PLAN","face · nested web\nhalf-line is a diameter"),
           (3.2,4.2,"S  SECTION","count as height\nhalf-line is the cut"),
           (5.85,4.2,"E  ELEVATION","look-back\ninversion through 1"),
           (8.5,4.2,"O  OBLIQUE","stack without a new cut")]
    for x,y,h,body in boxes:
        ax.add_patch(FancyBboxPatch((x,y),2.35,2.0,boxstyle="square,pad=0",facecolor="#efeae0",edgecolor=INK,lw=0.7))
        ax.text(x+0.12,y+1.72,h,fontsize=9,color=INK,fontweight="bold")
        ax.text(x+0.12,y+1.15,body,fontsize=7.5,color=INK)
    ax.text(0.55,2.4,"Measure what is parallel to the sheet.\nScale is a title block. The half-line is in every frame.\ncad_half_line.html — static object, ortho snap, angles from the cut.",fontsize=8,color=INK)
    fig.savefig(out/"A0_index.png",dpi=150,facecolor=PAPER); plt.close()

def sheet_P1(out,n):
    fig,ax=sheet(); bare(ax); title(fig,"P1",f"Plan  ·  freeze {n}","half-line is the diameter")
    R=radii(n)["R"]; ax.set_xlim(-R*1.25,R*1.25); ax.set_ylim(-R*1.25,R*1.25)
    draw_web(ax,n); fig.savefig(out/"P1_plan.png",dpi=150,facecolor=PAPER); plt.close()

def sheet_S1(out,n_max):
    fig,ax=sheet(); bare(ax); title(fig,"S1","Section on the half-line","count as height · face dropped")
    ax.set_xlim(-n_max/2*1.15,n_max/2*1.15); ax.set_ylim(-0.6,n_max+1.2)
    ax.plot([0,0],[1,n_max],color=CUT,lw=0.7)
    ax.plot([-0.5,n_max/2],[1,n_max],color=A,lw=1.0)
    for n in range(1,n_max+1):
        R=n/2.0; col=INK if n==n_max else RULE
        ax.plot([-R,R],[n,n],color=col,lw=0.9 if n==n_max else 0.45)
        if n in (1,2,5,6,10,n_max):
            ax.text(R+0.15,n,str(n),fontsize=6,color=DIM,va="center")
    fig.savefig(out/"S1_section.png",dpi=150,facecolor=PAPER); plt.close()

def sheet_E1(out,n_max):
    fig,ax=sheet(); ax.set_facecolor(PAPER)
    title(fig,"E1","Elevation  ·  look-back","weight of a tick is log n")
    ns=np.arange(1,min(n_max,24)+1)
    ax.plot(ns,np.log(ns),color=B,lw=1.2,marker="o",ms=4)
    ax.axhline(0,color=RULE,lw=0.5)
    ax.set_xlabel("n",color=DIM); ax.set_ylabel("log n",color=DIM)
    for s in ax.spines.values(): s.set_color(RULE)
    ax.tick_params(colors=DIM)
    fig.savefig(out/"E1_elevation.png",dpi=150,facecolor=PAPER); plt.close()

def sheet_O1(out,n_max):
    fig=plt.figure(figsize=(11,8.5),facecolor=PAPER)
    ax=fig.add_subplot(111,projection="3d",facecolor=PAPER)
    title(fig,"O1","Oblique  ·  stack","no new cut")
    for n in range(1,n_max+1):
        R=n/2.0; xs,ys=ngon(max(n,3),R); z=np.full_like(xs,n)
        ax.plot(xs,ys,z,color=A if n==n_max else RULE,lw=0.7 if n==n_max else 0.3)
    ax.plot([0,0],[0,0],[1,n_max],color=CUT,lw=1.0); ax.set_axis_off()
    fig.savefig(out/"O1_oblique.png",dpi=150,facecolor=PAPER); plt.close()

def sheet_D1(out):
    fig,ax=sheet(); bare(ax); title(fig,"D1","Paper  ·  n = 1","radius already 1/2")
    ax.set_xlim(-1.2,1.2); ax.set_ylim(-1.2,1.2)
    circ(ax,(0,0),0.5,edgecolor=INK,lw=1.3)
    ax.plot([-0.5,0.5],[0,0],color=CUT,lw=1.2); ax.plot(0,0,"o",color=B,ms=5)
    fig.savefig(out/"D1_paper.png",dpi=150,facecolor=PAPER); plt.close()

def sheet_D3(out):
    fig,ax=sheet(); bare(ax); title(fig,"D3","Meeting at five","2 cos(π/5) = φ")
    ax.set_xlim(-3.2,3.2); ax.set_ylim(-3.2,3.2); draw_web(ax,5)
    fig.savefig(out/"D3_five.png",dpi=150,facecolor=PAPER); plt.close()

def sheet_D5(out,n):
    fig,ax=sheet(); bare(ax); title(fig,"D5",f"Nested web  ·  n = {n}","lock, half, Φ-nest")
    R=radii(n)["R"]; ax.set_xlim(-R*1.2,R*1.2); ax.set_ylim(-R*1.2,R*1.2)
    draw_web(ax,n); fig.savefig(out/"D5_web.png",dpi=150,facecolor=PAPER); plt.close()

def cad_html(out,n):
    r=radii(n); R=r["R"]; rot=PI/2
    verts=[]
    for k in range(n):
        th=rot+2*PI*k/n
        verts.append((R*math.cos(th), R*math.sin(th), f"V{k}"))
    snaps=[(0.0,0.0,"origin")]+verts
    for name,rr in (("apo",r["apo"]),("B1",r["B1"]),("mid",r["mid"]),("B2",r["B2"]),("R",R)):
        if rr==rr and rr>0:
            snaps += [(rr,0.0,f"{name}+"),(-rr,0.0,f"{name}-"),(0.0,rr,f"{name}N"),(0.0,-rr,f"{name}S")]
    for k in range(n):
        th=rot+2*PI*k/n
        snaps.append((0.5*R*math.cos(th),0.5*R*math.sin(th),f"M{k}"))
    data=dict(n=n,R=R,mid=r["mid"],B1=r["B1"],B2=r["B2"],apo=r["apo"],verts=verts,snaps=snaps)
    html = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>EoP CAD — half-line</title>
<style>
html,body{margin:0;height:100%;background:#f4f1ea;font:13px/1.35 ui-sans-serif,system-ui;color:#1a1a1a}
#bar{position:fixed;top:0;left:0;right:0;padding:10px 16px;background:#efeae0;border-bottom:1px solid #c8c2b4;z-index:2}
#read{position:fixed;right:16px;top:56px;width:250px;background:#efeae0;border:1px solid #c8c2b4;padding:12px;z-index:2}
#read div{margin:4px 0;color:#6b6b6b} #read span{color:#1a1a1a}
canvas{display:block;margin:72px auto 24px}
</style></head><body>
<div id="bar"><b>ELEMENTS OF POSITION</b> &nbsp; CAD · freeze """ + str(n) + """ · half-line
&nbsp; <small>drag to measure · snap to axis / vertices / nests · hold Shift for 15°</small></div>
<div id="read">
<div>from <span id="a">origin</span></div><div>to <span id="b">—</span></div>
<div>dx <span id="dx">—</span></div><div>dy <span id="dy">—</span></div>
<div>len / R <span id="lr">—</span></div><div>angle° <span id="ang">—</span></div>
<div>snap <span id="sn">ortho</span></div>
</div>
<canvas id="c"></canvas>
<script>
const DATA = """ + json.dumps(data) + """;
const cvs=document.getElementById('c'); const ctx=cvs.getContext('2d');
const W=Math.min(980,window.innerWidth-40), H=Math.min(720,window.innerHeight-120);
cvs.width=W; cvs.height=H; const cx=W/2, cy=H/2; const sc=Math.min(W,H)*0.38/DATA.R;
const tox=x=>cx+x*sc, toy=y=>cy-y*sc, fromx=px=>(px-cx)/sc, fromy=py=>(cy-py)/sc;
function draw(){
  ctx.fillStyle='#f4f1ea'; ctx.fillRect(0,0,W,H);
  ctx.strokeStyle='#c8c2b4'; ctx.lineWidth=1;
  ctx.beginPath(); ctx.moveTo(0,cy); ctx.lineTo(W,cy); ctx.moveTo(cx,0); ctx.lineTo(cx,H); ctx.stroke();
  const rings=[['R',DATA.R,'#1a1a1a',1.6],['apo',DATA.apo,'#4a6fa5',1],['B1',DATA.B1,'#8b3a3a',1.3],['mid',DATA.mid,'#6b4c7a',1.1],['B2',DATA.B2,'#c17a6f',1]];
  for(const [name,r,col,w] of rings){ if(!(r>0)) continue; ctx.beginPath(); ctx.arc(cx,cy,r*sc,0,Math.PI*2); ctx.strokeStyle=col; ctx.lineWidth=w; ctx.stroke(); }
  ctx.beginPath(); DATA.verts.forEach((v,i)=>{const X=tox(v[0]),Y=toy(v[1]); i?ctx.lineTo(X,Y):ctx.moveTo(X,Y)});
  ctx.closePath(); ctx.strokeStyle='#2c3e50'; ctx.lineWidth=1.1; ctx.stroke();
  DATA.verts.forEach(v=>{ctx.beginPath();ctx.arc(tox(v[0]),toy(v[1]),3,0,7);ctx.fillStyle='#2c3e50';ctx.fill()});
  ctx.beginPath(); ctx.moveTo(tox(-DATA.R),cy); ctx.lineTo(tox(DATA.R),cy);
  ctx.strokeStyle='#6b4c7a'; ctx.lineWidth=2.2; ctx.stroke();
  ctx.fillStyle='#6b4c7a'; ctx.beginPath(); ctx.arc(cx,cy,4,0,7); ctx.fill();
  if(measure){
    const p=snap(measure.x,measure.y);
    ctx.beginPath(); ctx.moveTo(tox(measure.x0),toy(measure.y0)); ctx.lineTo(tox(p.x),toy(p.y));
    ctx.strokeStyle='#8b3a3a'; ctx.lineWidth=1.4; ctx.stroke();
    ctx.beginPath(); ctx.arc(tox(p.x),toy(p.y),4,0,7); ctx.fillStyle='#8b3a3a'; ctx.fill();
  }
}
function nearestSnap(x,y){
  let best=null,bd=1e9;
  for(const s of DATA.snaps){ const d=Math.hypot(x-s[0],y-s[1]); if(d<bd){bd=d;best=s} }
  if(best && bd<DATA.R*0.06) return {x:best[0],y:best[1],name:best[2],kind:'point'};
  return null;
}
function snap(x,y,shift){
  const p=nearestSnap(x,y); if(p) return p;
  if(Math.abs(y)<DATA.R*0.04) return {x:x,y:0,name:'on cut',kind:'ortho'};
  if(Math.abs(x)<DATA.R*0.04) return {x:0,y:y,name:'perp cut',kind:'ortho'};
  if(shift){ const ang=Math.round(Math.atan2(y,x)*180/Math.PI/15)*15*Math.PI/180; const L=Math.hypot(x,y);
    return {x:L*Math.cos(ang),y:L*Math.sin(ang),name:'15deg',kind:'angle'}; }
  return {x:x,y:y,name:'free',kind:'free'};
}
let measure=null, shiftOn=false;
window.addEventListener('keydown',e=>{if(e.key==='Shift') shiftOn=true});
window.addEventListener('keyup',e=>{if(e.key==='Shift') shiftOn=false});
cvs.addEventListener('mousedown',e=>{
  const r=cvs.getBoundingClientRect(); const p=snap(fromx(e.clientX-r.left),fromy(e.clientY-r.top),shiftOn);
  measure={x0:p.x,y0:p.y,x:p.x,y:p.y,from:p.name};
});
cvs.addEventListener('mousemove',e=>{
  if(!measure) return;
  const r=cvs.getBoundingClientRect(); const p=snap(fromx(e.clientX-r.left),fromy(e.clientY-r.top),shiftOn);
  measure.x=p.x; measure.y=p.y;
  const dx=p.x-measure.x0, dy=p.y-measure.y0;
  document.getElementById('a').textContent=measure.from;
  document.getElementById('b').textContent=p.name;
  document.getElementById('dx').textContent=dx.toFixed(4);
  document.getElementById('dy').textContent=dy.toFixed(4);
  document.getElementById('lr').textContent=(Math.hypot(dx,dy)/DATA.R).toFixed(4);
  document.getElementById('ang').textContent=(Math.atan2(dy,dx)*180/Math.PI).toFixed(2);
  document.getElementById('sn').textContent=p.kind;
  draw();
});
draw();
</script></body></html>"""
    (out/"cad_half_line.html").write_text(html)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--n-max", type=int, default=36)
    ap.add_argument("--out", type=Path, default=Path("/home/workdir/artifacts/eop_set"))
    args=ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    write_csv(args.n_max, args.out/"measurements.csv")
    sheet_A0(args.out, args.n_max)
    sheet_P1(args.out, args.n_max)
    sheet_S1(args.out, args.n_max)
    sheet_E1(args.out, args.n_max)
    sheet_O1(args.out, args.n_max)
    sheet_D1(args.out)
    sheet_D3(args.out)
    sheet_D5(args.out, args.n_max)
    cad_html(args.out, args.n_max)
    print("wrote", args.out)

if __name__=="__main__":
    main()
