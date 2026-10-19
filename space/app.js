'use strict';
// Local testing: serve from the project root.
// For Hugging Face Static Space, use the published GitHub raw data URL.
const RAW_BASE = 'https://raw.githubusercontent.com/marianomosquera/CCLTR/main/datos';
const $ = id => document.getElementById(id);
const FAMILY_LABELS = {'Reconocimiento facial, privacidad y seguridad':'Facial recognition, privacy & security','Educación y producción cultural':'Education & cultural production','Democracia y gobernanza algorítmica':'Democracy & algorithmic governance','Derechos y condición moral de la IA':'AI rights & moral status','Desarrollo de la IA e impactos sociales':'AI development & social impacts'};
const familyLabel = name => FAMILY_LABELS[name] || name;
let records = [], families = [], selectedFamily = null, selectedRecord = null, cy = null, filter = 'ALL';
const safe = value => String(value ?? '');
const fetchJSON = async path => {const r = await fetch(`${RAW_BASE}/${path}`); if (!r.ok) throw new Error(`${r.status} al cargar ${path}`); return r.json();};
const setStatus = message => $('status').textContent = message;

async function init(){
  try {
    if(typeof cytoscape !== 'function') throw new Error('Cytoscape.js could not load. Check your internet connection.');
    [records, families] = await Promise.all([fetchJSON('mapas_ia.json'),fetchJSON('familias.json')]);
    $('totalMaps').textContent = records.length;
    selectedFamily = families[0]?.familia || null;
    renderFamilies();renderResults();setStatus(`${records.length} debates available`);
    const first = records.find(r=>r.id==='debate-train-0096' && families.find(f=>f.familia===selectedFamily)?.mapas.includes(r.id)) || records.find(r=>families.find(f=>f.familia===selectedFamily)?.mapas.includes(r.id));
    if(first) await show(first);
  } catch(err){setStatus(`Error: ${err.message}`);$('graphPlaceholder').textContent = `Could not load the data. ${err.message}`;}
}
function renderFamilies(){
  const container=$('families');container.replaceChildren();
  const options=families.map(f=>({...f,key:f.familia}));
  for(const f of options){
    const b=document.createElement('button');b.type='button';b.className=`family${selectedFamily===f.key?' active':''}`;
    const name=document.createElement('span');name.textContent=familyLabel(f.familia);
    const count=document.createElement('span');count.className='count';count.textContent=String(f.cantidad);
    b.append(name,count);b.addEventListener('click',()=>{selectedFamily=f.key;renderFamilies();renderResults();const first=records.find(r=>f.mapas.includes(r.id));if(first)show(first);});container.append(b);
  }
}
function renderResults(){
  const ids=new Set((families.find(f=>f.familia===selectedFamily)?.mapas)||[]);
  const matching=records.filter(r=>ids.has(r.id));
  $('count').textContent=String(matching.length);$('results').replaceChildren();
  for(const r of matching){
    const b=document.createElement('button');b.type='button';b.className=`result${selectedRecord?.id===r.id?' active':''}`;
    const title=document.createElement('span');title.textContent=r.tesis;
    const small=document.createElement('small');small.textContent=`${r.id} · ${r.nodos} nodes`;
    b.append(title,small);b.addEventListener('click',()=>show(r));$('results').append(b);
  }
}
function familyOf(id){return families.find(f=>f.mapas.includes(id))?.familia || 'Unclassified';}
function textOf(n){return safe(n.claim||n.label||n.text||n.id);}
function resetDetail(){const d=$('detail');d.replaceChildren();const p=document.createElement('p');p.className='muted';p.textContent='Select a node to read its full claim and relationships.';d.append(p);}
function showDetail(node){
  const data=node.data(),d=$('detail');d.replaceChildren();
  const tag=document.createElement('div');tag.className='detail-tag';tag.textContent=node.data('isRoot')?'CENTRAL THESIS':'ARGUMENT NODE';
  const p=document.createElement('p');p.className='claim';p.textContent=textOf(data);
  const id=document.createElement('p');id.className='detail-id';id.textContent=`ID: ${data.id}`;
  const incoming=node.incomers('edge');const outgoing=node.outgoers('edge');
  const meta=document.createElement('div');meta.className='detail-meta';meta.textContent=`Incoming relations: ${incoming.length} · outgoing: ${outgoing.length}`;
  d.append(tag,p,id,meta);
}
function applyFilter(){
  if(!cy)return;
  cy.batch(()=>{
    cy.elements().style('display','element');
    if(filter!=='ALL'){
      cy.edges().forEach(e=>{if(e.data('valence')!==filter)e.style('display','none');});
      cy.nodes().forEach(n=>{if(!n.data('isRoot')&&n.connectedEdges(':visible').length===0)n.style('display','none');});
    }
  });
  ['All','Pro','Con'].forEach(x=> $(`filter${x}`).classList.toggle('active',x.toUpperCase()===filter));
}
function layout(){
  if(!cy)return;
  // Force-directed CoSE: organic constellation-like clusters, not hierarchical rows.
  cy.layout({name:'cose',randomize:true,animate:'end',animationDuration:850,
    fit:true,padding:55,nodeRepulsion:node=>110000,idealEdgeLength:edge=>85,
    edgeElasticity:edge=>95,gravity:0.3,numIter:1300,initialTemp:200,
    coolingFactor:0.95,minTemp:1.0}).run();
}
async function show(r){
  selectedRecord=r;renderResults();$('title').textContent=r.tesis;$('mapId').textContent=r.id;
  $('familyName').textContent=familyLabel(familyOf(r.id)).toUpperCase();
  const link=$('source');if(/^https:\/\//.test(safe(r.fuente))){link.href=r.fuente;link.hidden=false;}else{link.hidden=true;}
  $('graphPlaceholder').textContent='Loading argument constellation…';$('graphPlaceholder').style.display='grid';resetDetail();
  try{
    const g=await fetchJSON(`grafos/${encodeURIComponent(r.id)}.json`);
    if(selectedRecord?.id!==r.id)return;
    const edgesRaw=g.edges||g.links||[];
    const outgoing=new Set(edgesRaw.map(e=>safe(e.source)));
    const roots=(g.nodes||[]).filter(n=>!outgoing.has(safe(n.id)));
    const rootId=roots.length===1?safe(roots[0].id):safe(r.root_id);
    const nodes=(g.nodes||[]).map(n=>({data:{...n,id:safe(n.id),label:textOf(n).slice(0,48),isRoot:safe(n.id)===rootId}}));
    const edges=edgesRaw.map((e,i)=>({data:{...e,id:`edge-${i}`,source:safe(e.source),target:safe(e.target),valence:safe(e.valence).toUpperCase()}}));
    if(cy)cy.destroy();
    cy=cytoscape({container:$('cy'),elements:[...nodes,...edges],minZoom:.08,maxZoom:3,wheelSensitivity:.16,style:[
      {selector:'node',style:{'background-color':'#7898bd','width':9,'height':9,'border-width':1,'border-color':'#a2b5d0','label':'','transition-property':'background-color,width,height','transition-duration':'150ms'}},
      {selector:'node[?isRoot]',style:{'background-color':'#f1bd68','width':30,'height':30,'border-width':3,'border-color':'#fff0c6','label':'THESIS','font-size':11,'font-weight':700,'color':'#f8e7c5','text-valign':'top','text-margin-y':-11}},
      {selector:'node:selected',style:{'background-color':'#ffffff','border-color':'#5baeff','border-width':4,'width':20,'height':20,'label':'data(label)','color':'#fff','font-size':11,'text-wrap':'wrap','text-max-width':180,'text-background-color':'#142b49','text-background-opacity':.9,'text-background-padding':'6px'}},
      {selector:'edge',style:{'width':1.25,'line-color':'#5a7194','target-arrow-color':'#5a7194','target-arrow-shape':'triangle','arrow-scale':.6,'curve-style':'unbundled-bezier','control-point-distances':30,'control-point-weights':0.5,'opacity':.52}},
      {selector:'edge[valence = "PRO"]',style:{'line-color':'#3bceab','target-arrow-color':'#3bceab','opacity':.75}},
      {selector:'edge[valence = "CON"]',style:{'line-color':'#ff718a','target-arrow-color':'#ff718a','opacity':.75}}
    ],layout:{name:'preset'}});
    cy.on('tap','node',e=>showDetail(e.target));
    $('nodeCount').textContent=nodes.length.toLocaleString('en-US');$('edgeCount').textContent=edges.length.toLocaleString('en-US');
    $('proCount').textContent=edges.filter(e=>e.data.valence==='PRO').length.toLocaleString('en-US');
    $('conCount').textContent=edges.filter(e=>e.data.valence==='CON').length.toLocaleString('en-US');
    $('graphPlaceholder').style.display='none';filter='ALL';applyFilter();layout();
  }catch(err){$('graphPlaceholder').textContent=`Could not load the map: ${err.message}`;setStatus('Error loading graph');}
}
$('filterAll').addEventListener('click',()=>{filter='ALL';applyFilter();});
$('filterPro').addEventListener('click',()=>{filter='PRO';applyFilter();});
$('filterCon').addEventListener('click',()=>{filter='CON';applyFilter();});
$('fit').addEventListener('click',()=>cy?.fit(cy.elements(':visible'),40));
$('reset').addEventListener('click',layout);
init();
