// Browser acceptance on an actual generated demo. No test hooks in shipped code.
// PLAYWRIGHT_MODULE=/path/to/playwright CHROME_BIN=/usr/bin/chromium \
// node scripts/test_walkthrough.cjs http://127.0.0.1:PORT/ /tmp/walk-evidence
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const fs = require('node:fs');
const assert = require('node:assert/strict');
const path = require('node:path');
(async () => {
  const url = process.argv[2];
  assert.ok(url, 'Pass the localhost URL of a generated demo review');
  const output = process.argv[3] || '/tmp/interior-walk-evidence';
  fs.mkdirSync(output, {recursive: true});
  const browser = await chromium.launch({executablePath: process.env.CHROME_BIN || '/usr/bin/chromium', headless: true,
    args: ['--no-sandbox', '--use-angle=swiftshader', '--enable-webgl']});
  try {
    const page = await browser.newPage({viewport:{width:1280,height:900},deviceScaleFactor:1});
    const errors = [], failed = [];
    page.on('pageerror', e => errors.push(e.message));
    page.on('response', r => {if(r.status() >= 400) failed.push([r.status(), r.url()]);});
    // Observe matrices actually sent to WebGL, instead of exposing camera globals.
    await page.addInitScript(() => {
      window.probe = {draws:0, view:null, projection:null};
      window.captureKeys = new Set();
      const add = document.addEventListener.bind(document), remove = document.removeEventListener.bind(document);
      document.addEventListener = (name, listener, options) => {
        if (name === 'keydown' && (options === true || options?.capture)) captureKeys.add(listener);
        return add(name, listener, options);
      };
      document.removeEventListener = (name, listener, options) => {
        if (name === 'keydown' && (options === true || options?.capture)) captureKeys.delete(listener);
        return remove(name, listener, options);
      };
      for (const prototype of [WebGLRenderingContext.prototype, WebGL2RenderingContext.prototype]) {
        const locations = new WeakMap();
        const get = prototype.getUniformLocation;
        prototype.getUniformLocation = function(program, name) {const loc=get.call(this,program,name);if(loc)locations.set(loc,name);return loc;};
        const matrix = prototype.uniformMatrix4fv;
        prototype.uniformMatrix4fv = function(location, transpose, value) {
          const name=locations.get(location);
          if(name==='viewMatrix')window.probe.view=Array.from(value);
          if(name==='projectionMatrix')window.probe.projection=Array.from(value);
          return matrix.call(this,location,transpose,value);
        };
        for(const name of ['drawElements','drawArrays']) {
          const draw=prototype[name];prototype[name]=function(...args){window.probe.draws++;return draw.apply(this,args);};
        }
      }
    });
    await page.goto(url);
    await page.waitForSelector('[data-variant=mcm][aria-pressed=true]');
    assert.equal(await page.locator('#model canvas').count(),0);
    assert.equal(await page.evaluate(()=>performance.getEntriesByType('resource').filter(r=>/\.glb(?:\?|$)/.test(r.name)).length),0);
    const model = async () => {
      await page.locator('[data-mode=model]').click();
      await page.waitForFunction(()=>document.querySelector('#model canvas') && !document.querySelector('#status').textContent);
    };
    const pose = () => page.evaluate(()=>structuredClone(window.probe));
    const redraw = async (action) => {const before=await page.evaluate(()=>probe.draws);await action();await page.waitForFunction(n=>probe.draws>n,before);await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));};
    await model();
    await redraw(()=>page.locator('#walk').click());
    const start=await pose();assert.ok(start.view);
    await page.locator('#stage').screenshot({path:path.join(output,'walk-before.png')});
    await redraw(()=>page.locator('#walk-forward').click());
    const moved=await pose();
    assert.notDeepEqual(moved.view,start.view,'View matrix changes');
    assert.deepEqual(moved.projection,start.projection,'Projection/FOV unchanged by forward movement');
    // Camera position from inverse rigid view matrix: -R^T t.
    const eye=m=>[0,1,2].map(i=>-(m[i*4]*m[12]+m[i*4+1]*m[13]+m[i*4+2]*m[14]));
    const a=eye(start.view), b=eye(moved.view);
    const distance=Math.hypot(...a.map((v,i)=>v-b[i]));
    assert.ok(Math.abs(distance-.35)<1e-4, `Actual translation ${distance}`);
    assert.ok(Math.abs(a[1]-b[1])<1e-5);
    // Translation at fixed projection changes the angular separation of near and
    // distant static scene points: parallax rather than a digital enlargement.
    const project=(view,projection,p)=>{
      const v=[0,1,2,3].map(r=>view[r]*p[0]+view[4+r]*p[1]+view[8+r]*p[2]+view[12+r]);
      const clip=[0,1,2,3].map(r=>projection[r]*v[0]+projection[4+r]*v[1]+projection[8+r]*v[2]+projection[12+r]*v[3]);
      return clip[0]/clip[3];
    };
    const near=[a[0]+.5,a[1],a[2]-1],far=[a[0]+.5,a[1],a[2]-3];
    const separation=state=>project(state.view,state.projection,near)-project(state.view,state.projection,far);
    assert.ok(Math.abs(separation(start)-separation(moved))>1e-3);
    await page.locator('#stage').screenshot({path:path.join(output,'walk-after.png')});
    await redraw(()=>page.locator('#reset').click());
    assert.deepEqual((await pose()).view,start.view);
    // Drag / touch-like pointer look changes orientation, without moving the eye.
    const box=await page.locator('#model canvas').boundingBox();
    await page.mouse.move(box.x+box.width/2,box.y+box.height/2);
    await page.mouse.down();await page.mouse.move(box.x+box.width/2+80,box.y+box.height/2+15);await page.mouse.up();
    await page.waitForTimeout(300);
    assert.notDeepEqual((await pose()).view,start.view);
    assert.ok(Math.hypot(...eye((await pose()).view).map((v,i)=>v-a[i]))<1e-4);
    await redraw(()=>page.locator('#reset').click());
    await page.locator('#model canvas').focus();await page.keyboard.down('w');await page.waitForTimeout(250);await page.keyboard.up('w');
    assert.notDeepEqual((await pose()).view,start.view);
    await redraw(()=>page.locator('#reset').click());
    const idleStart=await pose();await page.waitForTimeout(2000);const idleEnd=await pose();
    assert.equal(idleEnd.draws-idleStart.draws,0,'Idle draws');
    await page.locator('[data-mode=render]').click();
    assert.equal(await page.locator('#walk-tools').isVisible(),false);
    const offStart=await pose();await page.waitForTimeout(300);assert.equal((await pose()).draws,offStart.draws);
    await model();
    // Input controls outside the canvas must keep their normal key handling.
    await page.locator('#lighting-time').focus();const inputStart=await pose();await page.keyboard.press('w');
    assert.deepEqual((await pose()).view,inputStart.view);
    await page.locator('#lighting-time').selectOption('night');
    await page.waitForFunction(()=>document.querySelector('canvas').dataset.lightingTime==='night');
    await page.locator('#lighting-lights').selectOption('off');
    await page.waitForFunction(()=>document.querySelector('canvas').dataset.lightingLights==='false');
    await page.locator('#lighting-time').selectOption('day');await page.locator('#lighting-lights').selectOption('on');
    await page.locator('#walk').click();assert.equal(await page.locator('#walls').isEnabled(),true);
    for(const mode of ['layout','mep','drawings','render']) {
      await page.locator(`[data-mode=${mode}]`).click();
      const selector=mode==='render'?'#render':'#plan';
      await page.locator(selector).evaluate(img=>img.decode());
    }
    await page.locator('[data-mode=drawings]').click();
    const options=await page.locator('#sheet-select option').evaluateAll(nodes=>nodes.map(n=>n.value));
    if(options.length>1)await page.locator('#sheet-select').selectOption(options[1]);
    await page.locator('#zoom-in').click();assert.notEqual(await page.locator('#zoom-value').textContent(),'100%');
    await page.locator('#zoom-fit').click();
    const downloadEvent=page.waitForEvent('download');await page.locator('#primary-pdf').click();
    const download=await downloadEvent;assert.match(download.suggestedFilename(),/\.pdf$/);assert.equal(await download.failure(),null);
    for(const style of ['japandi','contemporary','bauhaus','mcm']) {
      await page.locator(`[data-variant=${style}]`).click();
      await page.waitForSelector(`[data-variant=${style}][aria-pressed=true]`);
      await model();assert.equal(await page.locator('#walk').isEnabled(),true);
      await redraw(()=>page.locator('#walk').click());
      await redraw(()=>page.locator('#walk-forward').click());
      assert.equal(await page.locator('#model canvas').count(),1);
    }
    const widths=[];
    for(const width of [320,390,768,1024,1440]) {
      await page.setViewportSize({width,height:900});await page.waitForTimeout(150);
      const fit=await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth);
      assert.ok(fit,`Page fits width ${width}`);widths.push(width);
      for(const id of ['walk-forward','walk-back']) {
        const rect=await page.locator(`#${id}`).boundingBox();assert.ok(rect.height>=44&&rect.width>=44);
      }
      if(width===390)await page.screenshot({path:path.join(output,'mobile.png'),fullPage:true});
    }
    // Exercise real touch pointer events in a mobile browser context.
    const touchContext=await browser.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true,deviceScaleFactor:1});
    const touch=await touchContext.newPage();
    touch.on('pageerror',e=>errors.push(e.message));
    await touch.goto(url);await touch.locator('[data-mode=model]').tap();
    await touch.waitForFunction(()=>document.querySelector('#model canvas')&&!document.querySelector('#status').textContent);
    await touch.locator('#walk').tap();await touch.locator('#walk-forward').tap();
    const touchBefore=await touch.locator('#stage').screenshot();
    const touchCanvas=await touch.locator('#model canvas').boundingBox();
    const client=await touchContext.newCDPSession(touch);
    const x=touchCanvas.x+touchCanvas.width/2,y=touchCanvas.y+touchCanvas.height/2;
    await client.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x,y}]});
    await client.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x:x+60,y}]});
    await client.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
    const touchAfter=await touch.locator('#stage').screenshot();
    assert.notDeepEqual(touchAfter,touchBefore,'Touch drag changes actual scene pixels');
    await touch.locator('#walk-back').tap();await touch.locator('#reset').tap();
    await touch.screenshot({path:path.join(output,'mobile-touch.png'),fullPage:true});
    assert.equal(await touch.locator('#walk-tools').isVisible(),true);
    await touchContext.close();
    // Simulate the visibility predicate/event to cover the hidden-tab guard in
    // headless Chrome, whose real tab visibility is platform dependent.
    await page.evaluate(()=>{Object.defineProperty(document,'hidden',{value:true,configurable:true});document.dispatchEvent(new Event('visibilitychange'));});
    const hiddenDraws=(await pose()).draws;await page.waitForTimeout(300);assert.equal((await pose()).draws,hiddenDraws);
    await page.evaluate(()=>{Object.defineProperty(document,'hidden',{value:false,configurable:true});document.dispatchEvent(new Event('visibilitychange'));});
    // Rapid switching exercises stale model load cleanup.
    for(const style of ['japandi','bauhaus','mcm'])await page.locator(`[data-variant=${style}]`).click();
    await page.waitForSelector('[data-variant=mcm][aria-pressed=true]');await model();
    assert.equal(await page.locator('#model canvas').count(),1);
    // Hold one GLB request while a newer model takes ownership. Only the
    // current OrbitControls document key interceptor may remain registered.
    let requested;
    const pending = new Promise(resolve => { requested = resolve; });
    const slowModel = async route => { requested(); await new Promise(resolve => setTimeout(resolve, 800)); await route.continue(); };
    await page.route('**/japandi/geometry/model.glb', slowModel);
    await page.locator('[data-variant=japandi]').click();await Promise.race([pending,new Promise((_,reject)=>setTimeout(()=>reject(new Error('Delayed GLB route was not reached')),10000))]);
    await page.locator('[data-variant=mcm]').click();
    await page.waitForSelector('[data-variant=mcm][aria-pressed=true]');await model();
    await page.waitForTimeout(1000);
    assert.equal(await page.evaluate(()=>captureKeys.size),1,'One current document key interceptor');
    assert.equal(await page.locator('#model canvas').count(),1);
    await page.unroute('**/japandi/geometry/model.glb',slowModel);
    // A restored context has lost GPU-only render targets, including PMREM.
    // Demand rendering must rebuild them and restore the actual scene unaided.
    await page.waitForTimeout(300);
    const expectedView=(await pose()).view;
    const recoveryStart=await page.evaluate(()=>{
      const gl=document.querySelector('#model canvas').getContext('webgl2');
      window.contextRecovery=gl.getExtension('WEBGL_lose_context');
      if(!contextRecovery)throw new Error('WEBGL_lose_context unavailable');
      probe.view=null;const draws=probe.draws;contextRecovery.loseContext();return draws;
    });
    await page.waitForTimeout(250);
    await page.evaluate(()=>contextRecovery.restoreContext());
    await page.waitForFunction(({view,draws})=>probe.draws>draws&&JSON.stringify(probe.view)===JSON.stringify(view),{view:expectedView,draws:recoveryStart});
    await page.locator('#stage').screenshot({path:path.join(output,'context-restored.png')});
    const settled=(await pose()).draws;await page.waitForTimeout(2000);assert.equal((await pose()).draws,settled,'Restored context settles again');
    assert.deepEqual(errors,[]);assert.deepEqual(failed,[]);
    const result={cameraBefore:a,cameraAfter:b,translationMetres:distance,fixedProjection:true,parallax:true,idleDraws:0,widths,styles:4,touch:true,simulatedHiddenDraws:0,contextRestored:true,currentDocumentKeyListeners:1,errors,failed,
      resources:await page.evaluate(()=>performance.getEntriesByType('resource').filter(r=>/\.(js|glb)$/.test(r.name)).map(r=>({file:r.name.split('/').pop(),bytes:r.decodedBodySize}))) };
    fs.writeFileSync(path.join(output,'results.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result,null,2));
  } finally {await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
