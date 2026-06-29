const fs = require("fs");
const pptxgen = require("pptxgenjs");
const T = JSON.parse(fs.readFileSync(process.argv[2] || "tokens.json"));
const C = T.colors, F = T.fonts, S = T.sizes;
const OUT = process.argv[3] || "deck.pptx";

const p = new pptxgen();
p.defineLayout({ name: "W", width: 13.333, height: 7.5 });
p.layout = "W";

// ---------- MASTERS (built from tokens; structural look lives here) ----------
p.defineSlideMaster({ title: "COVER", background: { color: C.primary }, objects: [
  { text: { text: "", options: { placeholder:"kicker", x:0.9, y:2.4, w:11, h:0.5, color:C.bg, fontFace:F.body, fontSize:S.caption, charSpacing:3 } } },
  { text: { text: "", options: { placeholder:"title", x:0.9, y:2.9, w:11.5, h:2.2, color:C.bg, fontFace:F.head, fontSize:S.title, bold:true, valign:"top" } } },
  { text: { text: "", options: { placeholder:"sub", x:0.9, y:5.2, w:11, h:0.8, color:C.bg, fontFace:F.body, fontSize:S.h2 } } },
]});
p.defineSlideMaster({ title: "SECTION", background: { color: C.ink }, objects: [
  { text: { text: "", options: { placeholder:"num", x:0.9, y:2.1, w:4, h:1.4, color:C.accent, fontFace:F.head, fontSize:S.sectionNum, bold:true } } },
  { text: { text: "", options: { placeholder:"title", x:0.9, y:3.5, w:11, h:1.5, color:C.bg, fontFace:F.head, fontSize:S.sectionTitle, bold:true } } },
]});
p.defineSlideMaster({ title: "CONTENT", background: { color: C.bg }, objects: [
  { text: { text: "", options: { placeholder:"title", x:0.9, y:0.6, w:11.5, h:1.0, color:C.ink, fontFace:F.head, fontSize:S.title, bold:true } } },
  { text: { text: "", options: { placeholder:"body", x:0.9, y:1.9, w:11.5, h:5.0, color:C.ink, fontFace:F.body, fontSize:S.body, valign:"top" } } },
]});
p.defineSlideMaster({ title: "DATA", background: { color: C.surface }, objects: [
  { text: { text: "", options: { placeholder:"title", x:0.9, y:0.6, w:11.5, h:1.0, color:C.ink, fontFace:F.head, fontSize:S.title, bold:true } } },
]});
p.defineSlideMaster({ title: "CLOSING", background: { color: C.primary }, objects: [
  { text: { text: "", options: { placeholder:"title", x:0.9, y:3.0, w:11.5, h:1.5, color:C.bg, fontFace:F.head, fontSize:S.title, bold:true } } },
  { text: { text: "", options: { placeholder:"sub", x:0.9, y:4.6, w:11, h:0.8, color:C.bg, fontFace:F.body, fontSize:S.h2 } } },
]});

// ---------- SLIDE BUILDERS (use masters + tokens) ----------
function cover(kicker, title, sub){ const s=p.addSlide({masterName:"COVER"});
  s.addText(kicker.toUpperCase(),{placeholder:"kicker"}); s.addText(title,{placeholder:"title"}); s.addText(sub,{placeholder:"sub"}); }
function section(num, title){ const s=p.addSlide({masterName:"SECTION"});
  s.addText(num,{placeholder:"num"}); s.addText(title,{placeholder:"title"}); }
function closing(title, sub){ const s=p.addSlide({masterName:"CLOSING"});
  s.addText(title,{placeholder:"title"}); s.addText(sub,{placeholder:"sub"}); }

function iconRows(title, rows){ const s=p.addSlide({masterName:"CONTENT"});
  s.addText(title,{placeholder:"title"});
  const top=2.0, gap=1.35;
  rows.forEach((r,i)=>{ const y=top+i*gap;
    s.addShape(p.ShapeType.ellipse,{x:0.9,y:y,w:0.7,h:0.7,fill:{color:C.primary}});
    s.addText(r.k,{x:0.95,y:y,w:0.6,h:0.7,align:"center",valign:"middle",color:C.bg,fontFace:F.head,fontSize:18,bold:true});
    s.addText(r.h,{x:1.9,y:y-0.05,w:10.6,h:0.5,color:C.ink,fontFace:F.head,fontSize:S.h2,bold:true,margin:0});
    s.addText(r.d,{x:1.9,y:y+0.45,w:10.6,h:0.7,color:C.secondary,fontFace:F.body,fontSize:S.body,margin:0});
  });
}
function twoCol(title, left, right){ const s=p.addSlide({masterName:"CONTENT"});
  s.addText(title,{placeholder:"title"});
  [[left,0.9],[right,7.1]].forEach(([col,x])=>{
    s.addShape(p.ShapeType.roundRect,{x:x,y:2.0,w:5.3,h:4.6,fill:{color:C.surface},rectRadius:0.1,line:{type:"none"}});
    s.addText(col.h,{x:x+0.35,y:2.3,w:4.6,h:0.6,color:C.primary,fontFace:F.head,fontSize:S.h2,bold:true,margin:0});
    s.addText(col.items.map(t=>({text:t,options:{bullet:{indent:14},breakLine:true,paraSpaceAfter:8}})),
      {x:x+0.35,y:3.0,w:4.6,h:3.4,color:C.ink,fontFace:F.body,fontSize:S.body,valign:"top",margin:0});
  });
}
function dataStats(title, stats){ const s=p.addSlide({masterName:"DATA"});
  s.addText(title,{placeholder:"title"});
  const w=11.5/stats.length;
  stats.forEach((st,i)=>{ const x=0.9+i*w;
    s.addText(st.v,{x:x,y:2.6,w:w-0.3,h:1.2,color:C.primary,fontFace:F.head,fontSize:S.stat,bold:true,align:"left",margin:0});
    s.addText(st.l,{x:x,y:3.9,w:w-0.3,h:1.0,color:C.secondary,fontFace:F.body,fontSize:S.body,align:"left",margin:0});
  });
}

// ---------- DEMO DECK ----------
cover("2026 Strategy Review","대체부문 성장방안","Alternative Investment Division · H2 Plan");
section("01","상반기 실적 요약");
dataStats("핵심 지표",[
  {v:"32.3조",l:"수탁고 (달성률 100.8%)"},{v:"91.9억",l:"수익 (목표 190억)"},
  {v:"+7.7%",l:"전년 대비 성장"},{v:"14",l:"본부·사업부"}]);
iconRows("상반기 주요 성과",[
  {k:"01",h:"채권 ETF·MMF 대형화",d:"더드림단기 +9,569억, MMF +2.5조 및 미래연기금풀 유니버스 선정"},
  {k:"02",h:"ETF·공모펀드 Line-up 강화",d:"미국30년국채혼합 액티브 ETF 출시, 신규 상품군 확대"},
  {k:"03",h:"국민연금 아웃퍼폼",d:"+26.0bp 초과수익, 리테일 채권형 1.2조 순증"}]);
twoCol("하반기 중점 계획",
  {h:"상품 전략",items:["글로벌 자산배분형 펀드 출시","초장기 채권 ETF 라인업","크레딧 리서치 상품화"]},
  {h:"조직·운영",items:["크레딧 애널리스트 충원","리스크 조기 인식모델 개발","퇴직연금 운용 고도화"]});
section("02","중장기 성장 기반");
closing("Thank You","대체부문 성장방안 · 2026");

p.writeFile({ fileName: OUT }).then(()=>console.log("deck:", OUT));
