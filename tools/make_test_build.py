import json
s=open('/home/claude/annapp.html').read()
s=s.replace("applySong(false);\n})();","applySong(false);window.__t={get song(){return song},musicXML,changed,play,stop};\n})();")
open('/tmp/claude-0/www/index.html','w').write('<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><style>:root{color-scheme:light}body{margin:0;font:14px system-ui}[hidden]{display:none!important}</style></head><body>'+s+'</body></html>')
N=lambda ps,d='q',**k:dict(ps=ps if isinstance(ps,list) else [ps],d=d,**k)
notes=[N(67,'q',tx='Refren',reh=True,tc=88,dyn='mf'),N(69,'e',ar=['stac']),N(71,'e',ar=['stacc2']),N(72,'s',sl='s'),N(74,'s'),N(76,'t'),N(77,'t'),N(79,'x'),N(77,'x'),N(76,'x'),N(74,'x'),N(72,'q',sl='e',ar=['ferm']),
 N(64,'e',gr='a'),N(67,'q',orn='tr',ch='C'),N(69,'q',orn='mord'),N(71,'q',orn='turn',ar=['acc']),N(72,'q',dot=2,ar=['marc'],ch='G7'),N(74,'s'),
 N(72,'q',ott='8va',ps2=None),N(74,'q'),N(76,'h',trem=2,dyn='sfz'),
 N([60,64,67],'q',arp=True,rs=True),N(65,'q',gl=True),N(72,'q',jz='fall'),N(64,'q',jz='scoop',ar=['breath']),
 N(67,'q',vo=1),N(65,'q',vo=1),N(64,'h',vo=1,re=True),
 N(62,'q',vo=2,tm='rit'),N(60,'q',vo=2,ar=['up']),N(60,'h',vo=2,dbl=True,ar=['down']),
 N(60,'q',tr=True,sg=True),N(62,'q',tr=True),N(64,'q',tr=True),N(65,'q',hp='<'),N(67,'q',pz='pizz',dyn='ff'),
 N(69,'q',tm='atempo'),N(71,'q',sw='on'),N(72,'q',fi=True,br=True),
 N(72,'h',ar=['ten','open']),N(71,'h',ar=['port','stop']),N(72,'w',ds=True)]
for n in notes: n.pop('ps2',None)
notes[18]['ps']=[84]
bass=[N([48,55],'w',ped='d'),N([43,55],'h'),N(43,'h',ped='u'),N([45,52],'w'),N([41,53],'w'),N([43,50],'w'),N(48,'w'),N(41,'w'),N(43,'w'),N(48,'w'),N(48,'w'),N(48,'w'),N(48,'w')]
song=dict(id='test1',title='Test znaków',tempo=100,mn=4,md=4,msym='C',key=-3,hands=2,clefs=dict(t='t',b='b'),look='las',color=False,notes=notes,bass=bass,updated=9999999999999)
song2=dict(id='test2',title='Alt i tenor',tempo=90,mn=6,md=8,key=4,hands=2,clefs=dict(t='a',b='ten'),look='ocean',color=True,notes=[N(p,'e') for p in [60,62,64,65,67,69,71,72,74,76,77,79]],bass=[N(p,'e') for p in [48,50,52,53,55,57,59,60,62,64,65,67]],updated=1)
json.dump([song,song2],open('/tmp/claude-0/songs.json','w'))
