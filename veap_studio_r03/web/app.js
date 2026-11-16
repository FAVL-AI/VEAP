/* VEAP Foundry Studio R0.3 — original user interface, local-only research pilot.
   All camera/depth/scene renderings in demo mode are synthetic illustrations.
   Uploading MCAP does not prove source authenticity or enable ROS command authority. */
(()=>{
'use strict';
const $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)];
const readToken=()=>{try{return sessionStorage.getItem('veap-token')||''}catch{return ''}};
const st={assets:[], current:null,rows:[],report:null,idx:0,playing:false,speed:1,lastTime:0,angle:-.72,zoom:1.00,pointcloud:true,bounds:true,view:'replay',inspect:'events',reportExport:null,modal:false,modelVerts:null,worldPoints:null,mediaAsset:null,token:readToken()};
const esc=s=>String(s??'').replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
const num=(n,d=2)=>n!==null&&n!==undefined&&n!==''&&Number.isFinite(Number(n))?Number(n).toFixed(d):'—';
let toastHandle=null, mediaBlobUrl=null, currentDetailAsset=null;
function toast(text,bad=false){const t=$('#toast');t.textContent=text;t.style.borderColor=bad?'#ae5c5c':'#668d43';t.classList.add('show');clearTimeout(toastHandle);toastHandle=setTimeout(()=>t.classList.remove('show'),4500)}
async function api(path,options={}){let headers={'x-veap-token':st.token,...(options.headers||{})};let r=await fetch(path,{...options,headers});if(r.status===401){let value=prompt('Enter local VEAP_STUDIO_TOKEN configured on the server:');if(value){st.token=value;try{sessionStorage.setItem('veap-token',value)}catch{};return api(path,options)}}if(!r.ok){let j=await r.json().catch(()=>({detail:r.statusText}));throw Error(typeof j.detail==='string'?j.detail:'Request failed '+r.status)}return r.json()}
function openPage(name){st.view=name;$$('.page').forEach(p=>p.classList.toggle('active',p.id==='page'+name[0].toUpperCase()+name.slice(1)));$$('.railbutton[data-page]').forEach(b=>b.classList.toggle('active',b.dataset.page===name));let titles={replay:'Replay Operations',world:'World Studio',data:'Evidence Registry',policy:'Policy Lab',assurance:'Assurance',connectors:'Runtime Workbench'};$('#crumbPage').textContent=titles[name]||name;if(name==='world'){renderWorld();requestAnimationFrame(()=>drawScene('#worldCanvas'))}if(name==='data'){renderRegistry();loadInbox()};if(name==='policy'){ensureBenchInit();requestAnimationFrame(()=>benchScene&&benchScene.resize())}if(name==='assurance'){populateSelects();renderAssuranceCards();loadContracts()}if(name==='connectors')renderConnectors();if(name==='replay')requestAnimationFrame(renderAll)}
function setSide(name){$$('[data-side]').forEach(b=>b.classList.toggle('selected',b.dataset.side===name));$$('.side-content').forEach(n=>n.classList.add('hidden'));$('#side'+name[0].toUpperCase()+name.slice(1)).classList.remove('hidden')}
function badge(a){if(a.origin==='DEMO_SYNTHETIC')return '<span class="badge-lite">SYNTHETIC</span>';if(a.origin==='DERIVED_SYNTHETIC_FAULT')return '<span class="badge-lite">DERIVED</span>';return '<span class="badge-lite">UNATTESTED</span>'}
function assetLabel(a){return a.name.replace(/\.jsonl$/,'').replace(/\.csv$/,'')}
function assetList(){return st.assets.filter(x=>x.kind==='TRAJECTORY')}
async function refreshAssets(preferId){let j=await api('/api/assets');st.assets=j.assets;$('#sourceCount').textContent=st.assets.length;renderSources();renderRegistry();populateSelects();renderMediaOptions();if(preferId)await selectRun(preferId);else if(!st.current){const initial=assetList().find(a=>a.name.startsWith('M3 · Yard'))||assetList()[0];if(initial)await selectRun(initial.id)}}
function renderSources(){const match=$('#sideSearch').value.toLowerCase();const items=st.assets.filter(a=>!match||[a.name,a.kind,a.origin].join(' ').toLowerCase().includes(match));$('#sourceItems').innerHTML=items.map(a=>`<div class="source-item ${a.id===st.current?.id?'active':''}" data-source="${a.id}" role="button" tabindex="0"><div class="source-symbol">${a.kind==='TRAJECTORY'?'↝':a.kind==='VIDEO'?'▣':a.kind==='MCAP'?'◉':'◇'}</div><div><span>${esc(assetLabel(a))}</span><small>${esc(a.kind)} · ${a.origin==='DEMO_SYNTHETIC'?'Synthetic demonstration':'Unattested upload'}</small></div></div>`).join('')||'<p class="small-note">No matching evidence. Import a file.</p>';$$('[data-source]').forEach(n=>{n.onclick=()=>openAsset(n.dataset.source);n.onkeydown=e=>{if(e.key==='Enter')openAsset(n.dataset.source)}})}
function openAsset(id){let a=st.assets.find(x=>x.id===id);if(!a)return;
if(a.kind==='TRAJECTORY'){selectRun(id).then(()=>openPage('replay')).catch(e=>toast(e.message,true));return}
if(['MODEL_3D','CAD','ROBOT_DESCRIPTION','POINT_CLOUD'].includes(a.kind)){openPage('world');$('#geometrySelect').value=a.id;inspectGeometry();return}
if(['VIDEO','IMAGE'].includes(a.kind)){openPage('replay');$('#cameraSource').value=id;pickCameraMedia(id);toast('Media preview: recorded clock alignment has not been established.');return}
showAssetDetails(a)}
async function showAssetDetails(a){currentDetailAsset=a;$('#assetModalTitle').textContent=a.name;$('#assetTags').value=(a.meta.tags||[]).join(', ');$('#assetNote').value=a.note||'';$('#assetDetail').textContent=JSON.stringify({kind:a.kind,sha256:a.sha256,bytes:a.size,source:a.origin,provenance:a.meta.provenance,metadata:a.meta},null,2);$('#assetOverlay').classList.remove('hidden');
if(a.kind==='LOG'){try{let j=await api('/api/assets/'+a.id+'/text-preview');$('#assetDetail').textContent=j.text+(j.truncated?'\n[Preview truncated at 128 KB]':'')}catch(e){toast(e.message,true)}}}
function closeAssetDetails(){currentDetailAsset=null;$('#assetOverlay').classList.add('hidden')}
async function saveAssetDetails(){if(!currentDetailAsset)return;let tags=$('#assetTags').value.split(',').map(x=>x.trim()).filter(Boolean);try{let j=await api('/api/assets/'+currentDetailAsset.id,{method:'PATCH',headers:{'Content-Type':'application/json'},body:JSON.stringify({tags,note:$('#assetNote').value})});closeAssetDetails();await refreshAssets();toast('Local tags and notes updated; source bytes unchanged.')}catch(e){toast(e.message,true)}}
async function selectRun(id){let j=await api('/api/traces/'+id);st.current=j.asset;st.rows=j.rows;st.report=j.report;st.idx=0;st.playing=false;$('#playBtn').textContent='▶';updateHeader();renderSources();populateSelects();renderAll();await doCompare(false)}
function updateHeader(){let a=st.current,s=st.report;if(!a||!s)return;$('#runSubtitle').textContent=`${assetLabel(a)} • ${a.origin==='DEMO_SYNTHETIC'?'SYNTHETIC SOURCE':'UNATTESTED SOURCE'} • ${s.duration_s}s • ${s.samples} samples`;$('#statTask').textContent=s.task_complete===null?'NOT SCORED':(s.task_complete?'COMPLETE':'INCOMPLETE');$('#statTask').className=s.task_complete===null?'orange-text':(s.task_complete?'green-text':'orange-text');$('#statVerdict').textContent=s.process_accepted===null?'NO CONTRACT':(s.process_accepted?'ACCEPTED':'REVIEW');$('#statVerdict').className=s.process_accepted===null?'orange-text':(s.process_accepted?'green-text':'red-text');$('#statViolations').textContent=s.violations===null?'N/A':s.violations;$('#statViolations').className=s.violations===null?'orange-text':(s.violations?'red-text':'green-text');$('#statSamples').textContent=s.samples.toLocaleString();$('#contractVerdict').textContent=s.verdict;$('#sourceDigest').textContent=a.sha256;renderAssuranceCards();$('#eventCount').textContent=`${s.events.length} recorded events`;$('#timelineDuration').textContent=`${num(s.duration_s,1)} sec`;$('#scrub').max=Math.max(0,st.rows.length-1);$('#scrub').value=0;$('#worldMode').textContent=(a.name.includes('G1')?'G1 · FACILITY':'M3 · WAREHOUSE');let evts=s.events.length?s.events.slice(0,120):[{kind:'NO CONTRACT EVENTS',t_ns:st.rows[0].t_ns,index:0,severity:'info'}];$('#eventList').innerHTML=evts.map(e=>`<div class="event-card ${esc(e.severity)}" data-idx="${Number(e.index)}"><div class="event-title"><span class="evt-icon">${e.severity==='critical'?'!':e.severity==='warn'?'△':'•'}</span>${esc(e.kind)}<span class="event-time">${num((e.t_ns-st.rows[0].t_ns)/1e9,2)}s</span></div><div class="event-sub">${e.severity==='critical'?'Constraint breached under selected example':e.severity==='warn'?'Evidence-quality warning':'Trace event'} · sample ${e.index}</div></div>`).join('');$$('[data-idx]').forEach(e=>e.onclick=()=>seek(Number(e.dataset.idx)));drawEventTrack();}
function populateSelects(){let options=assetList().map(a=>`<option value="${a.id}">${esc(assetLabel(a))}</option>`).join('');['#compareSelect','#faultSource','#assuranceSource','#assuranceCompare'].forEach(selector=>{let s=$(selector);let old=s.value;s.innerHTML=(selector==='#assuranceCompare'?'<option value="">No reference</option>':'')+options;if([...s.options].some(x=>x.value===old))s.value=old;else if(st.current){if(selector==='#assuranceSource'||selector==='#faultSource')s.value=st.current.id;else if(selector==='#compareSelect'||selector==='#assuranceCompare'){let ref=assetList().find(x=>x.id!==st.current.id);if(ref)s.value=ref.id}}})}
async function doCompare(notify=true){if(!st.current||!$('#compareSelect').value)return;try{let c=await api('/api/compare',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({reference_id:st.current.id,candidate_id:$('#compareSelect').value})});$('#compareRmse').textContent=num(c.rmse_m,3)+' m';$('#compareMax').textContent=num(c.max_error_m,3)+' m';$('#compareRef').textContent=c.alignment==='ELAPSED_TIME_ONLY'?'ELAPSED':'—';$('#compareSummary').title='Uncalibrated discrepancy; not independent physics validation';if(notify)toast('Cross-trace discrepancy computed; calibration and ground truth not established.')}catch(e){$('#compareRmse').textContent='—';if(notify)toast(e.message,true)}}
function seek(i){if(!st.rows.length)return;st.idx=Math.max(0,Math.min(st.rows.length-1,Math.round(i)));$('#scrub').value=st.idx;renderAll()}
function frameSeconds(i){return st.rows.length?(st.rows[i].t_ns-st.rows[0].t_ns)/1e9:0}
function fmtTime(sec){let m=Math.floor(sec/60),s=Math.floor(sec%60),ms=Math.floor((sec%1)*1000);return `${String(m).padStart(2,'0')}:${String(s).padStart(2,'0')}.${String(ms).padStart(3,'0')}`}
function tickVisual(){let n=st.rows.length;if(!n)return;let r=st.rows[st.idx];$('#worldFrame').textContent=`t = ${num(frameSeconds(st.idx),2)} s`;$('#timelineClock').textContent=`${fmtTime(frameSeconds(st.idx))} / ${fmtTime(frameSeconds(n-1))}`;$('#frameText').textContent=`${String(st.idx).padStart(3,'0')} / ${n-1}`;['#cursor1','#cursor2','#cursor3'].forEach(s=>$(s).style.left=`${st.idx/Math.max(1,n-1)*100}%`);$('#scrub').value=st.idx}
const rand=(seed)=>{let x=Math.sin(seed*127.1)*43758.5453;return x-Math.floor(x)};
function ctx2(id){let cv=$(id),rect=cv.getBoundingClientRect();if(rect.width<1||rect.height<1)return null;let dpr=Math.min(2,window.devicePixelRatio||1);let w=Math.max(1,Math.round(rect.width*dpr)),h=Math.max(1,Math.round(rect.height*dpr));if(cv.width!==w||cv.height!==h){cv.width=w;cv.height=h}let c=cv.getContext('2d');c.setTransform(dpr,0,0,dpr,0,0);return {c,w:rect.width,h:rect.height}}
function poly(ctx,pts,fill,stroke,width=1){ctx.beginPath();ctx.moveTo(pts[0][0],pts[0][1]);for(const [x,y] of pts.slice(1))ctx.lineTo(x,y);ctx.closePath();if(fill){ctx.fillStyle=fill;ctx.fill()}if(stroke){ctx.strokeStyle=stroke;ctx.lineWidth=width;ctx.stroke()}}
function drawScene(selector='#sceneCanvas'){let obj=ctx2(selector);if(!obj||!st.rows.length)return;let {c,w,h}=obj;let g=c.createRadialGradient(w*.5,h*.3,5,w*.5,h*.5,Math.max(w,h)*.75);g.addColorStop(0,'#243a40');g.addColorStop(.55,'#12242c');g.addColorStop(1,'#09151b');c.fillStyle=g;c.fillRect(0,0,w,h);let scale=Math.min(w/18,h/10)*st.zoom;let angle=st.angle;
const p=(x,y,z=0)=>{let xx=x-6,yy=y-4.7;let X=xx*Math.cos(angle)-yy*Math.sin(angle);let Y=xx*Math.sin(angle)+yy*Math.cos(angle);return [w*.48+X*scale,h*.60+Y*scale*.58-z*scale*1.05]};
let ground=[p(0,0),p(12,0),p(12,9.4),p(0,9.4)];poly(c,ground,'#14252a','#52646b',1.5);
for(let x=0;x<=12;x+=.5){let a=p(x,0),b=p(x,9.4);c.beginPath();c.moveTo(...a);c.lineTo(...b);c.strokeStyle=(x%2===0)?'#3b575c6a':'#30505936';c.lineWidth=.8;c.stroke()}
for(let y=0;y<=9.4;y+=.5){let a=p(0,y),b=p(12,y);c.beginPath();c.moveTo(...a);c.lineTo(...b);c.strokeStyle=(y%2===0)?'#3b575c6a':'#30505936';c.stroke()}
function box(x,y,z,dx,dy,dz,col='#31515a',rim='#5e8791'){let top=[p(x,y,z+dz),p(x+dx,y,z+dz),p(x+dx,y+dy,z+dz),p(x,y+dy,z+dz)];poly(c,[p(x,y,z),p(x+dx,y,z),top[1],top[0]],'#1b343d',rim,0.6);poly(c,[p(x+dx,y,z),p(x+dx,y+dy,z),top[2],top[1]],'#173138',rim,.6);poly(c,[p(x,y+dy,z),p(x+dx,y+dy,z),top[2],top[3]],'#203c44',rim,.6);poly(c,top,col,rim,.9)}
let obstacles=[[1.3,2.4,1.6,.52,1.25],[7.3,6.8,2.2,.65,1.32],[8.8,3.2,1.25,.8,1.5],[2.8,7.1,2.0,.55,1.7]];
obstacles.forEach(([x,y,dx,dy,dz],j)=>{box(x,y,0,dx,dy,dz,j===0?'#375a62':'#304953','#6f9fab');for(let k=0;k<3;k++){let a=p(x+.1,y+.12,.35+k*.35),b=p(x+dx-.1,y+.12,.35+k*.35);c.strokeStyle='#89acbb58';c.beginPath();c.moveTo(...a);c.lineTo(...b);c.stroke()}});
// sensor point cloud, intentionally synthetic points and not a recovered real map
if(st.pointcloud){for(let k=0;k<650;k++){let x=rand(k+5)*12,y=rand(k*9+12)*9.4;if(rand(k+23)>.44)continue;let [cx,cy]=p(x,y,rand(k+777)*.22);c.fillStyle=k%9===0?'#a1d8bb93':'#76baba55';c.fillRect(cx,cy,1.2,1.2)}}
// Imported point-cloud source: user-provided metric coordinates; registration is unknown.
if(st.worldPoints?.length){let skip=Math.max(1,Math.floor(st.worldPoints.length/2700));for(let i=0;i<st.worldPoints.length;i+=skip){let [x,y,z]=st.worldPoints[i];let [cx,cy]=p(x,y,z);c.fillStyle='#c0f078ae';c.fillRect(cx,cy,2.0,2.0)}}
// Mesh vertices are normalized solely for display; no physics/collision semantics assumed.
if(st.modelVerts?.length){for(let i=0;i<st.modelVerts.length;i++){let [x,y,z]=st.modelVerts[i],pos=p(x,y,z);c.fillStyle='#ffca79b2';c.fillRect(pos[0],pos[1],1.4,1.4)}}
if(st.bounds){let z={x1:3.75,x2:5.65,y1:2.3,y2:4.55};let bounds=[p(z.x1,z.y1,.05),p(z.x2,z.y1,.05),p(z.x2,z.y2,.05),p(z.x1,z.y2,.05)];poly(c,bounds,'#bd645a30','#e68c6c',1.3);c.save();c.setLineDash([4,4]);poly(c,bounds,null,'#ec9a779c',1);c.restore();let [lx,ly]=p(z.x1,z.y2,.07);c.font='700 9px ui-monospace,monospace';c.fillStyle='#f3a18d';c.fillText('KEEP-OUT A',lx,ly-12)}
let prefix=st.rows.slice(0,st.idx+1);const drawLine=(data,col,width=2.4,dash=[])=>{if(!data.length)return;c.beginPath();data.forEach((r,i)=>{let v=p(r.x_m,r.y_m,.16);if(i===0)c.moveTo(...v);else c.lineTo(...v)});c.setLineDash(dash);c.strokeStyle=col;c.lineWidth=width;c.lineJoin='round';c.lineCap='round';c.stroke();c.setLineDash([])};
drawLine(st.rows,'#5adfe34c',2,[3,5]);drawLine(prefix,st.report?.process_accepted?'#99e344':'#ffb264',3.2);
// floor goal marker
let [gx,gy]=p(10.5,7.2,.1);c.beginPath();c.arc(gx,gy,9,0,Math.PI*2);c.strokeStyle='#a8eb45';c.lineWidth=2;c.stroke();c.fillStyle='#a2dd63';c.font='700 9px monospace';c.fillText('GOAL',gx+14,gy-3);
let r=st.rows[st.idx];let a=p(r.x_m,r.y_m,0),u=p(r.x_m,r.y_m,.38);let robotG1=st.current?.name.includes('G1');if(robotG1){box(r.x_m-.15,r.y_m-.13,0,.3,.27,.78,'#b0c4cb','#d5eaf0');let head=p(r.x_m,r.y_m,1.0);c.beginPath();c.arc(...head,5,0,2*Math.PI);c.fillStyle='#cfe8e1';c.fill();c.strokeStyle='#79e8c8';c.stroke()}else{box(r.x_m-.27,r.y_m-.24,0,.54,.48,.24,'#a8c0c6','#cbf0e7');let cam=p(r.x_m+.13,r.y_m+.04,.41);c.beginPath();c.arc(...cam,3,0,2*Math.PI);c.fillStyle='#9ef1da';c.fill()}
let rr=4+3*Math.sin(performance.now()/600);c.beginPath();c.ellipse(a[0],a[1],rr*2,rr,0,0,Math.PI*2);c.strokeStyle='#7deab277';c.stroke();if(st.pointcloud){for(let k=0;k<35;k++){let ang=k/35*Math.PI*2;let pt=p(r.x_m+1.6*Math.cos(ang),r.y_m+1.6*Math.sin(ang),.03);c.fillStyle='#7dd6c69c';c.fillRect(pt[0],pt[1],1.2,1.2)}}
let pt=p(r.x_m,r.y_m,.9);c.fillStyle='#d9f6e9';c.font='700 10px monospace';c.fillText(robotG1?'G1 / SURROGATE':'M3 PRO / SURROGATE',pt[0]+10,pt[1]-8);
c.strokeStyle='#344f5788';c.beginPath();c.moveTo(...p(0,0));c.lineTo(...p(0,9.4));c.moveTo(...p(12,0));c.lineTo(...p(12,9.4));c.stroke();
}
function drawCamera(id,index){let cv=ctx2(id);if(!cv)return;let {c,w,h}=cv;let r=st.rows[st.idx]||{x_m:0,y_m:0},s=index-1, horizon=h*.40;let bg=c.createLinearGradient(0,0,0,h);bg.addColorStop(0,'#273c49');bg.addColorStop(.4,'#44616a');bg.addColorStop(.41,'#2a3e44');bg.addColorStop(1,'#192f37');c.fillStyle=bg;c.fillRect(0,0,w,h);
// artificial warehouse camera reference
c.fillStyle='#31434b';poly(c,[[0,h],[w,h],[w*.68,horizon],[w*.31,horizon]],'#31434b');
for(let k=0;k<7;k++){let off=1/(k+1);let y=horizon+(h-horizon)*(1-off);c.strokeStyle='#97b1a42c';c.lineWidth=1;c.beginPath();c.moveTo(0,y);c.lineTo(w,y);c.stroke()}
for(let side of [-1,1]){for(let j=0;j<3;j++){let depth=j/3,factor=1-depth*.6,fw=24*factor,fh=(h*.53)*factor;let x=(side<0?0:w)-side*(10+j*11)*factor+(side<0?0:-fw),y=horizon+(j*.16*h);c.fillStyle=side===-1?'#3f5862':'#435965';c.fillRect(x,y,fw,fh);c.strokeStyle='#7e9e9b5e';c.strokeRect(x,y,fw,fh);for(let a=1;a<=3;a++){c.strokeStyle='#9caeaf33';c.beginPath();c.moveTo(x,y+a*fh/4);c.lineTo(x+fw,y+a*fh/4);c.stroke()}}}
let dx=(r.x_m/12-.5)*w*.18+s*w*.03,center=w*.52+dx;poly(c,[[center-16,h*.83],[center+16,h*.83],[center+10,h*.59],[center-10,h*.59]],'#7a9383','#aad6c0',1);
c.strokeStyle='#93eb9e';c.setLineDash([4,3]);c.lineWidth=1.5;c.strokeRect(center-22,h*.52,44,h*.35);c.setLineDash([]);
for(let x=0;x<w;x+=9){c.fillStyle='#84bab60c';c.fillRect(x,0,1,h)}c.fillStyle='#061015a1';c.fillRect(0,h-17,w,17);c.fillStyle='#b6d6d3';c.font='8px monospace';c.fillText('RGB 640×480 • SYNTHETIC',8,h-6);c.fillStyle='#8dea98';c.fillText(num(frameSeconds(st.idx),2)+'s',w-45,h-6)}
function drawSignals(){let o=ctx2('#signalCanvas');if(!o||!st.rows.length)return;let {c,w,h}=o;c.fillStyle='#111a20';c.fillRect(0,0,w,h);for(let k=0;k<5;k++){let y=9+k*(h-18)/4;c.beginPath();c.moveTo(0,y);c.lineTo(w,y);c.strokeStyle='#283e467f';c.lineWidth=.8;c.stroke()}let series=[['speed_m_s','#99d83f',1.5],['clearance_m','#6aa9df',1.1],['latency_ms','#e5a15b',50]];for(let [key,col,max] of series){c.beginPath();st.rows.forEach((r,i)=>{let x=8+(w-16)*i/Math.max(1,st.rows.length-1),y=h-10-(Math.min(max,r[key]??0)/max)*(h-22);if(!i)c.moveTo(x,y);else c.lineTo(x,y)});c.lineWidth=1.8;c.strokeStyle=col;c.stroke()}let x=8+(w-16)*st.idx/Math.max(1,st.rows.length-1);c.beginPath();c.moveTo(x,0);c.lineTo(x,h);c.strokeStyle='#e8efed';c.lineWidth=1;c.stroke()}
function drawEventTrack(){let el=$('#eventTrack');if(!st.report)return;let n=st.rows.length||1;el.innerHTML=st.report.events.filter(e=>e.severity==='critical').map(e=>`<i class="track-marker" style="left:${Math.min(99,100*e.index/(n-1))}%"></i>`).join('')}
function renderAll(){if(!st.rows.length)return;tickVisual();drawCamera('#cam1',0);drawCamera('#cam2',1);drawCamera('#cam3',2);drawScene();drawSignals()}
function anim(now){if(st.playing&&st.rows.length){let delta=Math.min(150,Math.max(0,now-st.lastTime||0));let ti=st.rows[st.idx].t_ns+delta*1e6*st.speed;while(st.idx+1<st.rows.length&&st.rows[st.idx+1].t_ns<=ti)st.idx++;if(st.idx>=st.rows.length-1){st.playing=false;$('#playBtn').textContent='▶'}renderAll()}st.lastTime=now;requestAnimationFrame(anim)}
function renderRegistry(){let q=$('#registrySearch').value.toLowerCase();let all=st.assets.filter(a=>!q||[a.name,a.kind,a.sha256,a.origin].join(' ').toLowerCase().includes(q));$('#registryCount').textContent=`${all.length} indexed assets`;$('#registryTable').innerHTML=`<table class="data-table"><thead><tr><th>Asset / Session</th><th>Format</th><th>Evidence class</th><th>Size</th><th>SHA-256</th><th>Action</th></tr></thead><tbody>${all.map(a=>`<tr><td>${esc(a.name)}</td><td>${esc(a.kind)}</td><td>${badge(a)}</td><td>${(a.size/1048576).toFixed(2)} MB</td><td class="mono">${esc(a.sha256.slice(0,14))}…</td><td><button class="mini-btn" data-open="${a.id}">${a.kind==='TRAJECTORY'?'REPLAY':'DETAILS'}</button></td></tr>`).join('')}</tbody></table>`;$$('[data-open]').forEach(n=>n.onclick=()=>openAsset(n.dataset.open))}
function renderWorld(){let models=st.assets.filter(a=>['MODEL_3D','CAD','ROBOT_DESCRIPTION','POINT_CLOUD'].includes(a.kind));$('#geometrySelect').innerHTML=models.map(a=>`<option value="${a.id}">${esc(a.name)}</option>`).join('')||'<option value="">No imported geometry</option>';$('#modelRegistry').innerHTML=models.length?`<table class="data-table"><thead><tr><th>Name</th><th>Type</th><th>Source</th></tr></thead><tbody>${models.map(a=>`<tr><td>${esc(a.name)}</td><td>${esc(a.kind)}</td><td>${esc(a.origin)}</td></tr>`).join('')}</tbody></table>`:'<div class="result-box">No external model imported. Current viewport uses explicitly uncalibrated M3/G1 surrogate geometry.</div>';$('#worldCapabilities').innerHTML=[['First-party USD/MJCF/SDF reference scene','EXPORT IMPLEMENTED'],['URDF / CAD / mesh inspection','FORMAT INSPECTION'],['Native Isaac Lab physics','RUNTIME PROBE IN WORKBENCH'],['Native MuJoCo physics','RUNTIME PROBE IN WORKBENCH'],['CAD fidelity and inertia','NOT CALIBRATED'],['Point cloud registration','NOT YET VALIDATED']].map(([a,b])=>`<div class="cap-row"><span>${a}</span><strong class="pending">${b}</strong></div>`).join('')}
async function inspectGeometry(){let id=$('#geometrySelect').value;if(!id)return toast('Import URDF, mesh or ASCII point cloud before inspection.',true);let a=st.assets.find(x=>x.id===id);if(!a)return;try{let j=await api(a.kind==='POINT_CLOUD'?'/api/reconstruct/'+id:'/api/geometry/'+id);let r=j.reconstruction||j.geometry;$('#geometryReadout').textContent=JSON.stringify({...r,vertices_sampled:undefined,points:undefined,occupancy_cells:undefined},null,2);st.worldPoints=null;st.modelVerts=null;
 if(r.points){let mins=r.bounds_m.min;st.worldPoints=r.points.map(pt=>[pt[0]-mins[0]+.9,pt[1]-mins[1]+.9,pt[2]-mins[2]]);toast('Projected point-cloud samples. Sensor registration and calibration remain unverified.')}
 if(r.vertices_sampled){let v=r.vertices_sampled,b=r.bounds_in_file_units,den=Math.max(...b[1].map((x,i)=>x-b[0][i]),.01);st.modelVerts=v.map(pt=>[(pt[0]-b[0][0])/den*3.4+4.6,(pt[1]-b[0][1])/den*3.4+3.1,(pt[2]-b[0][2])/den*2.8]);toast('Imported mesh vertex preview. Geometry units are unverified.')}
 drawScene('#worldCanvas');}catch(e){toast(e.message,true)}}
function renderAssuranceCards(){let s=st.report,fields=[['CONTRACT STATUS',s?(s.process_accepted===null?'NO CONTRACT':s.process_accepted?'PASS':'REVIEW'):'PENDING','Against recorded trace; not physical validation'],['VIOLATION TIMELINE',s?(s.violations===null?'NOT SCORED':s.violations+' events'):'—','Geometry / timestamp / dropout categories'],['RECOVERY DEADLINE','NOT TESTED','No independent fault-recovery timestamps'],['EVIDENCE COMPLETENESS',s?s.samples+' parsed':'—','Mission interval and sensors not attested'],['FAILURE ATTRIBUTION','HYPOTHESIS ONLY','No causal classification without reference truth'],['COST & LATENCY',s?(s.max_latency_ms===null?'NOT RECORDED':num(s.max_latency_ms,1)+' ms'):'—','Max supplied latency; energy not measured']];$('#assuranceMetrics').innerHTML=fields.map(([k,v,d])=>`<div class="assurance-metric"><span>${k}</span><strong>${esc(v)}</strong><small>${esc(d)}</small></div>`).join('')}
function renderMediaOptions(){let media=st.assets.filter(a=>a.kind==='VIDEO'||a.kind==='IMAGE');let select=$('#cameraSource'),old=select.value;select.innerHTML='<option value="">SYNTHETIC ONLY</option>'+media.map(a=>`<option value="${a.id}">${esc(a.name)}</option>`).join('');if([...select.options].some(o=>o.value===old))select.value=old}
async function pickCameraMedia(id){const el=$('#mediaOverlay');el.replaceChildren();if(mediaBlobUrl){URL.revokeObjectURL(mediaBlobUrl);mediaBlobUrl=null}if(!id){el.classList.add('hidden');return}let a=st.assets.find(x=>x.id===id);if(!a)return;try{let r=await fetch('/api/assets/'+id+'/raw',{headers:{'x-veap-token':st.token}});if(!r.ok)throw Error('Media access failed: '+r.status);mediaBlobUrl=URL.createObjectURL(await r.blob());let media=document.createElement(a.kind==='VIDEO'?'video':'img');media.src=mediaBlobUrl;if(a.kind==='VIDEO'){media.controls=true;media.muted=true;media.preload='metadata'}else media.alt='Uploaded camera/image evidence';el.appendChild(media);let cap=document.createElement('small');cap.textContent='UPLOAD / UNSYNCHRONIZED / UNATTESTED';el.appendChild(cap);el.classList.remove('hidden')}catch(e){toast(e.message,true)}}
async function loadInbox(){
 let el=$('#inboxResults');el.textContent='Scanning VEAP local inbox...';
 try{let v=await api('/api/inbox');
    if(!v.files.length){el.textContent='No local staged files. Place MCAP or CAD files in '+v.root+' using rsync or your file manager.';return}
    el.innerHTML=`<b>Local staging: ${esc(v.root)}</b>`+v.files.map(x=>`<div class="studio-inline" style="margin:7px 0"><span>${esc(x.name)} · ${(x.bytes/1048576).toFixed(1)} MiB</span><button class="mini-btn" data-inbox="${esc(x.name)}">Import source</button></div>`).join('');
    $$('[data-inbox]').forEach(btn=>btn.onclick=async()=>{try{let j=await api('/api/inbox/import',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:btn.dataset.inbox})});toast('Original evidence indexed: '+j.asset.sha256.slice(0,14));await refreshAssets();await loadInbox()}catch(e){toast(e.message,true)}})
 }catch(e){el.textContent='Local inbox discovery failed: '+e.message}
}
let integrationCache=null;
async function renderConnectors(){
  let root=$('#connectorGrid');
  root.innerHTML='<div class="result-box">Probing installed local engine environments…</div>';
  try{
    const [payload,jobs]=await Promise.all([api('/api/integrations'),api('/api/jobs')]);
    integrationCache=payload;
    root.innerHTML=payload.connectors.map(c=>{
      let ready=['AVAILABLE_LOCAL','MODULES_AVAILABLE','ROS_DECODER_AVAILABLE','CLI_FOUND','CONTAINER_READER_AVAILABLE'].includes(c.status);
      let cls=ready?'status-ready':(c.status==='NO_LIVE_LINK'?'status-muted':'status-fail');
      return `<div class="connector"><h3>${esc(c.name)}</h3><p>${esc(c.description)}</p><div class="status ${cls}">● ${esc(c.status.replaceAll('_',' '))}</div><small>${esc(c.claim)}</small>${c.runtime?`<small>${esc(c.runtime)}</small>`:''}</div>`
    }).join('');
    renderNativeJobs(jobs.jobs);
  }catch(e){root.innerHTML=`<div class="result-box">Unable to inspect engine runtime: ${esc(e.message)}</div>`}
  updateSourceOptions();
  $('#recordPlan').textContent=`# VEAP read-only ROS2 recording plan (execute manually after source qualification)\nsource /opt/ros/humble/setup.bash\nexport ROS_DOMAIN_ID=30\nros2 topic list -t\nros2 bag list storage\n# Requires an available ROS2 MCAP plugin and valid sensor graph.\nros2 bag record -s mcap -o veap_m3_session \
  /scan0 /scan1 /odom_raw /imu/data_raw /cmd_vel /tf\n# Not run by the browser. Do not run on the unqualified Jetson.`;
}
function updateSourceOptions(){
  let sels=[['#mcapSource',a=>a.kind==='MCAP','No MCAP files'],['#lerobotSource',a=>a.kind==='TRAJECTORY','No trajectories']];
  for(let [sel,filter,label] of sels){let el=$(sel);if(!el)continue;let old=el.value;let list=st.assets.filter(filter);el.innerHTML=list.map(a=>`<option value="${a.id}">${esc(a.name)} · ${esc(a.origin)}</option>`).join('')||`<option value="">${label}</option>`;if(list.some(a=>a.id===old))el.value=old}
}
function renderNativeJobs(jobs){
  let table=$('#nativeJobTable');if(!table)return;
  if(!jobs.length){table.innerHTML='<div class="result-box">No native jobs yet. Start an engine test or export a reference world.</div>';return}
  table.innerHTML=`<table class="job-table"><thead><tr><th>Job</th><th>Runtime</th><th>State</th><th>Result</th></tr></thead><tbody>`+jobs.map(j=>{
    let state=j.status==='COMPLETED'?'complete':j.status==='FAILED'?'failed':'running';
    let result=j.status==='COMPLETED'?(j.asset_id?'Indexed evidence '+j.asset_id.slice(0,8):'Artifacts available'):(j.error||'Pending');
    let links=j.kind==='scene_export'&&j.status==='COMPLETED'?` <button class="mini-btn" data-job-file="${j.id}:veap_reference.usda">USD</button> <button class="mini-btn" data-job-file="${j.id}:veap_reference.xml">MJCF</button> <button class="mini-btn" data-job-file="${j.id}:veap_reference.sdf">SDF</button> <button class="mini-btn" data-job-file="${j.id}:veap_reference.gltf">glTF</button>`:'';
    return `<tr><td><code>${esc(j.id.slice(0,10))}</code></td><td>${esc(j.kind)}</td><td class="${state}">${esc(j.status)}</td><td>${esc(result)}${links}</td></tr>`
  }).join('')+'</tbody></table>';
  $$('[data-job-file]').forEach(btn=>btn.onclick=async()=>{try{let [id,file]=btn.dataset.jobFile.split(':');let r=await fetch('/api/jobs/'+id+'/artifact/'+file,{headers:{'x-veap-token':st.token}});if(!r.ok)throw Error('File retrieval failed '+r.status);let url=URL.createObjectURL(await r.blob());let a=document.createElement('a');a.href=url;a.download=file;a.click();setTimeout(()=>URL.revokeObjectURL(url),2000)}catch(e){toast(e.message,true)}});
}
async function createNativeJob(kind,source_id=null){
  if(['mcap_decode','lerobot_dataset'].includes(kind)&&!source_id)return toast('Select a source asset first',true);
  try{
    let j=await api('/api/jobs',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({kind,source_id})});
    toast('VEAP job queued: '+kind+' — '+j.job.id.slice(0,8));
    await renderConnectors();
  }catch(e){toast('Cannot queue native operation: '+e.message,true)}
}
async function createFault(){if(!$('#faultSource').value)return toast('Import a trajectory first.',true);let request={asset_id:$('#faultSource').value,fault:$('#faultType').value,severity:Number($('#faultSeverity').value),seed:Number($('#faultSeed').value)};try{let r=await api('/api/counterfactual',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(request)});$('#faultResult').textContent=`Generated: ${r.asset.name}\nSource: SYNTHETIC COUNTERFACTUAL\nVerdict: ${r.report.verdict}\nEpisodes: 1 · Seed: ${request.seed}\nInferred physical safety: NOT ESTABLISHED`;await refreshAssets(r.asset.id);openPage('replay');toast('Counterfactual created and indexed. This is an analytic trace perturbation only.')}catch(e){toast(e.message,true)}}
function openModal(){st.modal=true;$('#modalOverlay').classList.remove('hidden');$('#uploadStatus').textContent='Maximum file size 128 MiB. Original input is copied into protected local storage.'}
function closeModal(){st.modal=false;$('#modalOverlay').classList.add('hidden')}
async function doUpload(){let file=$('#fileInput').files[0];if(!file)return toast('Select a file before importing.',true);if(file.size>128*1048576)return toast('File exceeds local 128 MiB limit.',true);let fd=new FormData();fd.append('file',file);fd.append('classification',$('#fileClass').value);$('#uploadStatus').textContent='Validating, hashing and indexing local evidence...';try{let j=await api('/api/assets',{method:'POST',body:fd});closeModal();$('#fileInput').value='';toast(`Imported ${file.name}. Provenance: UNATTESTED.`);await refreshAssets(j.asset.kind==='TRAJECTORY'?j.asset.id:null);if(j.asset.kind!=='TRAJECTORY')openPage('data')}catch(e){$('#uploadStatus').textContent='Import rejected: '+e.message;toast(e.message,true)}}
async function loadContracts(){
 try{let j=await api('/api/contracts');let el=$('#contractSelect');let old=el.value;el.innerHTML='<option value="">No matching contract</option>'+j.contracts.map(c=>`<option value="${c.id}">${esc(c.contract.name)} · ${c.id.slice(0,10)}</option>`).join('');if(j.contracts.some(c=>c.id===old))el.value=old}
 catch(e){toast('Contract list unavailable: '+e.message,true)}
}
async function registerContract(){
 try{let body=JSON.parse($('#contractJson').value);let j=await api('/api/contracts',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});await loadContracts();$('#contractSelect').value=j.id;toast('Immutable contract registered: '+j.id.slice(0,12))}
 catch(e){toast('Contract registration failed: '+e.message,true)}
}
async function evaluateContract(){
 let c=$('#contractSelect').value,a=$('#assuranceSource').value;
 if(!c||!a)return toast('Select registered contract and source trace first.',true);
 try{let result=await api('/api/contracts/'+c+'/evaluate/'+a,{method:'POST'});$('#reportText').textContent=JSON.stringify(result,null,2);st.reportExport={...result,report_id:c.slice(0,12)};$('#downloadJson').disabled=false;
 toast('Separate-process recorded-trace monitor completed. Physical truth remains unverified.')}
 catch(e){toast('External monitor unavailable: '+e.message,true)}
}
async function createAssurance(){if(!$('#assuranceSource').value)return toast('No trajectory selected.',true);try{let src=$('#assuranceSource').value,ref=$('#assuranceCompare').value;let r=await api('/api/reports',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({source_id:src,candidate_id:ref||null})});st.reportExport=r;$('#reportText').textContent=JSON.stringify(r,null,2);$('#downloadJson').disabled=false;toast('Report generated with explicit evidence and limitation fields.')}catch(e){toast(e.message,true)}}
function download(name,value,mime='application/json'){let blob=new Blob([value],{type:mime}),url=URL.createObjectURL(blob);let a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)}
function setSidebarCollapsed(collapsed){
  let shell=$('.shell');if(!shell)return;
  shell.classList.toggle('sidebar-collapsed',collapsed);
  let icon=$('#sidebarSliderIcon');if(icon)icon.textContent=collapsed?'›':'‹';
  ['#sidebarCollapseBtn','#sidebarSliderBtn'].forEach(sel=>{let b=$(sel);if(b)b.setAttribute('aria-expanded',String(!collapsed))});
  try{localStorage.setItem('veap-sidebar-collapsed',collapsed?'1':'0')}catch{}
  requestAnimationFrame(()=>{renderAll();if(st.view==='world')drawScene('#worldCanvas')});
  setTimeout(()=>{renderAll();if(st.view==='world')drawScene('#worldCanvas')},240);
}
function toggleSidebar(){
  let shell=$('.shell');if(!shell)return;
  setSidebarCollapsed(!shell.classList.contains('sidebar-collapsed'));
}
function initSidebarSlider(){
  let shell=$('.shell'),slider=$('#sidebarSlider'),btn=$('#sidebarSliderBtn'),collapseBtn=$('#sidebarCollapseBtn');
  if(!shell||!slider)return;
  try{
    let savedW=Number(localStorage.getItem('veap-sidebar-width'));
    if(savedW>=180&&savedW<=440)shell.style.setProperty('--sidebar-w',savedW+'px');
    if(localStorage.getItem('veap-sidebar-collapsed')==='1')setSidebarCollapsed(true);
  }catch{}
  if(collapseBtn)collapseBtn.onclick=()=>toggleSidebar();
  if(btn)btn.onclick=e=>{e.stopPropagation();toggleSidebar()};
  let dragging=false,moved=false,startX=0;
  slider.addEventListener('pointerdown',e=>{
    if(e.target.closest('#sidebarSliderBtn'))return;
    dragging=true;moved=false;startX=e.clientX;
    shell.classList.add('sidebar-dragging');
    slider.setPointerCapture(e.pointerId);
  });
  slider.addEventListener('pointermove',e=>{
    if(!dragging)return;
    if(Math.abs(e.clientX-startX)>3)moved=true;
    let railW=$('.rail')?.getBoundingClientRect().width||51;
    let w=e.clientX-railW;
    if(w<110){
      setSidebarCollapsed(true);
    }else{
      let clamped=Math.max(180,Math.min(440,Math.round(w)));
      shell.style.setProperty('--sidebar-w',clamped+'px');
      if(shell.classList.contains('sidebar-collapsed'))setSidebarCollapsed(false);
      try{localStorage.setItem('veap-sidebar-width',String(clamped))}catch{}
      renderAll();if(st.view==='world')drawScene('#worldCanvas');
    }
  });
  const endDrag=()=>{if(!dragging)return;dragging=false;shell.classList.remove('sidebar-dragging');if(!moved)toggleSidebar();renderAll();if(st.view==='world')drawScene('#worldCanvas')};
  slider.addEventListener('pointerup',endDrag);
  slider.addEventListener('pointercancel',endDrag);
  slider.addEventListener('dblclick',()=>{shell.style.setProperty('--sidebar-w','242px');try{localStorage.removeItem('veap-sidebar-width')}catch{};setSidebarCollapsed(false)});
  $$('.side-section.collapsible').forEach(sec=>{
    sec.onclick=()=>{
      let target=$('#'+sec.dataset.collapse);if(!target)return;
      let expanded=sec.getAttribute('aria-expanded')!=='false';
      sec.setAttribute('aria-expanded',String(!expanded));
      target.classList.toggle('collapsed',expanded);
    };
  });
}
function bind(){
initSidebarSlider();
$$('.railbutton[data-page]').forEach(b=>b.onclick=()=>{if(st.view===b.dataset.page&&$('.shell')?.classList.contains('sidebar-collapsed'))setSidebarCollapsed(false);openPage(b.dataset.page)});$$('[data-side]').forEach(b=>b.onclick=()=>setSide(b.dataset.side));$('#sideSearch').oninput=renderSources;
$$('[data-inspect]').forEach(b=>b.onclick=()=>{$$('[data-inspect]').forEach(x=>x.classList.toggle('active',x===b));$$('.inspector-body').forEach(x=>x.classList.add('hidden'));$('#inspector'+b.dataset.inspect[0].toUpperCase()+b.dataset.inspect.slice(1)).classList.remove('hidden')});
$('#scrub').oninput=e=>{st.playing=false;$('#playBtn').textContent='▶';seek(Number(e.target.value))};$('#playBtn').onclick=()=>{if(st.idx===st.rows.length-1)seek(0);st.playing=!st.playing;$('#playBtn').textContent=st.playing?'❚❚':'▶'};
$('#skipBack').onclick=()=>{st.playing=false;$('#playBtn').textContent='▶';seek(0)};$('#skipForward').onclick=()=>{st.playing=false;$('#playBtn').textContent='▶';seek(st.rows.length-1)};$('#playSpeed').onchange=e=>st.speed=Number(e.target.value);
$('#cameraReset').onclick=()=>{st.angle=-.72;st.zoom=1;drawScene()};$('#togglePoints').onclick=e=>{st.pointcloud=!st.pointcloud;e.currentTarget.classList.toggle('selected',st.pointcloud);drawScene()};$('#toggleBounds').onclick=e=>{st.bounds=!st.bounds;e.currentTarget.classList.toggle('selected',st.bounds);drawScene()};
let canvas=$('#sceneCanvas'),drag=false,prev=0;canvas.addEventListener('pointerdown',e=>{drag=true;prev=e.clientX;canvas.setPointerCapture(e.pointerId)});canvas.addEventListener('pointermove',e=>{if(!drag)return;st.angle+=(e.clientX-prev)*.007;prev=e.clientX;drawScene()});canvas.addEventListener('pointerup',()=>drag=false);canvas.addEventListener('wheel',e=>{e.preventDefault();st.zoom=Math.max(.6,Math.min(2.4,st.zoom*(e.deltaY>0?.92:1.08)));drawScene()},{passive:false});
$('#runCompare').onclick=()=>doCompare();$('#compareSelect').onchange=()=>doCompare(false);$('#btnCompare').onclick=()=>{$('#compareSelect').focus();doCompare()};$('#btnRecord').onclick=()=>{openPage('connectors');toast('Record plan shown. Live capture is not enabled in this research pilot.')};$('#dataRecord').onclick=()=>openPage('connectors');$('#inspectInbox').onclick=loadInbox;
['#btnUpload','#dataImport','#worldImport'].forEach(k=>$(k).onclick=openModal);$('#closeModal').onclick=closeModal;$('#cancelModal').onclick=closeModal;$('#modalOverlay').onclick=e=>{if(e.target===$('#modalOverlay'))closeModal()};$('#uploadNow').onclick=doUpload;
$('#assetClose').onclick=closeAssetDetails;$('#assetCancel').onclick=closeAssetDetails;$('#assetSave').onclick=saveAssetDetails;$('#assetOverlay').onclick=e=>{if(e.target===$('#assetOverlay'))closeAssetDetails()};$('#worldReconstruct').onclick=()=>{openPage('data');$('#registrySearch').value='POINT_CLOUD';renderRegistry();toast('Import an XYZ/PLY point cloud for future reconstruction. No calibrated registration is currently implemented.')};$('#worldEngines').onclick=()=>openPage('connectors');$('#previewGeometry').onclick=inspectGeometry;$('#cameraSource').onchange=e=>pickCameraMedia(e.target.value);$('#registrySearch').oninput=renderRegistry;
$('#faultSeverity').oninput=e=>$('#faultSeverityValue').textContent=num(e.target.value,1);$('#createFault').onclick=createFault;$('#buildReport').onclick=createAssurance;$('#registerContract').onclick=registerContract;$('#evaluateContract').onclick=evaluateContract;$('#downloadJson').onclick=()=>{if(st.reportExport)download('veap-assurance-'+st.reportExport.report_id.slice(0,9)+'.json',JSON.stringify(st.reportExport,null,2))};$('#exportReport').onclick=()=>{openPage('assurance');if(st.current)$('#assuranceSource').value=st.current.id};
$('#comparePhysics').onclick=async()=>{try{let j=await api('/api/jobs');let m=j.jobs.find(x=>x.kind==='mujoco_fall'&&x.status==='COMPLETED');let i=j.jobs.find(x=>x.kind==='isaac_fall'&&x.status==='COMPLETED');if(!m||!i)return toast('Native MuJoCo and Isaac runs must both complete first.',true);let result=await api('/api/physics/compare',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({reference_job_id:m.id,candidate_job_id:i.id})});$('#nativeCompareReport').textContent=JSON.stringify(result,null,2);toast('3D discrepancy calculated; physics calibration remains unvalidated.')}catch(e){toast(e.message,true)}};$('#refreshIntegrations').onclick=renderConnectors;$('#runMujoco').onclick=()=>createNativeJob('mujoco_fall');if($('#runGazebo'))$('#runGazebo').onclick=()=>createNativeJob('gazebo_fall');$('#runIsaac').onclick=()=>createNativeJob('isaac_fall');$('#buildScene').onclick=()=>createNativeJob('scene_export');$('#worldExportScene').onclick=()=>{openPage('connectors');createNativeJob('scene_export')};$('#decodeMcap').onclick=()=>createNativeJob('mcap_decode',$('#mcapSource').value);$('#makeLeRobot').onclick=()=>createNativeJob('lerobot_dataset',$('#lerobotSource').value);
$('#copyRecord').onclick=()=>navigator.clipboard.writeText($('#recordPlan').textContent).then(()=>toast('Recording command copied; execute only after live topics and storage are qualified.')).catch(()=>toast('Clipboard permission denied; select the text and copy it.'));
$('#shortcuts').onclick=()=>toast('Shortcuts: Space = play/pause · [ or Ctrl+B = toggle sidebar · / = source search · 1–6 = workspace tabs · Arrow keys = seek');$('#about').onclick=()=>toast('VEAP R0.3: first-party engineering studio. Native jobs only when configured. No live robot control or safety certification.');
document.addEventListener('keydown',e=>{if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='b'){e.preventDefault();toggleSidebar();return}if(e.target instanceof HTMLInputElement||e.target instanceof HTMLTextAreaElement||e.target instanceof HTMLSelectElement)return;if(e.key==='['){e.preventDefault();toggleSidebar()}if(e.key===' '){e.preventDefault();$('#playBtn').click()}if(e.key==='ArrowRight')seek(st.idx+1);if(e.key==='ArrowLeft')seek(st.idx-1);if(e.key==='/'){e.preventDefault();$('#sideSearch').focus()}if(/^[1-6]$/.test(e.key))openPage(['replay','world','data','policy','assurance','connectors'][Number(e.key)-1]);if(e.key==='Escape'){closeModal();closeAssetDetails()}});window.addEventListener('resize',()=>{renderAll();if(st.view==='world')drawScene('#worldCanvas')});
}
/* Policy Lab: VEAP Benchmark Observatory & Evidence Ledger */
const bench={scenarios:[],runs:[],selectedScenario:null,selectedRun:null,auth:'',polling:false,initialized:false,tab:'runner'};
let benchScene=null;
function benchText(id,val){const el=document.getElementById(id);if(el)el.textContent=String(val)}
function benchAuthModal(show){const m=$('#benchAuthModal');if(!m)return;m.classList.toggle('hidden',!show);if(show)$('#benchAuthInput')?.focus()}
async function benchApi(path,options={}){
  const headers={...(options.headers||{})};
  if(bench.auth)headers.Authorization='Bearer '+bench.auth;
  if(options.body&&!headers['Content-Type'])headers['Content-Type']='application/json';
  const res=await fetch(path,{...options,headers,cache:'no-store'});
  if(res.status===401){benchAuthModal(true);throw Error('API authentication required')}
  if(!res.ok){let msg=res.statusText;try{const j=await res.json();msg=typeof j.detail==='string'?j.detail:JSON.stringify(j.detail)}catch{}throw Error(msg||`HTTP ${res.status}`)}
  return options.blob?res.blob():res.json();
}
function openPolicyTab(tab){
  bench.tab=tab;
  $$('.policy-tab').forEach(b=>b.classList.toggle('active',b.dataset.policyTab===tab));
  const map={runner:'policyTabRunner',scenarios:'policyTabScenarios',ledger:'policyTabLedger',research:'policyTabResearch',counterfactual:'policyTabCounterfactual'};
  Object.entries(map).forEach(([k,id])=>{const el=document.getElementById(id);if(el)el.classList.toggle('active',k===tab)});
  if(tab==='runner'&&benchScene)requestAnimationFrame(()=>benchScene.resize());
}
function benchCurrentScenario(){return bench.scenarios.find(s=>s.id===bench.selectedScenario)||null}
function benchScenarioSelect(id){
  const s=bench.scenarios.find(x=>x.id===id);if(!s)return;
  bench.selectedScenario=id;
  const sel=$('#benchScenarioSelect');if(sel)sel.value=id;
  benchText('benchScenarioLabel',s.title);
  benchText('benchScenarioDesc',s.description);
  if(benchScene)benchScene.setScenario(s);
  if(!bench.selectedRun||bench.selectedRun.scenario_id!==id){
    if(benchScene)benchScene.setEvents([]);
    benchSetRunInfo(null);
    benchText('benchSceneStatus','PREVIEW');
  }
}
function benchRenderScenarios(){
  const parent=$('#benchScenarioCards');if(!parent)return;
  parent.replaceChildren();
  for(const s of bench.scenarios){
    const card=document.createElement('article');card.className='bench-scenario-card';
    card.innerHTML=`<div class="bench-scenario-kicker"><span>${esc(s.family.toUpperCase())} / ${esc(s.id)}</span><span>${esc(s.split.toUpperCase())}</span></div><h3>${esc(s.title)}</h3><p>${esc(s.description)}</p><div class="bench-scenario-foot"><span>${s.waypoints.length} GOALS · ${s.obstacles.length} OBSTACLES · ${s.faults.length} FAULTS</span><button class="mini-btn" type="button">OPEN IN LAB →</button></div>`;
    card.querySelector('button').addEventListener('click',()=>{benchScenarioSelect(s.id);openPolicyTab('runner')});
    parent.appendChild(card);
  }
}
function benchRenderRuns(){
  const p=$('#benchRunTable');if(!p)return;
  p.replaceChildren();
  benchText('benchRunCount',bench.runs.length+' RUNS');
  if(!bench.runs.length){const tr=document.createElement('tr');tr.innerHTML='<td colspan="7">No experiments recorded yet.</td>';p.appendChild(tr);return}
  for(const run of bench.runs){
    const tr=document.createElement('tr');tr.className='clickable-row';
    const ver=run.summary?.verified;
    const status=run.status==='completed'?(ver?'VERIFIED':'NOT VERIFIED'):run.status.toUpperCase();
    const cls=ver?'green-text':run.status==='completed'?'red-text':'';
    tr.innerHTML=`<td class="mono"><b>${esc(run.id.slice(0,9))}</b></td><td>${esc(run.scenario_id)}</td><td>${esc(run.policy)}</td><td>${run.shield?'ON':'OFF'}</td><td class="${cls}">${escapeHtmlStatus(status)}</td><td>${run.summary?.safety_violations??'—'}</td><td>${new Date(run.created_at*1000).toLocaleString()}</td>`;
    tr.addEventListener('click',()=>benchSelectRun(run.id,true));
    p.appendChild(tr);
  }
}
function escapeHtmlStatus(s){return esc(s)}
function benchAggregate(){
  const done=bench.runs.filter(r=>r.status==='completed'&&r.summary);
  const trials=done.length;
  const sum=key=>done.reduce((a,r)=>a+(Number(r.summary[key])||0),0);
  benchText('benchMetricRate',trials?(100*sum('verified')/trials).toFixed(1)+'%':'—');
  benchText('benchMetricRateNote',`${trials} trial${trials===1?'':'s'} evaluated by a verifier separate from the agent`);
  benchText('benchMetricViolations',trials?sum('safety_violations'):'—');
  benchText('benchMetricViolationsNote','Across '+trials+' completed experiments');
  benchText('benchMetricShields',trials?sum('interventions'):'—');
  benchText('benchMetricShieldsNote','Geometric motion gate actions');
  const count=bench.selectedRun?.events?.length;
  benchText('benchMetricEvents',count?count.toLocaleString():'—');
  benchText('benchMetricEventsNote','Selected run hash-chain entries');
  benchRenderResearch();
}
function benchRenderResearch(){
  const done=bench.runs.filter(r=>r.status==='completed'&&r.summary);
  const groups=[['greedy',false],['greedy',true],['route',false],['route',true]];
  const p=$('#benchComparisonBars');if(!p)return;
  p.replaceChildren();
  if(!done.length){const e=document.createElement('p');e.className='small-note';e.style.padding='0';e.textContent='No experiments yet. Run both policies against the same scenario and seed.';p.appendChild(e);return}
  for(const [policy,shield] of groups){
    const list=done.filter(r=>r.policy===policy&&r.shield===shield);
    if(!list.length)continue;
    const ratio=list.filter(r=>r.summary.verified).length/list.length;
    const row=document.createElement('div');row.className='bench-compare-row';
    row.innerHTML=`<span>${policy==='route'?'Route planning':'Greedy control'} / ${shield?'gate on':'gate off'} <small>(n=${list.length})</small></span><div class="bench-compare-track"><div class="bench-compare-fill"></div></div><b>${Math.round(ratio*100)}%</b>`;
    row.querySelector('.bench-compare-fill').style.width=`${Math.max(ratio*100,.3)}%`;
    p.appendChild(row);
  }
  const notice=document.createElement('p');notice.className='small-note';notice.style.padding='6px 0 0';
  notice.textContent='Descriptive local run history only; not a paired, controlled estimate of model performance.';
  p.appendChild(notice);
}
function benchGate(name,label,tone){const node=document.querySelector(`[data-bench-gate="${name}"] b`);if(node){node.textContent=label;node.className=tone||''}}
function benchSetRunInfo(run){
  const v=run?.summary;
  benchGate('chain',v?(v.trace_integrity?'PASS':'FAIL'):'—',v?(v.trace_integrity?'ok':'bad'):'');
  benchGate('postcondition',v?(v.task_completed?'PASS':'FAIL'):'—',v?(v.task_completed?'ok':'bad'):'');
  benchGate('safety',v?(v.safety_violations===0?'PASS':'FAIL'):'—',v?(v.safety_violations===0?'ok':'bad'):'');
  benchGate('attestation',v?(v.attestation_verified===true?'SIGNED':v.attestation_verified===false?'INVALID':'UNSIGNED'):'—',v?(v.attestation_verified===true?'ok':v.attestation_verified===false?'bad':''):'');
  benchText('benchVerifStatus',v?(v.verified?'VERIFIED':'NOT VERIFIED'):run?.status?.toUpperCase()||'AWAITING EVIDENCE');
  const vs=$('#benchVerifStatus');if(vs)vs.className='bench-verif-state '+(v?(v.verified?'passed':'failed'):'');
  const dl=$('#benchDownloadBtn'),ex=$('#benchLedgerExportBtn');
  if(dl)dl.disabled=!(run?.status==='completed');
  if(ex)ex.disabled=!(run?.status==='completed');
  benchText('benchRunProgress',v?Math.round(v.progress*100)+'%':'—');
  const bar=$('#benchRunProgressBar');if(bar)bar.style.width=v?Math.min(100,Math.max(0,v.progress*100))+'%':'0%';
  benchText('benchLastClearance',v&&v.min_clearance_m!==null?v.min_clearance_m.toFixed(2)+' m':'—');
  benchText('benchLastFaults',v?`${v.faults} / ${v.recovered_faults}`:'—');
  benchText('benchLastDuration',v?v.sim_time_seconds.toFixed(1)+' s':'—');
  benchText('benchLastEnergy',v?v.energy_proxy.toFixed(2)+' proxy':'—');
  benchText('benchAnalysisTag',run?run.id.slice(0,8).toUpperCase():'NO RUN');
}
function benchEventLabel(e){
  const p=e.payload||{};
  if(e.kind==='state')return `Position [${Number(p.x).toFixed(2)}, ${Number(p.y).toFixed(2)}] · stage ${p.stage}`;
  if(e.kind==='proposal')return `${p.decision||'motion'} · v=(${p.vx}, ${p.vy})`;
  if(e.kind==='intervention')return p.reason||'Safety gate intervened';
  if(e.kind==='milestone')return `Verified checkpoint: ${p.label||p.index}`;
  if(e.kind==='fault')return `${p.kind} · ${p.phase}`;
  if(e.kind==='terminal')return `Terminal claim: ${p.claimed}`;
  if(e.kind==='observation')return p.sensor_ok?'Sensor observation accepted':'Sensor observation unavailable';
  if(e.kind==='abstain')return p.reason||'Correct abstention';
  return JSON.stringify(p).slice(0,100);
}
function benchRenderEvents(events){
  const p=$('#benchEventsList');if(!p)return;
  p.replaceChildren();
  benchText('benchEventCount',`${events.length} EVENTS`);
  const noteworthy=events.filter(e=>['fault','intervention','milestone','abstain','terminal'].includes(e.kind));
  const recent=(noteworthy.length?noteworthy:events.filter(e=>e.kind==='proposal')).slice(-9).reverse();
  if(!recent.length){p.innerHTML='<div class="small-note">No events yet. The trace will appear after you start an experiment.</div>';return}
  for(const e of recent){
    const item=document.createElement('div');item.className='bench-event';
    item.innerHTML=`<span class="bench-event-tick">T+${String(e.tick).padStart(3,'0')}</span><span class="bench-event-tag ${esc(e.kind)}">${esc(e.kind.toUpperCase())}</span><span class="bench-event-content"></span>`;
    item.querySelector('.bench-event-content').textContent=benchEventLabel(e);
    item.title=benchEventLabel(e);
    p.appendChild(item);
  }
}
function benchRenderTrace(run){
  if(!run){benchText('benchTracePreview','Choose a completed run to inspect event provenance.');return}
  const events=run.events||[];
  const overview={id:run.id,scenario:run.scenario_id,policy:run.policy,seed:run.seed,shield:run.shield,status:run.status,verification:run.summary,manifest:run.manifest||null,tail_events:events.slice(-5)};
  benchText('benchTracePreview',JSON.stringify(overview,null,2));
}
async function benchRefresh(){
  if(bench.polling)return;
  bench.polling=true;
  try{
    bench.runs=await benchApi('/api/runs');
    benchRenderRuns();
    const selectedId=bench.selectedRun?.id;
    if(selectedId){
      const r=await benchApi('/api/runs/'+selectedId);
      const wasComplete=bench.selectedRun.status==='completed';
      const isDifferent=r.events?.length!==bench.selectedRun.events?.length||r.status!==bench.selectedRun.status;
      bench.selectedRun=r;
      if(isDifferent){
        if(benchScene){if(r.status==='completed'&&!wasComplete)benchScene.setEvents([]);benchScene.setEvents(r.events||[],r.status==='completed')}
        benchSetRunInfo(r);benchRenderEvents(r.events||[]);benchRenderTrace(r);
        benchText('benchSceneStatus',r.status==='completed'?(r.summary?.verified?'VERIFIED':'REVIEW REQUIRED'):'EXECUTING');
      }
    }else if(bench.runs.length){
      const first=bench.runs[0];
      if(first.status==='completed')await benchSelectRun(first.id,false);
    }
    benchAggregate();
  }catch(e){if(!String(e.message).includes('authentication'))console.warn(e)}finally{bench.polling=false}
}
async function benchSelectRun(id,navigate){
  try{
    const r=await benchApi('/api/runs/'+id);
    bench.selectedRun=r;
    if(bench.scenarios.find(s=>s.id===r.scenario_id))benchScenarioSelect(r.scenario_id);
    if(benchScene){benchScene.setEvents([]);benchScene.setEvents(r.events||[],r.status==='completed')}
    benchSetRunInfo(r);benchRenderEvents(r.events||[]);benchRenderTrace(r);benchAggregate();
    benchText('benchSceneStatus',r.status==='completed'?(r.summary?.verified?'VERIFIED':'REVIEW REQUIRED'):'EXECUTING');
    if(navigate)openPolicyTab('runner');
  }catch(e){toast(e.message,true)}
}
async function benchRun(policy=null){
  const s=benchCurrentScenario();if(!s)return toast('Scenario contracts not loaded',true);
  const seed=Number($('#benchSeedInput').value);
  if(!Number.isInteger(seed)||seed<0||seed>4294967295)return toast('Seed must be an integer between 0 and 2^32−1',true);
  try{
    const chosenPolicy=policy||$('#benchPolicySelect').value;
    const req={scenario_id:s.id,policy:chosenPolicy,seed,shield:$('#benchShieldToggle').checked};
    const accepted=await benchApi('/api/runs',{method:'POST',body:JSON.stringify(req)});
    bench.selectedRun=null;
    if(benchScene)benchScene.setEvents([]);
    benchSetRunInfo(null);
    benchText('benchSceneStatus','QUEUED');
    toast(`Trial ${accepted.run_id.slice(0,8)} queued · ${chosenPolicy}`);
    await benchSelectRun(accepted.run_id,false);
    openPolicyTab('runner');
  }catch(e){toast(e.message,true)}
}
async function benchCompare(){
  const s=benchCurrentScenario();if(!s)return toast('Scenario contracts not loaded',true);
  const seed=Number($('#benchSeedInput').value);
  if(!Number.isInteger(seed)||seed<0||seed>4294967295)return toast('Invalid seed',true);
  try{
    for(const p of ['greedy','route']){
      await benchApi('/api/runs',{method:'POST',body:JSON.stringify({scenario_id:s.id,policy:p,seed,shield:$('#benchShieldToggle').checked})});
    }
    toast('Paired baseline trials queued with identical seed and scenario');
    setTimeout(benchRefresh,600);
    openPolicyTab('research');
  }catch(e){toast(e.message,true)}
}
async function benchExportRun(){
  if(!bench.selectedRun||bench.selectedRun.status!=='completed')return;
  try{
    const blob=await benchApi(`/api/runs/${bench.selectedRun.id}/bundle`,{blob:true});
    const href=URL.createObjectURL(blob);
    const a=document.createElement('a');a.href=href;a.download=`veap-evidence-${bench.selectedRun.id.slice(0,8)}.json`;a.click();
    setTimeout(()=>URL.revokeObjectURL(href),1000);
    toast('Evidence JSON bundle exported');
  }catch(e){toast(e.message,true)}
}
class BenchWorldRenderer{
  constructor(canvas){
    this.canvas=canvas;this.ctx=canvas.getContext('2d');this.yaw=-.57;this.zoom=1;this.frame=0;this.frames=[];this.scenario=null;this.playing=false;this.last=0;this.drag=false;this.mouseX=0;
    this.resize();window.addEventListener('resize',()=>this.resize());new ResizeObserver(()=>this.resize()).observe(canvas);
    canvas.addEventListener('pointerdown',e=>{this.drag=true;this.mouseX=e.clientX;canvas.setPointerCapture(e.pointerId)});
    canvas.addEventListener('pointerup',()=>this.drag=false);canvas.addEventListener('pointercancel',()=>this.drag=false);
    canvas.addEventListener('pointermove',e=>{if(this.drag){this.yaw+=(e.clientX-this.mouseX)*.008;this.mouseX=e.clientX}});
    canvas.addEventListener('wheel',e=>{e.preventDefault();this.zoom=Math.max(.57,Math.min(1.8,this.zoom*(e.deltaY>0?.94:1.06)))},{passive:false});
    requestAnimationFrame(t=>this.loop(t));
  }
  resize(){
    const rect=this.canvas.getBoundingClientRect();if(!rect.width||!rect.height)return;
    this.w=rect.width;this.h=rect.height;const dpr=Math.min(2,window.devicePixelRatio||1);
    this.canvas.width=Math.round(this.w*dpr);this.canvas.height=Math.round(this.h*dpr);
    this.ctx.setTransform(dpr,0,0,dpr,0,0);
  }
  setScenario(s){this.scenario=s;this.frame=0;this.zoom=1;this.yaw=-.57;this.frames=[];this.playing=false;this.updateControls()}
  setEvents(events,autoplay=false){
    const prev=this.frames.length;
    this.frames=events.filter(e=>e.kind==='state').map(e=>({tick:e.tick,x:Number(e.payload.x),y:Number(e.payload.y),vx:Number(e.payload.vx),vy:Number(e.payload.vy),stage:Number(e.payload.stage)}));
    if(autoplay&&this.frames.length&&prev===0){this.frame=0;this.playing=true}
    else if(this.frame>=this.frames.length){this.frame=Math.max(0,this.frames.length-1)}
    this.updateControls();
  }
  updateControls(){
    const max=Math.max(0,this.frames.length-1);
    const sc=$('#benchScrubber');if(sc){sc.max=max;sc.value=Math.min(max,this.frame)}
    const dt=this.scenario?.dt||.2,tick=this.frames[this.frame]?.tick||0;
    benchText('benchPlaybackTime','T+ '+(tick*dt).toFixed(1)+'s');
    benchText('benchPlaybackTotal',max?(this.frames[max].tick*dt).toFixed(1)+'s':'—');
    benchText('benchPlayPause',this.playing?'Ⅱ':'▶');
  }
  loop(t){
    if(this.playing&&this.frames.length>1&&t-this.last>74){
      this.last=t;this.frame++;
      if(this.frame>=this.frames.length){this.frame=this.frames.length-1;this.playing=false}
      this.updateControls();
    }
    this.render(t);requestAnimationFrame(ts=>this.loop(ts));
  }
  point(x,y,h=0){
    const s=this.scenario;if(!s)return{x:0,y:0,d:0};
    const cx=s.width/2,cy=s.height/2,dx=x-cx,dy=y-cy,cs=Math.cos(this.yaw),ss=Math.sin(this.yaw);
    const u=dx*cs-dy*ss,v=dx*ss+dy*cs;
    const k=Math.min((this.w||700)/(s.width*1.57),(this.h||360)/(s.height*.97))*this.zoom;
    return{x:this.w/2+u*k,y:this.h*.52+v*k*.58-h*k*.83,d:v,k};
  }
  polygon(pts,fill,stroke=null,w=1){const c=this.ctx;c.beginPath();pts.forEach((p,i)=>i?c.lineTo(p.x,p.y):c.moveTo(p.x,p.y));c.closePath();if(fill){c.fillStyle=fill;c.fill()}if(stroke){c.strokeStyle=stroke;c.lineWidth=w;c.stroke()}}
  line(pts,col,w=1){if(pts.length<2)return;const c=this.ctx;c.beginPath();pts.forEach((p,i)=>i?c.lineTo(p.x,p.y):c.moveTo(p.x,p.y));c.strokeStyle=col;c.lineWidth=w;c.stroke()}
  rectZone(z){const p=(x,y,h)=>this.point(x,y,h);const q=[[z.x1,z.y1],[z.x2,z.y1],[z.x2,z.y2],[z.x1,z.y2]];this.polygon(q.map(a=>p(...a,0.01)),'#8b43386e','#c97c52',1);this.polygon(q.map(a=>p(...a,.1)),'#b362472a','#e6976080',1)}
  cylinder(x,y,r,h,main,top){
    const verts=[],cnt=20;for(let i=0;i<cnt;i++){const a=2*Math.PI*i/cnt;verts.push([x+r*Math.cos(a),y+r*Math.sin(a)])}
    const base=verts.map(q=>this.point(q[0],q[1],.01)),roof=verts.map(q=>this.point(q[0],q[1],h));
    for(let i=0;i<cnt;i++){const j=(i+1)%cnt;this.polygon([base[i],base[j],roof[j],roof[i]],i%3===0?main:main+'cc',null)}
    this.polygon(roof,top,'#7aa89e4d',1);
  }
  label(str,x,y,col='#b8d4cc'){const c=this.ctx;c.font='10px ui-sans-serif,system-ui';c.textAlign='center';c.fillStyle=col;c.fillText(str,x,y)}
  render(t){
    if(!this.ctx||!this.scenario||!this.w)return;
    const c=this.ctx,s=this.scenario;c.clearRect(0,0,this.w,this.h);
    const bg=c.createRadialGradient(this.w*.5,this.h*.45,25,this.w*.5,this.h*.48,this.w*.75);
    bg.addColorStop(0,'#1b3033');bg.addColorStop(1,'#091317');c.fillStyle=bg;c.fillRect(0,0,this.w,this.h);
    const p=(x,y,h=0)=>this.point(x,y,h);
    this.polygon([p(0,0),p(s.width,0),p(s.width,s.height),p(0,s.height)],'#14252a','#49676b',1.3);
    for(let x=0;x<=s.width+.01;x++)this.line([p(x,0),p(x,s.height)],'#6898941c',.8);
    for(let y=0;y<=s.height+.01;y++)this.line([p(0,y),p(s.width,y)],'#6898941c',.8);
    for(const z of s.forbidden_zones)this.rectZone(z);
    const entries=[];
    for(const o of s.obstacles)entries.push({depth:p(o.x,o.y).d,render:()=>{this.cylinder(o.x,o.y,o.radius,.71,'#29434d','#3f6470');const a=p(o.x,o.y,1.0);this.label(o.label,a.x,a.y,'#7ea3ad')}});
    for(let i=0;i<s.waypoints.length;i++){
      const wp=s.waypoints[i];
      entries.push({depth:p(wp.x,wp.y).d,render:()=>{
        const a=p(wp.x,wp.y,.08),top=p(wp.x,wp.y,.8);
        c.strokeStyle='#a69ff0ab';c.lineWidth=1.5;c.beginPath();c.moveTo(a.x,a.y);c.lineTo(top.x,top.y);c.stroke();
        const done=(this.frames[this.frame]?.stage||0)>i;
        c.beginPath();c.ellipse(top.x,top.y,7+Math.sin(t/450+i)*1.4,5,0,0,Math.PI*2);
        c.fillStyle=done?'#8fd31a':'#b7b1ff';c.fill();c.strokeStyle='#f0edff99';c.stroke();
        this.label(`${i+1}  ${wp.label}`,top.x,top.y-13,done?'#c5f76e':'#c6c3fd');
      }});
    }
    const trail=this.frames.slice(0,this.frame+1);
    if(trail.length>1){c.save();c.shadowColor='#55d7b9';c.shadowBlur=10;this.line(trail.map(q=>p(q.x,q.y,.07)),'#55d7b9cc',2.5);c.restore()}
    const cur=this.frames.length?this.frames[this.frame]:{x:s.start.x,y:s.start.y,vx:0,vy:0};
    entries.push({depth:p(cur.x,cur.y).d,render:()=>{
      const a=p(cur.x,cur.y,.08);c.save();c.shadowColor='#8fd31a';c.shadowBlur=22;c.beginPath();c.ellipse(a.x,a.y,13,6,0,0,2*Math.PI);c.fillStyle='#8fd31a66';c.fill();c.restore();
      this.cylinder(cur.x,cur.y,.22,.38,'#2f8c5a','#b9f378');
      const top=p(cur.x,cur.y,.44);c.beginPath();c.arc(top.x,top.y,3,0,2*Math.PI);c.fillStyle='#081e0c';c.fill();
      if(Math.hypot(cur.vx,cur.vy)>.02){const dir=p(cur.x+.55*cur.vx,cur.y+.55*cur.vy,.43);this.line([top,dir],'#e6fff0',2)}
      this.label('AGENT',top.x,top.y-19,'#c8f782');
    }});
    entries.sort((a,b)=>a.depth-b.depth);for(const e of entries)e.render();
    c.fillStyle='#83a0a8';c.font='10px ui-monospace,monospace';c.textAlign='left';c.fillText(`X ${cur.x.toFixed(2)}  Y ${cur.y.toFixed(2)}   /  ${s.width}×${s.height} m`,14,this.h-44);
  }
}
function bindBench(){
  const cv=$('#benchWorldCanvas');if(cv&&!benchScene)benchScene=new BenchWorldRenderer(cv);
  $$('.policy-tab').forEach(b=>b.addEventListener('click',()=>openPolicyTab(b.dataset.policyTab)));
  $('#benchRunTop')?.addEventListener('click',()=>benchRun());
  $('#benchRunBtn')?.addEventListener('click',()=>benchRun());
  $('#benchCompareTop')?.addEventListener('click',benchCompare);
  $('#benchResearchCompareBtn')?.addEventListener('click',benchCompare);
  $('#benchScenarioSelect')?.addEventListener('change',e=>benchScenarioSelect(e.target.value));
  $('#benchDownloadBtn')?.addEventListener('click',benchExportRun);
  $('#benchLedgerExportBtn')?.addEventListener('click',benchExportRun);
  $('#benchPlayPause')?.addEventListener('click',()=>{
    if(!benchScene||!benchScene.frames.length){toast('No trajectory to replay yet');return}
    if(benchScene.frame===benchScene.frames.length-1)benchScene.frame=0;
    benchScene.playing=!benchScene.playing;benchScene.updateControls();
  });
  $('#benchScrubber')?.addEventListener('input',e=>{if(!benchScene)return;benchScene.frame=Number(e.target.value);benchScene.playing=false;benchScene.updateControls()});
  $('#benchResetCamera')?.addEventListener('click',()=>{if(!benchScene)return;benchScene.yaw=-.57;benchScene.zoom=1});
  $('#benchAuthBtn')?.addEventListener('click',()=>benchAuthModal(true));
  $('#benchAuthClose')?.addEventListener('click',()=>benchAuthModal(false));
  $('#benchAuthCancel')?.addEventListener('click',()=>benchAuthModal(false));
  $('#benchAuthSave')?.addEventListener('click',async()=>{bench.auth=$('#benchAuthInput').value.trim();$('#benchAuthInput').value='';benchAuthModal(false);await ensureBenchInit(true)});
}
async function ensureBenchInit(force=false){
  if(bench.initialized&&!force)return;
  bench.initialized=true;
  try{
    bench.scenarios=await benchApi('/api/scenarios');
    const sel=$('#benchScenarioSelect');
    if(sel){
      sel.replaceChildren();
      for(const s of bench.scenarios){const o=document.createElement('option');o.value=s.id;o.textContent=`${s.title}  [${s.split}]`;sel.appendChild(o)}
    }
    benchRenderScenarios();
    benchScenarioSelect(bench.selectedScenario||'warehouse-transfer');
    await benchRefresh();
  }catch(e){bench.initialized=false;if(!String(e.message).includes('authentication'))toast(e.message,true)}
}

async function init(){bind();bindBench();try{await refreshAssets();renderConnectors();renderWorld();requestAnimationFrame(anim);setInterval(()=>{if(st.view==='connectors')api('/api/jobs').then(j=>renderNativeJobs(j.jobs)).catch(()=>{});if(st.view==='policy')benchRefresh()},1500)}catch(e){toast(e.message,true);$('#eventList').innerHTML=`<p class="small-note">Unable to load server: ${esc(e.message)}. Start the local API using uvicorn.</p>`}}
window.addEventListener('DOMContentLoaded',init);
})();
