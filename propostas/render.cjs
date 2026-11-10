const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1240,height:1754}});
await p.goto('file://'+process.argv[2]);await p.waitForSelector('html[data-pronto]');await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(800);
const els=await p.$$('section.pg');for(let i=0;i<els.length;i++){await els[i].screenshot({path:`${process.argv[3]}/q-${String(i+1).padStart(2,'0')}.png`});}
await p.pdf({path:process.argv[4],width:'1240px',height:'1754px',printBackground:true});await b.close();})();
