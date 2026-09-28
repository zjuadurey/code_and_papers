// Local Chromium DevTools smoke check. No npm packages required (Node 22).
import fs from 'node:fs/promises';
const targets = await (await fetch('http://127.0.0.1:9228/json')).json();
const ws = new WebSocket(targets.find(t => t.type === 'page').webSocketDebuggerUrl);
await new Promise(resolve => ws.addEventListener('open', resolve, {once:true}));
let counter=0;const waiting=new Map();
ws.addEventListener('message',event=>{const m=JSON.parse(event.data);if(waiting.has(m.id)){
  const {resolve,reject}=waiting.get(m.id);waiting.delete(m.id);m.error?reject(Error(JSON.stringify(m.error))):resolve(m.result);
}});
function call(method,params={}){return new Promise((resolve,reject)=>{let id=++counter;waiting.set(id,{resolve,reject});ws.send(JSON.stringify({id,method,params}));});}
async function js(expression){let r=await call('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value;}
async function until(expression){let end=Date.now()+20000;while(Date.now()<end){if(await js(expression))return;await new Promise(r=>setTimeout(r,100));}throw Error('Browser check timed out: '+expression);}
try{
  await call('Emulation.setDeviceMetricsOverride',{width:1600,height:1140,deviceScaleFactor:1,mobile:false});
  await call('Page.navigate',{url:'http://127.0.0.1:8765/'});
  await until("document.body.dataset.ready === 'true'");
  await js("document.getElementById('run').click()");
  await until("document.getElementById('status').textContent.startsWith('PASS')");
  let satisfiable=await js("document.getElementById('status').textContent");
  let png=await call('Page.captureScreenshot',{format:'png'});
  await fs.writeFile('coursework/artifacts/browser-search.png',Buffer.from(png.data,'base64'));
  await js("document.getElementById('preset').value='unsat';document.getElementById('preset').dispatchEvent(new Event('change'));document.getElementById('run').click()");
  await until("document.getElementById('status').textContent.includes('hybrid=false')");
  let unsatisfiable=await js("document.getElementById('status').textContent");
  if(!unsatisfiable.startsWith('PASS'))throw Error(unsatisfiable);
  await js("document.getElementById('retainTab').click()");
  let retained=await js("document.getElementById('retainStatus').textContent");
  if(!retained.startsWith('PASS'))throw Error(retained);
  await fs.writeFile('coursework/artifacts/browser-retained.png',Buffer.from((await call('Page.captureScreenshot',{format:'png'})).data,'base64'));
  await js("document.getElementById('searchTab').click();document.getElementById('clauses').value='[[99]]';document.getElementById('run').click()");
  await until("document.getElementById('error').textContent.length > 0");
  let invalidInput=await js("document.getElementById('error').textContent");
  await fs.writeFile('coursework/artifacts/browser_checks.json',JSON.stringify({satisfiable,unsatisfiable,retained,invalidInput,passed:true},null,2)+'\n');
  console.log('Browser checks PASS: real SAT / UNSAT runs, retained callbacks, invalid input');
}finally{ws.close();}
