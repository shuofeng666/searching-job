const test=require('node:test');
const assert=require('node:assert/strict');
const handle=require('../api/scan.js');
const originalFetch=global.fetch;
function response(){return {code:200,headers:{},setHeader(k,v){this.headers[k]=v;return this;},status(n){this.code=n;return this;},json(value){this.data=value;return this;}};}
function request(method='GET',password=''){return {method,headers:{host:'radar.example.com',origin:'https://radar.example.com','content-type':'application/json'},body:{password}};}
function env(){process.env.GH_ACTIONS_TOKEN='test-token';process.env.SCAN_PASSWORD='this-is-a-long-demo-password';}
function githubRun(created_at,status='completed'){return {ok:true,status:200,json:async()=>({workflow_runs:[{created_at,status,conclusion:'success',html_url:'https://github.com/example/run'}]})};}
test('secret configuration required',async()=>{delete process.env.GH_ACTIONS_TOKEN;delete process.env.SCAN_PASSWORD;const out=response();await handle(request(),out);assert.equal(out.code,503);assert.equal(out.data.configured,false);});
test('rejects invalid origin and password without GitHub calls',async()=>{env();global.fetch=async()=>{throw Error('should not fetch');};const req=request('POST','wrong-password');req.headers.origin='https://attacker.example';let out=response();await handle(req,out);assert.equal(out.code,403);out=response();await handle(request('POST','wrong-password'),out);assert.equal(out.code,401);});
test('authorized request dispatches workflow',async()=>{env();let calls=[];global.fetch=async(url,opt)=>{calls.push({url,method:opt.method||'GET'});if(url.includes('/runs?'))return {ok:true,status:200,json:async()=>({workflow_runs:[]})};return {ok:true,status:204};};const out=response();await handle(request('POST',process.env.SCAN_PASSWORD),out);assert.equal(out.code,202);assert.equal(calls.length,2);assert.equal(calls[1].method,'POST');assert.equal(out.data.ok,true);});
test('cooldown prevents another dispatch',async()=>{env();let calls=0;global.fetch=async()=>{calls++;return githubRun(new Date().toISOString());};const out=response();await handle(request('POST',process.env.SCAN_PASSWORD),out);assert.equal(out.code,429);assert.equal(calls,1);});
test.after(()=>{global.fetch=originalFetch;delete process.env.GH_ACTIONS_TOKEN;delete process.env.SCAN_PASSWORD;});
