
const $=s=>document.querySelector(s);
let current=null;
function status(t,type=""){const e=$("#status");e.textContent=t;e.className="status "+type}
function fmt(sec){if(!sec)return"";sec=Math.floor(sec);return `${Math.floor(sec/60)}:${String(sec%60).padStart(2,"0")}`}
$("#analyze").onclick=async()=>{
 const url=$("#url").value.trim(); if(!url){status("Vui lòng dán liên kết.","error");return}
 $("#result").classList.add("hidden"); status("⏳ Đang phân tích liên kết...");
 try{
   const r=await fetch("/api/info?url="+encodeURIComponent(url));
   const d=await r.json(); if(!r.ok) throw new Error(d.detail||"Không phân tích được.");
   current=d; $("#thumb").src=d.thumbnail||""; $("#title").textContent=d.title||"Video";
   $("#uploader").textContent=[d.uploader,fmt(d.duration)].filter(Boolean).join(" • ");
   $("#platform").textContent=d.platform;
   const q=$("#quality");q.innerHTML="";
   (d.qualities||[1080,720,480]).forEach(h=>{let o=document.createElement("option");o.value=h;o.textContent=h+"p";q.appendChild(o)});
   $("#result").classList.remove("hidden");status("✓ Đã phân tích. Chọn chất lượng để tải.","ok");
 }catch(e){status("⚠ "+e.message,"error")}
};
function go(audio=false){
 const url=$("#url").value.trim(); if(!url)return;
 status(audio?"♫ Đang chuẩn bị MP3...":"⬇ Đang chuẩn bị tải video...");
 const h=$("#quality").value||720;
 window.location.href=`/api/download?url=${encodeURIComponent(url)}&height=${h}&audio=${audio}`;
}
$("#videoBtn").onclick=()=>go(false); $("#audioBtn").onclick=()=>go(true);
$("#url").addEventListener("keydown",e=>{if(e.key==="Enter")$("#analyze").click()});
