/* Cerchio del tempo.
   Disegna ogni era presente in ERAS come arco proporzionale agli anni e vi colloca
   gli eventi di EVENTS. Ridisegna tutto a ogni selezione. Nessuna libreria, tutto SVG.
   Eventi troppo vicini vengono distanziati di MINSTEP gradi per poterli toccare. */

const CX=350,CY=350,R=250,GAP=20,SPAN=360-GAP,MINSTEP=3.6;
const TOT=ERAS.reduce((t,s)=>t+s.len,0);
let cur=GAP/2;
ERAS.forEach(s=>{s.span=SPAN*s.len/TOT;s.a0=cur;s.a1=cur+s.span;cur=s.a1});

const AN=EVENTS.map(e=>{
  const s=ERAS.find(x=>x.id===e.era);
  return s.a0+e.year/s.len*s.span;
});
for(let i=AN.length-2;i>=0;i--)AN[i]=Math.min(AN[i],AN[i+1]-MINSTEP);
if(AN[0]<ERAS[0].a0+.4){AN[0]=ERAS[0].a0+.4;for(let i=1;AN[i]<AN[i-1]+MINSTEP;i++)AN[i]=AN[i-1]+MINSTEP}

const P=(a,r)=>{const t=a*Math.PI/180;return[CX+r*Math.sin(t),CY-r*Math.cos(t)]};
const arc=(a,b,r)=>{const[x1,y1]=P(a,r),[x2,y2]=P(b,r);return`M${x1.toFixed(1)} ${y1.toFixed(1)}A${r} ${r} 0 ${b-a>180?1:0} 1 ${x2.toFixed(1)} ${y2.toFixed(1)}`};
const wrap=(t,n)=>{const w=t.split(" ");const L=[];let c="";w.forEach(x=>{if((c+" "+x).trim().length>n&&c){L.push(c);c=x}else c=(c+" "+x).trim()});L.push(c);return L};

let S=EVENTS.findIndex(e=>e.id==="distruzione-anello");
if(S<0)S=0;

function draw(){
  const e=EVENTS[S],era=ERAS.find(x=>x.id===e.era);
  let g="";
  ERAS.forEach(s=>{
    g+=`<path class="arc" d="${arc(s.a0+.4,s.a1-.4,R)}"/>`;
    const m=(s.a0+s.a1)/2;
    if(m>GAP/2+30||m<180)g+=`<text class="era" x="${CX}" y="${350-R-16}" text-anchor="middle">${s.name.toUpperCase()}</text>`;
  });
  for(let y=500;y<era.len;y+=500){const a=era.a0+y/era.len*era.span,[x1,y1]=P(a,R-10),[x2,y2]=P(a,R-20);
    g+=`<line class="tick" x1="${x1.toFixed(1)}" y1="${y1.toFixed(1)}" x2="${x2.toFixed(1)}" y2="${y2.toFixed(1)}"/>`;
    const[tx,ty]=P(a,R-40);g+=`<text class="tickL" x="${tx.toFixed(1)}" y="${ty.toFixed(1)}" dy=".35em" text-anchor="middle">${y}</text>`}
  const a=AN[S],[sx,sy]=P(a,R),[ex,ey]=P(a,R-58);
  g+=`<line class="conn" x1="${sx}" y1="${sy}" x2="${ex}" y2="${ey}"/>`;
  const L=wrap(e.title,20).slice(0,3),big=e.label,fs=big.length>14?27:(big.length>8?36:46),n=L.length;
  g+=`<text class="big" x="350" y="${296-(n-1)*16}" text-anchor="middle" font-size="${fs}">${big}</text>`;
  g+=L.map((l,i)=>`<text class="ttl" x="350" y="${348-(n-1)*16+i*33}" text-anchor="middle">${l}</text>`).join("");
  EVENTS.forEach((v,i)=>{const[x,y]=P(AN[i],R),on=i===S;
    g+=`<g class="dot" tabindex="0" role="button" aria-label="${v.title}" data-i="${i}"><circle class="hit" cx="${x}" cy="${y}" r="15" fill="transparent"/><circle class="v" cx="${x}" cy="${y}" r="${on?9:4.5}"/>${on?`<circle class="ring" cx="${x}" cy="${y}" r="15"/>`:""}</g>`});
  document.getElementById("chart").innerHTML=`<svg viewBox="0 0 700 700" role="group" aria-label="Cerchio del tempo">${g}</svg>`;
  document.getElementById("det").innerHTML=`<p class="y">${era.name} · ${e.label}</p><h2>${e.title}</h2><p>${e.desc}</p>`;
  document.getElementById("cn").textContent=`${S+1} di ${EVENTS.length}`;
}

const go=i=>{S=(i+EVENTS.length)%EVENTS.length;draw()};
document.getElementById("chart").addEventListener("click",ev=>{
  const d=ev.target.closest("[data-i]");if(d)go(+d.dataset.i);
});
document.getElementById("chart").addEventListener("keydown",ev=>{
  if((ev.key==="Enter"||ev.key===" ")&&ev.target.dataset.i){ev.preventDefault();go(+ev.target.dataset.i);
    const g=document.querySelector(`[data-i="${S}"]`);g&&g.focus()}
});
document.getElementById("pv").onclick=()=>go(S-1);
document.getElementById("nx").onclick=()=>go(S+1);
document.addEventListener("keydown",e=>{if(e.key==="ArrowLeft")go(S-1);if(e.key==="ArrowRight")go(S+1)});
draw();
