# builds annapp-site/index.html from annapp.html (standalone tweaks)
s=open('/home/claude/annapp.html').read()
def R(a,b):
    global s
    assert s.count(a)==1,a[:60];s=s.replace(a,b)
R("async function saveFile(filename,data){const d=await downloads();if(!d){toast('Pobieranie nie działa w tym widoku. Otwórz AnnApp w claude.ai.');return}",
  "async function saveFile(filename,data){const d=await downloads();if(!d){try{const blob=data instanceof Blob?data:new Blob([data]);const u=URL.createObjectURL(blob);const a=document.createElement('a');a.href=u;a.download=filename;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(u),4000);toast('Zapisano plik')}catch(e){toast('Nie udało się zapisać pliku')}return}")
R("let dl;async function downloads(){if(dl===undefined){try{dl=window.claude&&window.claude.use?await window.claude.use('downloads'):null}catch(e){dl=null}}return dl}",
  "let dl;async function downloads(){if(dl===undefined){try{dl=window.claude&&window.claude.use?await window.claude.use('downloads'):null}catch(e){dl=null}}return dl}\nif('serviceWorker' in navigator&&location.protocol==='https:'&&!window.claude)navigator.serviceWorker.register('sw.js').catch(()=>{});")
R("let songs=loadLocal();","let songs=loadLocal();try{navigator.storage&&navigator.storage.persist&&navigator.storage.persist()}catch(e){}")
p='/home/claude/annapp-site/index.html';old=open(p).read();head=old[:old.index('<body>\n')+7]
open(p,'w').write(head+s+'\n</body>\n</html>\n')
import re
sw='/home/claude/annapp-site/sw.js';t=open(sw).read();v=int(re.search(r"annapp-v(\d+)",t).group(1));open(sw,'w').write(t.replace(f"annapp-v{v}'",f"annapp-v{v+1}'"))
print('site built, cache v',v+1)
