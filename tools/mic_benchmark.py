import asyncio,json,sys
from playwright.async_api import async_playwright
# sequence at 100 bpm: (midi or None, beats)
import os
BPM=int(os.environ.get('BPM','100'));PED=os.environ.get('PED','0')=='1'
SEQ=[(60,1),(60,1),(64,.5),(64,.5),(67,1),(72,.5),(71,.5),(69,.5),(67,.5),(65,1),(None,1),(48,1),(55,1),(52,2),(76,.25),(77,.25),(79,.5),(81,1),(62,.5),(62,.5),(62,1),(70,1),(57,2)]
FAKE="""
navigator.mediaDevices.getUserMedia=async()=>{const c=new AudioContext();const d=c.createMediaStreamDestination();
 const noise=c.createBufferSource();const nb=c.createBuffer(1,c.sampleRate*2,c.sampleRate);const ch=nb.getChannelData(0);for(let i=0;i<ch.length;i++)ch[i]=(Math.random()*2-1)*.02;noise.buffer=nb;noise.loop=true;noise.connect(d);noise.start();
 const names=['C2','Ds2','Fs2','A2','C3','Ds3','Fs3','A3','C4','Ds4','Fs4','A4','C5','Ds5','Fs5','A5','C6'];const mid=n=>{const m=n.match(/^([A-G])(s?)(\\d)$/);return(+m[3]+1)*12+{C:0,D:2,E:4,F:5,G:7,A:9,B:11}[m[1]]+(m[2]?1:0)};
 const bufs=await Promise.all(names.map(n=>fetch('s/'+n+'.mp3').then(r=>r.arrayBuffer()).then(b=>c.decodeAudioData(b)).then(x=>[mid(n),x])));
 const room=c.createConvolver();const ir=c.createBuffer(2,c.sampleRate*.8,c.sampleRate);for(let k=0;k<2;k++){const a=ir.getChannelData(k);for(let i=0;i<a.length;i++)a[i]=(Math.random()*2-1)*Math.pow(1-i/a.length,3)*.25}room.buffer=ir;
 const wet=c.createGain();wet.gain.value=.35;room.connect(wet);wet.connect(d);const dry=c.createGain();dry.gain.value=.5;dry.connect(d);dry.connect(room);
 window.__playMic=(seq,bpm,ped)=>{let seed=7;const rnd=()=>{seed=(seed*16807)%2147483647;return seed/2147483647};const spb=60/bpm;let t=c.currentTime+.05;for(const [m,b] of seq){if(m){let best=bufs[0];for(const x of bufs)if(Math.abs(x[0]-m)<Math.abs(best[0]-m))best=x;
   const s=c.createBufferSource();s.buffer=best[1];s.playbackRate.value=Math.pow(2,(m-best[0])/12);const g=c.createGain();const v=.3+rnd()*.7,rel=t+b*spb*(ped?2.2:.92);g.gain.setValueAtTime(v,t);g.gain.setValueAtTime(v,rel);g.gain.setTargetAtTime(0,rel,.08);s.connect(g);g.connect(dry);s.start(t);s.stop(rel+.6)}t+=b*spb}};
 return d.stream};
"""
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required']);errs=[]
        pg=await b.new_page(viewport={'width':1180,'height':820})
        pg.on('pageerror',lambda e:errs.append('ERR '+str(e)))
        await pg.add_init_script(FAKE)
        await pg.goto('http://localhost:8765/');await pg.wait_for_timeout(800)
        await pg.click('#newBtn');await pg.wait_for_timeout(200)
        await pg.evaluate("(()=>{const t=document.getElementById('tempo');t.value=%d;t.dispatchEvent(new Event('input'));t.dispatchEvent(new Event('change'))})()"%BPM)
        await pg.click('#recBtn');await pg.click('#recSrc button[data-s="mic"]');await pg.click('#recGo')
        SPB=60/BPM
        await pg.wait_for_timeout(int((4*SPB+.25)*1000)-60)
        await pg.evaluate("window.__playMic(%s,%d,%s)"%(json.dumps(SEQ),BPM,"true" if PED else "false"))
        await pg.wait_for_timeout(int(sum(x[1] for x in SEQ)*SPB*1000)+1500)
        await pg.click('#recStop');await pg.wait_for_timeout(300)
        r=await pg.evaluate("window.__t.song.notes.map(n=>(n.ps.join('+')||'r')+n.d+(n.dot?'.':'')+(n.tie?'~':'')).join(' ')")
        got=await pg.evaluate("(()=>{let t=0;const o=[];for(const n of window.__t.song.notes){if(n.ps.length&&!(o.length&&o[o.length-1].tie))o.push({p:n.ps[0],t});else if(n.ps.length){} if(o.length)o[o.length-1].tie=!!n.tie;t+=({w:4,h:2,q:1,e:.5,s:.25,t:.125,x:.0625})[n.d]*(n.dot===2?1.75:n.dot?1.5:1)}return o.map(x=>[x.p,x.t])})()")
        exp=[];t=0
        for m,bb in SEQ:
            if m: exp.append((m,t))
            t+=bb
        ok=sum(1 for m,tt in exp if any(g[0]==m and abs(g[1]-tt)<.13 for g in got))
        print('expected',len(exp),'got',len(got),'exact match',ok);print(r);print(errs)
        await b.close()
asyncio.run(main())
