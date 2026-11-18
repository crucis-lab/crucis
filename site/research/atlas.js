"use strict";
(()=>{
 const doc=document,scenes=[...doc.querySelectorAll('[data-step]')],jumps=[...doc.querySelectorAll('[data-step-jump]')];
 const back=doc.getElementById('back'),next=doc.getElementById('next'),count=doc.getElementById('step-count'),handoff=doc.getElementById('page-handoff');let current=0,all=false;
 function fromHash(){let id;try{id=decodeURIComponent(location.hash.slice(1));}catch{return 0;}const idx=scenes.findIndex(s=>s.id===id);return idx<0?0:idx;}
 function render(index,focus=false){if(!scenes.length)return;current=Math.max(0,Math.min(scenes.length-1,index));scenes.forEach((s,i)=>s.hidden=!all&&i!==current);jumps.forEach((b,i)=>{if(i===current)b.setAttribute('aria-current','step');else b.removeAttribute('aria-current');});
  const select=doc.getElementById('step-select');if(select)select.value=String(current);
  if(back)back.disabled=current===0;if(next){next.hidden=current===scenes.length-1;next.textContent=scenes[current].dataset.nextLabel||'Continue →';}if(count)count.textContent=`${current+1} / ${scenes.length}`;if(handoff)handoff.hidden=!all&&current!==scenes.length-1;
  if(focus){const h=scenes[current].querySelector('h2');h?.focus({preventScroll:true});}
 }
 function move(index){if(index<0||index>=scenes.length)return;history.pushState(null,'','#'+scenes[index].id);render(index,true);}
 jumps.forEach((b,i)=>b.addEventListener('click',()=>move(i)));back?.addEventListener('click',()=>move(current-1));next?.addEventListener('click',()=>move(current+1));window.addEventListener('hashchange',()=>render(fromHash()));window.addEventListener('popstate',()=>render(fromHash()));
 doc.getElementById('step-select')?.addEventListener('change',e=>move(Number(e.target.value)));
 function reveal(group){const step=group.closest('[data-step]');step?.querySelectorAll('[data-after-attempt]').forEach(el=>el.hidden=false);step?.querySelectorAll('[data-before-attempt]').forEach(el=>el.hidden=true);}
 const viewAll=doc.getElementById('view-all');viewAll?.addEventListener('click',()=>{all=!all;doc.body.classList.toggle('all-steps',all);viewAll.textContent=all?'Return to one step at a time':'Read every step together';viewAll.setAttribute('aria-pressed',String(all));if(all)doc.querySelectorAll('[data-exercise]').forEach(reveal);render(current);});render(fromHash());
 for(const group of doc.querySelectorAll('[data-exercise]')){const result=group.querySelector('[data-exercise-result]');group.querySelectorAll('button[data-result]').forEach(b=>b.addEventListener('click',()=>{group.querySelectorAll('button[data-result]').forEach(x=>x.setAttribute('aria-pressed',String(x===b)));if(result)result.textContent=b.dataset.result;reveal(group);}));group.querySelector('[data-reveal]')?.addEventListener('click',()=>{reveal(group);if(result)result.textContent='The explanation is now shown alongside the rules.';});}
 const territories=[...doc.querySelectorAll('[data-territory]')],panels=[...doc.querySelectorAll('[data-territory-panel]')];
 const regionNames=['reference','answers','comparison','reconstruction','validation'];
 function selectTerritory(name){if(!regionNames.includes(name))return;territories.forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.territory===name)));panels.forEach(p=>p.hidden=p.dataset.territoryPanel!==name);doc.querySelectorAll('[data-land]').forEach(g=>{g.setAttribute('data-selected',String(g.dataset.land===name));g.querySelector('path')?.setAttribute('fill',g.dataset.land===name?'var(--known)':'var(--land)');});}
 territories.forEach(b=>b.addEventListener('click',()=>{selectTerritory(b.dataset.territory);history.replaceState(null,'','#'+b.dataset.territory);}));
 function territoryFromHash(){const name=location.hash.slice(1);selectTerritory(regionNames.includes(name)?name:'answers');}
 if(territories.length){territoryFromHash();window.addEventListener('hashchange',territoryFromHash);}
})();

/* The homepage uses ordinary fragment links so every branch remains linkable. */
(()=>{
 const panels=[...document.querySelectorAll('[data-home-region]')];
 if(!panels.length)return;
 const ids=panels.map(p=>p.id),links=[...document.querySelectorAll('[data-home-select]')];
 function select(name,focus=false){
  if(!ids.includes(name))return;
  panels.forEach(p=>p.hidden=p.id!==name);
  links.forEach(a=>{if(a.dataset.homeSelect===name)a.setAttribute('aria-current','true');else a.removeAttribute('aria-current');});
  document.querySelectorAll('[data-home-land]').forEach(g=>g.dataset.selected=String(g.dataset.homeLand===name));
  if(focus)document.getElementById(name)?.focus({preventScroll:true});
 }
 function fromHash(){let name;try{name=decodeURIComponent(location.hash.slice(1));}catch{return;}const target=document.getElementById(name);const region=target?.closest('[data-home-region]');if(region)select(region.id);const scene=target?.closest('[data-case-panel]');if(scene)caseSelect(scene.dataset.casePanel);let details=target?.closest('details');while(details){details.open=true;details=details.parentElement?.closest('details');}}
 links.forEach(a=>a.addEventListener('click',e=>{e.preventDefault();const name=a.dataset.homeSelect;select(name,true);history.pushState(null,'','#'+name);document.getElementById(name).scrollIntoView({block:'start'});}));
 select(ids.includes(location.hash.slice(1))?location.hash.slice(1):'answers');
 window.addEventListener('hashchange',fromHash);window.addEventListener('popstate',fromHash);
 const choices=[...document.querySelectorAll('[data-case-select]')],cases=[...document.querySelectorAll('[data-case-panel]')];
 function caseSelect(name){cases.forEach(p=>p.hidden=p.dataset.casePanel!==name);choices.forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.caseSelect===name)));}
 choices.forEach(b=>b.addEventListener('click',()=>caseSelect(b.dataset.caseSelect)));
 document.querySelectorAll('a[href="#apartment-task"]').forEach(a=>a.addEventListener('click',event=>{event.preventDefault();const task=document.getElementById('apartment-task');task.open=true;if(location.hash!=='#apartment-task')history.pushState(null,'','#apartment-task');task.querySelector('summary').focus({preventScroll:true});task.scrollIntoView({block:'start'});}));
 caseSelect('decision');
 fromHash();
})();
