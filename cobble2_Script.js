const canvas = document.getElementById('waves');
const ctx    = canvas.getContext('2d');

function setCanvas() {
  const w = 1920;
  const h = 1080;
  const zoom = window.outerWidth / window.innerWidth;

  canvas.width = w;
  canvas.height = h;
  canvas.style.width = w + "px";
  canvas.style.height = h + "px";
  canvas.style.transform = `scale(${1 / zoom})`;
}

setCanvas();
window.addEventListener('resize', setCanvas);

function hexToRgb(h) {
  const n = parseInt(h.slice(1), 16);
  return { r: (n>>16)&255, g: (n>>8)&255, b: n&255 };
}
function rgbToHex(r,g,b){
  return "#" + [r,g,b].map(x=>x.toString(16).padStart(2,"0")).join("");
}
function interpolateColor(c1,c2,f){
  const a = hexToRgb(c1), b = hexToRgb(c2);
  return rgbToHex(
    Math.round(a.r + f*(b.r - a.r)),
    Math.round(a.g + f*(b.g - a.g)),
    Math.round(a.b + f*(b.b - a.b))
  );
}

const colorStops = ['#383B42','#1C1F26','#383B42'];
const totalWaves = 13;
const spacing    = 150;
const offsetTop  = -550;
const waves      = [];

for (let i = 0; i < totalWaves; i++) {
  const f     = i/(totalWaves-1);
  const color = f < 0.5
    ? interpolateColor(colorStops[0], colorStops[1], f*2)
    : interpolateColor(colorStops[1], colorStops[2], (f-0.5)*2);

  waves.push({
    amp:     40 + Math.random()*15,
    waveLen: 800 + Math.random()*400,
    speed:   0.50 + Math.random()*0.1,
    phase:   Math.random()*Math.PI*2,
    color,
    yBase:   offsetTop + spacing * i
  });
}

function animateWaves() {
  ctx.clearRect(0,0,canvas.width,canvas.height);
  ctx.save();
  ctx.translate(canvas.width/2,canvas.height/2);
  ctx.rotate(-Math.PI/4);
  ctx.translate(-canvas.width/2,-canvas.height/2);

  const span = Math.hypot(canvas.width,canvas.height)*1.2;
  waves.forEach(w=>{
    ctx.beginPath();
    ctx.moveTo(-span, w.yBase);
    for (let x = -span; x <= canvas.width+span; x += 5) {
      const y = w.yBase + w.amp * Math.sin((x/w.waveLen)*2*Math.PI + w.phase);
      ctx.lineTo(x, y);
    }
    ctx.lineTo(canvas.width+span, canvas.height+span);
    ctx.lineTo(-span, canvas.height+span);
    ctx.closePath();
    ctx.fillStyle = w.color;
    ctx.fill();
  });

  ctx.restore();
  waves.forEach(w=> w.phase += 0.005 * w.speed);
  requestAnimationFrame(animateWaves);
}
animateWaves();

document.getElementById('download-form').addEventListener('submit', async e => {
  e.preventDefault();
  const form = new FormData(e.target);
  const resp = await fetch('/download/', {
    method: 'POST',
    body: form
  });
  const result = await resp.json();
  alert(result.message);
});
