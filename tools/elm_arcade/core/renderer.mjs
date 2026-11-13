const VERTEX = `
attribute vec2 aPosition;
varying vec2 vUv;
void main() { vUv=aPosition*.5+.5; gl_Position=vec4(aPosition,0.,1.); }
`;
const FRAGMENT = `
precision highp float;
varying vec2 vUv;
uniform vec2 uResolution;
uniform float uTime;
uniform float uDetail;
uniform vec3 uEye;
uniform vec3 uForward;
uniform vec3 uUp;
float water(vec2 p) {
  float h=sin(p.x*1.4+uTime*.7)*.19+cos(p.y*1.8-uTime*.5)*.14;
  h+=sin((p.x+p.y)*3.6+uTime)*.07*uDetail;
  h+=sin(p.x*7.-p.y*5.+uTime*1.4)*.025*uDetail;
  return h;
}
vec3 sky(vec3 ray) {
  float horizon=pow(1.-abs(ray.y),3.);
  return mix(vec3(.012,.023,.09),vec3(.08,.27,.39),max(0.,ray.y))+
    horizon*vec3(.09,.025,.15)+pow(max(0.,dot(ray,normalize(vec3(-.5,.7,-.4)))),64.)*vec3(1.,.75,.45);
}
void main() {
  vec2 uv=(vUv*2.-1.)*vec2(uResolution.x/uResolution.y,1.);
  vec3 right=normalize(cross(uForward,uUp));
  vec3 ray=normalize(uForward+right*uv.x*.65+uUp*uv.y*.65);
  vec3 eye=uEye*.16+vec3(0.,2.3,0.);
  vec3 color=sky(ray);
  if(ray.y<-.025) {
    float t=clamp(-eye.y/ray.y,0.,80.);
    for(int i=0;i<5;i++) { vec3 p=eye+ray*t; t=clamp(t+(water(p.xz)-p.y)/ray.y,0.,80.); }
    vec3 p=eye+ray*t;
    float e=.025;
    vec3 n=normalize(vec3(water(p.xz-vec2(e,0.))-water(p.xz+vec2(e,0.)),2.*e,
      water(p.xz-vec2(0.,e))-water(p.xz+vec2(0.,e))));
    float fresnel=.06+.94*pow(1.-max(0.,dot(-ray,n)),5.);
    vec3 reflected=sky(reflect(ray,n));
    vec3 refracted=refract(ray,n,1./1.333);
    vec2 floorPoint=p.xz+refracted.xz*(2./max(.1,-refracted.y));
    float caustic=pow(.5+.5*sin(floorPoint.x*3.+sin(floorPoint.y*2.+uTime)),5.);
    vec3 deep=vec3(.01,.16,.22)+vec3(.025,.12,.13)*caustic;
    float gloss=pow(max(0.,dot(reflect(-normalize(vec3(-.5,.8,-.3)),n),-ray)),100.);
    color=mix(deep,reflected,fresnel)+gloss*vec3(1.,.75,.5)*1.8;
    color=mix(color,sky(ray),1.-exp(-t*.018));
  }
  color*=1.-.24*dot(vUv-.5,vUv-.5);
  gl_FragColor=vec4(pow(max(color,vec3(0.)),vec3(.8)),1.);
}
`;
export class LiquidRenderer {
  constructor(canvas, camera, { quality = "high", reducedMotion = false } = {}) {
    this.canvas = canvas; this.camera = camera; this.quality = quality; this.reducedMotion = reducedMotion;
    this.originalVisibility = canvas?.style?.visibility || "";
    if (canvas?.style && quality === "low") canvas.style.visibility = "hidden";
    this.gl = null; this.ctx = null; this.lost = false; this.resources = [];
    this.onLost = event => { event.preventDefault(); this.lost = true; if (canvas?.style) canvas.style.visibility = "hidden"; };
    this.onRestored = () => {
      this.lost = false; this.initialize();
      if (canvas?.style) canvas.style.visibility = this.quality === "low" ? "hidden" : this.originalVisibility;
    };
    canvas?.addEventListener?.("webglcontextlost", this.onLost);
    canvas?.addEventListener?.("webglcontextrestored", this.onRestored);
    this.initialize();
  }
  initialize() {
    if (!this.canvas || this.quality === "low") return;
    try {
      const gl = this.canvas.getContext("webgl", { alpha: false, antialias: this.quality !== "low", powerPreference: "low-power" });
      if (!gl) throw new Error("WebGL unavailable");
      this.gl = gl; this.resources = [];
      const compile = (type, source) => {
        const shader = gl.createShader(type); this.resources.push(["shader", shader]);
        gl.shaderSource(shader, source); gl.compileShader(shader);
        if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) throw new Error("Shader compilation failed");
        return shader;
      };
      const program = gl.createProgram(); this.resources.push(["program", program]);
      gl.attachShader(program, compile(gl.VERTEX_SHADER, VERTEX)); gl.attachShader(program, compile(gl.FRAGMENT_SHADER, FRAGMENT));
      gl.linkProgram(program); if (!gl.getProgramParameter(program, gl.LINK_STATUS)) throw new Error("Shader linking failed");
      this.program = program; gl.useProgram(program);
      this.buffer = gl.createBuffer(); this.resources.push(["buffer", this.buffer]);
      gl.bindBuffer(gl.ARRAY_BUFFER, this.buffer);
      gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, -1, 1, 1, -1, 1, 1]), gl.STATIC_DRAW);
      this.attribute = gl.getAttribLocation(program, "aPosition");
      this.uniforms = Object.fromEntries(["uResolution", "uTime", "uDetail", "uEye", "uForward", "uUp"].map(n => [n, gl.getUniformLocation(program, n)]));
    } catch {
      this.disposeGL(); this.gl = null;
      try { this.ctx = this.canvas.getContext("2d"); } catch { this.ctx = null; }
    }
  }
  resize(width = this.canvas?.clientWidth || 800, height = this.canvas?.clientHeight || 600, dpr = globalThis.devicePixelRatio || 1) {
    if (!this.canvas) return;
    const scale = this.quality === "low" ? 0.65 : Math.min(2, dpr);
    const w = Math.max(1, Math.round(width * scale)), h = Math.max(1, Math.round(height * scale));
    if (this.canvas.width !== w) this.canvas.width = w;
    if (this.canvas.height !== h) this.canvas.height = h;
  }
  setQuality(quality, reducedMotion = this.reducedMotion) {
    this.quality = quality === "low" ? "low" : "high"; this.reducedMotion = Boolean(reducedMotion);
    if (this.canvas?.style) this.canvas.style.visibility = this.quality === "low" || this.lost ? "hidden" : this.originalVisibility;
    if (this.quality === "high" && !this.gl && !this.ctx) this.initialize();
    this.resize();
  }
  render(time = 0) {
    if (!this.canvas || this.lost || this.quality === "low") return;
    const { width, height } = this.canvas, t = this.reducedMotion ? 0 : time;
    const gl = this.gl;
    if (gl) {
      gl.viewport(0, 0, width, height); gl.useProgram(this.program);
      gl.bindBuffer(gl.ARRAY_BUFFER, this.buffer); gl.enableVertexAttribArray(this.attribute);
      gl.vertexAttribPointer(this.attribute, 2, gl.FLOAT, false, 0, 0);
      const listener = this.camera?.getListener?.() || { position: { x: 0, y: 0, z: 10 }, forward: { x: 0, y: -0.3, z: -1 }, up: { x: 0, y: 1, z: 0 } };
      gl.uniform2f(this.uniforms.uResolution, width, height); gl.uniform1f(this.uniforms.uTime, t);
      gl.uniform1f(this.uniforms.uDetail, this.quality === "low" ? 0 : 1);
      for (const [name, vector] of [["uEye", listener.position], ["uForward", listener.forward], ["uUp", listener.up]]) gl.uniform3f(this.uniforms[name], vector.x, vector.y, vector.z);
      gl.drawArrays(gl.TRIANGLES, 0, 6);
    } else if (this.ctx) {
      const ctx = this.ctx, gradient = ctx.createLinearGradient(0, 0, width, height);
      gradient.addColorStop(0, "#07132e"); gradient.addColorStop(1, "#14556b"); ctx.fillStyle = gradient; ctx.fillRect(0, 0, width, height);
      ctx.strokeStyle = "#4f97ad"; ctx.globalAlpha = 0.18; ctx.lineWidth = 2;
      for (let row = 0; row < 10; row++) {
        ctx.beginPath();
        for (let x = 0; x <= width; x += 16) {
          const y = height * (0.3 + row * 0.08) + Math.sin(x / 100 + t * 0.4 + row) * (10 + row * 2);
          if (!x) ctx.moveTo(x, y); else ctx.lineTo(x, y);
        }
        ctx.stroke();
      }
      ctx.globalAlpha = 1;
    }
  }
  disposeGL() {
    if (!this.gl) return;
    for (const [kind, resource] of this.resources) {
      if (kind === "shader") this.gl.deleteShader(resource);
      if (kind === "program") this.gl.deleteProgram(resource);
      if (kind === "buffer") this.gl.deleteBuffer(resource);
    }
    this.resources = [];
  }
  destroy() {
    this.disposeGL();
    if (this.canvas?.style) this.canvas.style.visibility = this.originalVisibility;
    this.canvas?.removeEventListener?.("webglcontextlost", this.onLost);
    this.canvas?.removeEventListener?.("webglcontextrestored", this.onRestored);
    this.gl = this.ctx = null;
  }
}
