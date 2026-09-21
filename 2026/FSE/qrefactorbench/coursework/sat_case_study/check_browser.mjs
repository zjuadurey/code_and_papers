// Node 22 + a locally launched Chromium with --remote-debugging-port=9228.
import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const base='coursework/sat_case_study';
const targets=await(await fetch('http://127.0.0.1:9228/json')).json();
const ws=new WebSocket(targets.find(t=>t.type==='page').webSocketDebuggerUrl);
await new Promise(resolve=>ws.addEventListener('open',resolve,{once:true}));
let id=0;const waiting=new Map();
ws.addEventListener('message',e=>{let m=JSON.parse(e.data);if(waiting.has(m.id)){let p=waiting.get(m.id);waiting.delete(m.id);m.error?p.reject(Error(JSON.stringify(m.error))):p.resolve(m.result)}});
function call(method,params={}){return new Promise((resolve,reject)=>{let n=++id;waiting.set(n,{resolve,reject});ws.send(JSON.stringify({id:n,method,params}))})}
async function js(expression){let r=await call('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value}
async function until(expression){let end=Date.now()+25000;while(Date.now()<end){if(await js(expression))return;await new Promise(r=>setTimeout(r,100))}throw Error('Timeout: '+expression)}
try{
  await call('Emulation.setDeviceMetricsOverride',{width:1440,height:1150,deviceScaleFactor:1,mobile:false});
  await call('Page.navigate',{url:'http://127.0.0.1:8766/'});
  await until("document.body.dataset.ready==='true'");
  let records=[];
  for(const index of [0,1,2]){
    await js(`document.body.dataset.result='';document.getElementById('example').value='${index}';document.getElementById('example').dispatchEvent(new Event('change'));document.getElementById('run').click()`);
    await until("document.body.dataset.result.length>0");
    records.push(await js("({prediction:document.getElementById('prediction').textContent,verification:document.getElementById('verification').textContent})"));
    if(index===2){if(!records[2].verification.startsWith('MISMATCH'))throw Error('Expected known-error demonstration');await fs.writeFile(base+'/results/demo_error.png',Buffer.from((await call('Page.captureScreenshot',{format:'png'})).data,'base64'))}
  }
  await js("document.getElementById('clauses').value='[[999,1]]';document.getElementById('run').click()");
  await until("document.getElementById('error').textContent.length>0");
  const validation=await js("document.getElementById('error').textContent");
  await fs.writeFile(base+'/results/browser_validation.json',JSON.stringify({examples:records,invalid_input:validation,passed:true},null,2)+'\n');
  // Export the English report with its real figures, not an image-only text substitute.
  await call('Page.navigate',{url:pathToFileURL(path.resolve(base+'/deliverables/CA6000_SAT_REPORT.html')).href});
  await until("document.title==='CA6000 SAT Report' && Array.from(document.images).every(i=>i.complete && i.naturalWidth>0)");
  const pdf=await call('Page.printToPDF',{printBackground:true,preferCSSPageSize:true,displayHeaderFooter:false});
  await fs.writeFile(base+'/deliverables/CA6000_SAT_REPORT.pdf',Buffer.from(pdf.data,'base64'));
  console.log('PASS: saved-model SAT/UNSAT/error examples, invalid input, report PDF export');
}finally{ws.close()}
