import asyncio,json,os
from playwright.async_api import async_playwright
BPM=int(os.environ.get('BPM','90'));KIND=os.environ.get('KIND','hum');NOISE=float(os.environ.get('NOISE','.006'));STAC=os.environ.get('STAC','0')=='1'
SEQ=[(60,1),(62,1),(64,1),(60,1),(64,1),(65,1),(67,2),(67,.5),(69,.5),(67,.5),(65,.5),(64,1),(60,1),(None,1),(62,1),(62,1),(55,1),(60,2),(72,1),(71,.5),(69,.5),(67,1)]
FAKE="""
navigator.mediaDevices.getUserMedia=async()=>{const c=new AudioContext();const d=c.createMediaStreamDestination();
 const noise=c.createBufferSource();const nb=c.createBuffer(1,c.sampleRate*2,c.sampleRate);const ch=nb.getChannelData(0);for(let i=0;i<ch.length;i++)ch[i]=(Math.random()*2-1)*%s;noise.buffer=nb;noise.loop=true;noise.connect(d);noise.start();
 window.__sing=(seq,bpm,kind,stac)=>{let seed=11;const rnd=()=>{seed=(seed*16807)%%2147483647;return seed/2147483647};const spb=60/bpm;let t=c.currentTime+.05;const T0=t;
  const sh=kind==='whistle'?24:kind==='low'?-12:0;const det=kind==='whistle'?.3:-.25;
  for(let i=0;i<seq.length;i++){const [m,b]=seq[i];if(!m){t+=b*spb;continue}
   const late=(rnd()-.5)*.06;const t0=t+late,dur=b*spb,nx=seq[i+1],same=nx&&nx[0]===m;const gap=stac?dur*.35:same?.07:.025;const t1=t0+dur-gap;
   const f=440*Math.pow(2,(m+sh+det+(rnd()-.5)*.25-69)/12);
   const o=c.createOscillator();o.type=kind==='whistle'?'sine':'sawtooth';o.frequency.setValueAtTime(f*Math.pow(2,-.9/12),t0);o.frequency.exponentialRampToValueAtTime(f,t0+.07);
   const lfo=c.createOscillator();lfo.frequency.value=5.3;const lg=c.createGain();lg.gain.setValueAtTime(0,t0);lg.gain.linearRampToValueAtTime(f*.017,t0+Math.min(.4,dur*.6));lfo.connect(lg);lg.connect(o.frequency);
   const lp=c.createBiquadFilter();lp.type='lowpass';lp.frequency.value=kind==='whistle'?8000:900;lp.Q.value=2;
   const g=c.createGain();const v=(kind==='whistle'?.12:.35)*(.6+rnd()*.4);g.gain.setValueAtTime(0,t0);g.gain.linearRampToValueAtTime(v,t0+.04);g.gain.setValueAtTime(v,t1-.04);g.gain.linearRampToValueAtTime(0,t1);
   o.connect(lp);lp.connect(g);g.connect(d);o.start(t0);lfo.start(t0);o.stop(t1+.05);lfo.stop(t1+.05);
   if(kind==='whistle'){const ns=c.createBufferSource();ns.buffer=nb;const bp=c.createBiquadFilter();bp.type='bandpass';bp.frequency.value=f;bp.Q.value=3;const ng=c.createGain();ng.gain.setValueAtTime(0,t0);ng.gain.linearRampToValueAtTime(1.5,t0+.04);ng.gain.setValueAtTime(1.5,t1-.04);ng.gain.linearRampToValueAtTime(0,t1);ns.connect(bp);bp.connect(ng);ng.connect(d);ns.start(t0);ns.stop(t1+.05)}
   t+=b*spb}};
 return d.stream};
"""%NOISE
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required']);errs=[]
        pg=await b.new_page(viewport={'width':1180,'height':820})
        pg.on('console',lambda m:print(m.text) if m.text.startswith('ON') else None);pg.on('pageerror',lambda e:errs.append('ERR '+str(e)))
        await pg.add_init_script(FAKE)
        await pg.goto('http://localhost:8765/');await pg.wait_for_timeout(800)
        await pg.click('#newBtn');await pg.wait_for_timeout(200)
        await pg.evaluate("(()=>{const t=document.getElementById('tempo');t.value=%d;t.dispatchEvent(new Event('input'));t.dispatchEvent(new Event('change'))})()"%BPM)
        await pg.click('#recBtn');await pg.click('#recSrc button[data-s="voice"]');await pg.click('#recGo')
        SPB=60/BPM
        await pg.wait_for_timeout(int((4*SPB+.25)*1000)-40)
        await pg.evaluate("window.__sing(%s,%d,'%s',%s)"%(json.dumps(SEQ),BPM,KIND,'true' if STAC else 'false'))
        await pg.wait_for_timeout(int(sum(x[1] for x in SEQ)*SPB*1000)+1500)
        await pg.click('#recStop');await pg.wait_for_timeout(300)
        r=await pg.evaluate("window.__t.song.notes.map(n=>(n.ps.join('+')||'r')+n.d+(n.dot?'.':'')+(n.tie?'~':'')).join(' ')")
        got=await pg.evaluate("(()=>{let t=0;const o=[];for(const n of window.__t.song.notes){if(n.ps.length&&!(o.length&&o[o.length-1].tie))o.push({p:n.ps[0],t});else if(n.ps.length){} if(o.length)o[o.length-1].tie=!!n.tie;t+=({w:4,h:2,q:1,e:.5,s:.25,t:.125,x:.0625})[n.d]*(n.dot===2?1.75:n.dot?1.5:1)}return o.map(x=>[x.p,x.t])})()")
        exp=[];t=0
        for m,bb in SEQ:
            if m: exp.append((m,t))
            t+=bb
        best=0
        for k in range(-3,4):
            ok=sum(1 for m,tt in exp if any(g[0]==m+12*k and abs(g[1]-tt)<.13 for g in got));best=max(best,ok)
        print(KIND,BPM,'noise',NOISE,'stac' if STAC else '','expected',len(exp),'got',len(got),'match',best);print(r[:400]);print(errs)
        await b.close()
asyncio.run(main())
