/** Authenticated Vercel Function: only the server holds GitHub credentials. */
const { timingSafeEqual } = require('node:crypto');
const BASE='https://api.github.com/repos/shuofeng666/searching-job/actions/workflows/scan.yml';
const COOLDOWN=15*60*1000;
function equal(a,b){const x=Buffer.from(String(a||'')),y=Buffer.from(String(b||''));return x.length===y.length&&timingSafeEqual(x,y);}
async function github(path,options={}){
 const response=await fetch(BASE+path,{...options,headers:{'Accept':'application/vnd.github+json','Authorization':`Bearer ${process.env.GH_ACTIONS_TOKEN}`,'X-GitHub-Api-Version':'2022-11-28',...options.headers},signal:AbortSignal.timeout(10000)});
 if(!response.ok)throw Error(`GitHub HTTP ${response.status}`);
 return response.status===204?null:response.json();
}
function reply(res,status,payload){res.setHeader('Cache-Control','no-store');return res.status(status).json(payload);}
module.exports=async(req,res)=>{
 if(!['GET','POST'].includes(req.method)){res.setHeader('Allow','GET, POST');return reply(res,405,{error:'Method not allowed'});}
 const configured=!!(process.env.GH_ACTIONS_TOKEN&&(process.env.SCAN_PASSWORD||'').length>=16);
 if(!configured)return reply(res,503,{configured:false,error:'未配置环境变量：请设置 GH_ACTIONS_TOKEN 与至少16位 SCAN_PASSWORD。'});
 if(req.method==='POST'){
  if(!req.headers.origin||req.headers.origin!==`https://${req.headers.host}`)return reply(res,403,{error:'请求来源未授权'});
  if(!String(req.headers['content-type']||'').startsWith('application/json'))return reply(res,415,{error:'Expected JSON'});
  const supplied=req.body&&typeof req.body==='object'?req.body.password:'';
  if(typeof supplied!=='string'||supplied.length>256||!equal(supplied,process.env.SCAN_PASSWORD))return reply(res,401,{error:'扫描密码不正确'});
 }
 try{
  const data=await github('/runs?per_page=1');const run=data.workflow_runs?.[0];
  const last=run?{status:run.status,conclusion:run.conclusion,created_at:run.created_at,url:run.html_url}:null;
  if(req.method==='GET')return reply(res,200,{configured:true,last});
  if(run){
   if(run.status!=='completed')return reply(res,409,{error:'已有扫描正在运行，请等待结束。',last});
   if(Date.now()-Date.parse(run.created_at)<COOLDOWN)return reply(res,429,{error:'距上次启动未满15分钟，请稍后再试。',last});
  }
  await github('/dispatches',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({ref:'main'})});
  return reply(res,202,{ok:true,message:'已提交 GitHub Actions；结果生成并部署后网页会更新。'});
 }catch(error){
  console.error('Scan API error:',String(error.message).slice(0,80));
  return reply(res,502,{error:'GitHub Actions 暂时不可用，请检查 Token 权限或打开 GitHub Actions。'});
 }
};
