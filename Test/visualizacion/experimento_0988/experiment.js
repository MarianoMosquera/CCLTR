(() => {
'use strict';
const $=id=>document.getElementById(id);
const escapeHTML=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const IDS={
 'a1b0de03-9f46-4af5-b85b-78c819417e06':0,
 '00f57384-fa62-4210-9cd2-2c4493679253':1,
 'b297d3d6-c894-4bcf-9ea3-6f6823ab50d2':2
};
// English editorial translations of the three new/reformulated claims.
// Source text and IDs are retained in the JSON audit trail.
const englishClaims=[
 'AI analytics can improve policy by converting time spent processing data into institutional capacity to act and review decisions. However, producing analyses, implementing them, and enabling affected people to challenge priorities compete for time, staff, and resources. Greater predictive capacity can coexist with reduced capacity to correct decisions. Available information, effective action, and opportunities to contest decisions must be distinguished; none guarantees the others.',
 'Backup systems can prevent AI failures from becoming catastrophes when they provide an effective capacity to maintain services and interrupt automation. This requires alternatives without shared failure modes, personnel able to operate them, and authorized activation procedures. Maintaining reserves may conflict with cost savings and intensive resource use; duplicating systems alone does not demonstrate that digital dependence is controlled.',
 'AI contributions to global well-being should face dual contestability: affected communities must be able to challenge external definitions of well-being, while individuals must be able to challenge decisions by their own communities that violate universal rights. These demands can require incompatible decisions about the same deployment. Neither aggregate benefits nor community acceptance automatically overrides the other; sectoral improvements alone cannot establish that AI will ultimately improve global well-being.'
];
const labels=['Reformulation 1 · Institutional capacity','Reformulation 2 · Operational redundancy','New node · Dual contestability','New PRO relation · Humanitarian imperative','New PRO relation · Cultural variance','New CON relation · Global well-being claim','New CON relation · AI bias and healthcare inequality','New CON relation · Insight–action gap and redundancy'];
const edges=[
 ['2c255901-73a6-4ce1-8261-87e952ac3bce','b297d3d6-c894-4bcf-9ea3-6f6823ab50d2','PRO'],
 ['05b7be24-2d22-4dff-9b5c-96aa5593f9d0','b297d3d6-c894-4bcf-9ea3-6f6823ab50d2','PRO'],
 ['b297d3d6-c894-4bcf-9ea3-6f6823ab50d2','4337ee26-e1db-499e-9340-97bce6e0276d','CON'],
 ['4d0b50b8-d93e-49bc-98d3-2019caa8fbbf','25f7d32e-8a43-41c9-bdfc-1c8aec6ffe95','CON'],
 ['18392527-0b3d-4fd4-8d43-74fe66e3a146','00f57384-fa62-4210-9cd2-2c4493679253','CON']
];
let cy, graph, step=0, timer=null;
function originalElements(g){
 return [
 ...g.nodes.map((n,i)=>({data:{id:String(n.id),label:String(i+1),claim:n.claim||'',title:n.label||'Original argument',kind:'original'}})),
 ...g.edges.map((e,i)=>({data:{id:'a-edge-'+i,source:String(e.source),target:String(e.target),valence:String(e.valence||'').toUpperCase(),kind:'original-edge'}}))
 ];
}
function setArgument(d){
 const claim=d.claim||'';
 $('exp-argument').innerHTML=`<strong>${escapeHTML(d.title||'Argument')}</strong><p class="exp-claim">${escapeHTML(claim)}</p><p class="exp-id">${escapeHTML(d.id)}</p><p class="exp-note">${escapeHTML(d.kind||'')}</p>`;
}
function render(stepValue){
 step=Math.max(0,Math.min(8,Number(stepValue)||0));$('exp-step').value=String(step);
 $('exp-counter').textContent=step?`Operation ${step} / 8`:'Original graph';
 $('exp-operation').textContent=step?labels[step-1]:'Original debate — all 20 source nodes remain visible.';
 if(!cy)return;
 cy.batch(()=>{
  cy.elements('[kind="version"], [kind="new-node"], [kind="new-edge"], [kind="version-link"]').remove();
  for(let i=0;i<Math.min(step,2);i++){
   const id=Object.keys(IDS).find(k=>IDS[k]===i),base=cy.getElementById(id);
   if(!base.length)continue;
   const p=base.position(),vid='version-'+id;
   cy.add({group:'nodes',data:{id:vid,label:(i+1)+'B',title:labels[i],claim:englishClaims[i],kind:'version'},position:{x:p.x+65,y:p.y-50}});
   cy.add({group:'edges',data:{id:'version-link-'+i,source:id,target:vid,kind:'version-link'}});
  }
  if(step>=3){
   const source=cy.getElementById('2c255901-73a6-4ce1-8261-87e952ac3bce');
   const p=source.length?source.position():{x:0,y:0};
   cy.add({group:'nodes',data:{id:'b297d3d6-c894-4bcf-9ea3-6f6823ab50d2',label:'B+',title:'Dual contestability',claim:englishClaims[2],kind:'new-node'},position:{x:p.x+115,y:p.y+85}});
  }
  for(let i=0;i<Math.max(0,step-3);i++){
   const [source,target,valence]=edges[i];
   if(cy.getElementById(source).length&&cy.getElementById(target).length)
    cy.add({group:'edges',data:{id:'new-edge-'+i,source,target,valence,kind:'new-edge'}});
  }
 });
 cy.elements('[kind="version"], [kind="new-node"]').lock();
}
function metricRow(name,a,b,suffix=''){
 const fmt=v=>typeof v==='number'?v.toFixed(4)+suffix:'—';
 return `<tr><td>${escapeHTML(name)}</td><td>${fmt(a)}</td><td>${fmt(b)}</td></tr>`;
}
function statistics(){
  const cmp=graph.comparison?.comparacion||{};
  const adjusted=graph.comparison?.comparacion_ajustada?.comparacion||{};
  const A=graph.measurements.a, B=graph.measurements.b;
  const fmt=x=>Number.isFinite(x)?x.toFixed(3):'—';
  const pct=x=>Number.isFinite(x)?x.toFixed(1)+'%':'—';
  const bar=(label,a,b,max=1,percent=true)=>{
    const width=x=>Math.max(0,Math.min(100,100*(Number.isFinite(x)?x:0)/max));
    const val=x=>percent?pct(x*100):fmt(x);
    return '<div class="exp-bar-group"><div class="exp-bar-name">'+escapeHTML(label)+'</div>'+
      '<div class="exp-bar-line"><span>A</span><div class="exp-track"><i class="exp-bar-a" style="width:'+width(a)+'%"></i></div><b>'+val(a)+'</b></div>'+
      '<div class="exp-bar-line"><span>B</span><div class="exp-track"><i class="exp-bar-b" style="width:'+width(b)+'%"></i></div><b>'+val(b)+'</b></div></div>';
  };
  const dimensions=[['Values','Valores'],['Agenda','Agenda'],['Rationality','Racionalidad'],['Governance','Gobernanza']];
  const da=A.mediciones.dimensional.conteos,db=B.mediciones.dimensional.conteos;
  const sum=obj=>Object.values(obj).reduce((t,n)=>t+(Number(n)||0),0);
  const ta=sum(da),tb=sum(db);
  const fa=A.mediciones.funcional.conteos,fb=B.mediciones.funcional.conteos;
  const funcs=[['Pragmatic','pragmatica'],['Conditional','condicional'],['Prospective','prospectiva']];
  const faTotal=sum(fa),fbTotal=sum(fb);
  const anchors=graph.operations.flatMap(op=>op.propuesta?.anclajes_skos||[]);
  const unique=new Set(anchors);
  const perNodeA=A.mediciones.riqueza_skos.riqueza_media;
  const perNodeB=B.mediciones.riqueza_skos.riqueza_media;
  const cmpRow=(name,o)=>'<tr><td>'+escapeHTML(name)+'</td><td>'+fmt(o?.rama_a)+'</td><td>'+fmt(o?.rama_b)+'</td><td>'+pct(o?.variacion_porcentual)+'</td></tr>';
  const rows=[['Global diversity',cmp.indice_global],['Dimensional',cmp.dimensional],['SKOS richness',cmp.riqueza_skos],['Functional',cmp.funcional],['Semantic',cmp.semantica]];
  const adjRows=[['Size-adjusted global',adjusted.indice_ajustado],['Size-adjusted dimensional',adjusted.dimensional],['Size-adjusted richness',adjusted.riqueza_skos],['Size-adjusted functional',adjusted.funcional],['Size-adjusted semantic',adjusted.semantica]];
  const table=rows=>'<table class="exp-metrics"><thead><tr><th>Metric</th><th>A</th><th>B</th><th>Δ%</th></tr></thead><tbody>'+rows.map(x=>cmpRow(...x)).join('')+'</tbody></table>';
  $('exp-stats').innerHTML='<p class="exp-note">A: '+graph.original.nodes.length+' nodes / '+graph.original.edges.length+' relations · B: '+graph.transformed.nodes.length+' nodes / '+graph.transformed.edges.length+' relations</p>'+
    '<h4>Dimensional distribution</h4><p class="exp-note">Share of dimension assignments</p>'+
    dimensions.map(([label,key])=>bar(label,da[key]/ta,db[key]/tb)).join('')+
    '<h4>Functional diversity</h4><p class="exp-note">Share of functional assignments</p>'+
    funcs.map(([label,k])=>bar(label,fa[k]/faTotal,fb[k]/fbTotal)).join('')+
    '<h4>SKOS Richness</h4>'+
    '<p class="exp-note">Comparison of SKOS concept coverage and richness across A and B.</p>'+
    
    bar('Rarefied SKOS Richness',perNodeA,perNodeB,Math.max(perNodeA,perNodeB)*1.08,false)+
    
    '<h4>Observed diversity indices</h4>'+table(rows)+'<h4>Size-adjusted indices</h4>'+table(adjRows)+
    '<p class="exp-note">Adjusted comparison: 10-node samples, 1,000 repetitions without replacement. </p>';
}

function play(){
 if(timer){clearInterval(timer);timer=null;$('exp-play').textContent='Play';return;}
 if(step===8)render(0);
 $('exp-play').textContent='Pause';timer=setInterval(()=>{if(step>=8){clearInterval(timer);timer=null;$('exp-play').textContent='Play';return;}render(step+1)},1600);
}
async function init(){
 if(!$('ccltr-experiment'))return;
 if(typeof cytoscape!=='function'){$('exp-operation').textContent='Cytoscape library unavailable.';return;}
 try{
  const response=await fetch('experiment/0988.json');if(!response.ok)throw Error('HTTP '+response.status);
  graph=await response.json();
  if(graph.original.nodes.length!==20||graph.transformed.nodes.length!==21)throw Error('Unexpected graph size');
  cy=cytoscape({container:$('exp-cy'),elements:originalElements(graph.original),
   style:[
    {selector:'node',style:{'background-color':'#2c8cdd','label':'data(label)','color':'#fff','font-size':10,'text-valign':'center','text-halign':'center','width':34,'height':34,'border-width':2,'border-color':'#9ed2ff'}},
    {selector:'node[kind="version"]',style:{'background-color':'#f07832','border-color':'#ffd7ae','width':35,'height':35}},
    {selector:'node[kind="new-node"]',style:{'background-color':'#29b76b','border-color':'#b4ffcf','width':40,'height':40}},
    {selector:'edge',style:{'width':1.6,'line-color':'#6588b1','target-arrow-color':'#6588b1','target-arrow-shape':'triangle','curve-style':'bezier','arrow-scale':.7}},
    {selector:'edge[valence="CON"]',style:{'line-style':'dashed'}},
    {selector:'edge[kind="new-edge"][valence="CON"]',style:{'line-style':'dashed'}},
    {selector:'edge[kind="version-link"]',style:{'line-color':'#ff9d45','target-arrow-color':'#ff9d45','width':3,'line-style':'dotted'}},
    {selector:'edge[kind="new-edge"]',style:{'line-color':'#ffe15c','target-arrow-color':'#ffe15c','width':5}},
    {selector:':selected',style:{'border-width':5,'border-color':'#fff'}}
   ],layout:{name:'cose',animate:false,randomize:false,nodeRepulsion:8500,idealEdgeLength:100,padding:45}});
  cy.on('tap','node',e=>setArgument(e.target.data()));
  cy.once('layoutstop',()=>{cy.nodes().lock();render(0)});
  render(0);statistics();
 }catch(err){$('exp-operation').textContent='Experiment data unavailable: '+err.message;}
 $('exp-prev').onclick=()=>render(step-1);$('exp-next').onclick=()=>render(step+1);
 $('exp-reset').onclick=()=>{if(timer)play();render(0)};
 $('exp-play').onclick=play;$('exp-step').oninput=e=>render(e.target.value);
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();
