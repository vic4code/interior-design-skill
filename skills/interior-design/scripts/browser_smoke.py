"""Developer-only real Chromium checks. Requires Python Playwright and Chromium.

Run with a dev/preview server already listening; screenshots go outside the repo.
"""
import argparse
import io
import json
import os
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright
from PIL import Image


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--url',default='http://127.0.0.1:5173');parser.add_argument('--out',type=Path,default=Path('/tmp/interior-browser'));args=parser.parse_args()
    binary=os.environ.get('INTERIOR_CHROMIUM') or shutil.which('chromium') or shutil.which('google-chrome')
    args.out.mkdir(parents=True,exist_ok=True)
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=binary,headless=True,args=['--no-sandbox','--enable-unsafe-swiftshader'])
        page=browser.new_page(viewport={'width':1440,'height':1100},device_scale_factor=1)
        errors=[];failed=[];gpu_warnings=[]
        page.on('pageerror',lambda error:errors.append(str(error)))
        def console_message(msg):
            if msg.type not in ('error','warning'): return
            if msg.type=='warning' and msg.text.startswith('[.WebGL-') and 'GPU stall due to ReadPixels' in msg.text:
                gpu_warnings.append(msg.text)
            else: errors.append(msg.text)
        page.on('console',console_message)
        page.on('response',lambda response:failed.append(f'{response.status} {response.url}') if response.status>=400 else None)
        page.goto(args.url,wait_until='networkidle')
        page.get_by_role('heading',name='Warm Studio / 光木工作室').wait_for()
        page.wait_for_function("document.getElementById('render').complete && document.getElementById('render').naturalWidth === 1920")
        assert page.locator('#reviews li').count()==7
        assert page.locator('#downloads a').count()==10
        for width in (320,768,1024,1440):
            page.set_viewport_size({'width':width,'height':1000})
            assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'),f'Horizontal overflow at {width}'
            page.screenshot(path=str(args.out/f'viewer-{width}.png'),full_page=True)
        page.get_by_role('button',name='尺寸平面',exact=True).click()
        assert page.locator('#plan').is_visible()
        page.wait_for_function("document.getElementById('plan').complete && document.getElementById('plan').naturalWidth > 0")
        with page.expect_download() as event:page.get_by_role('link',name='完整設計圖面 / PDF').click()
        download=event.value;download.save_as(str(args.out/'downloaded-drawings.pdf'))
        assert (args.out/'downloaded-drawings.pdf').read_bytes().startswith(b'%PDF-')
        page.get_by_role('button',name='3D 空間',exact=True).click()
        page.wait_for_function("document.getElementById('status').textContent === '' && document.querySelector('#model canvas') !== null",timeout=30000)
        page.locator('#rotate').click();page.locator('#reset').click();page.locator('#walls').check();page.locator('#walls').uncheck()
        page.locator('#model canvas').focus();page.keyboard.press('ArrowLeft')
        image=Image.open(io.BytesIO(page.locator('#model canvas').screenshot()))
        assert len(image.getcolors(maxcolors=10000000))>30,'Blank WebGL canvas'
        page.screenshot(path=str(args.out/'viewer-3d.png'),full_page=True)
        assert not errors,errors
        assert not failed,failed
        page.close()
        # Error path: missing generated package must give useful next steps.
        page=browser.new_page()
        page.route('**/generated/manifest.json',lambda route:route.fulfill(status=404,body='missing'))
        page.goto(args.url)
        page.get_by_role('heading',name='尚未建立設計交付包').wait_for()
        assert 'scripts/project.py build' in page.locator('#status').inner_text()
        assert page.locator('[data-mode]:disabled').count()==3
        page.close()
        # Drawings-only packages are useful without Blender and must not imply a model exists.
        page=browser.new_page()
        def drawings_only(route):
            package=route.fetch().json()
            package['has_model']=False
            package['files']=[f for f in package['files'] if f['name'] not in ('scene.glb','scene.blend','render.png','render-settings.json')]
            route.fulfill(json=package)
        page.route('**/generated/manifest.json',drawings_only)
        page.goto(args.url)
        page.get_by_role('heading',name='Warm Studio / 光木工作室').wait_for()
        assert page.locator('#plan').is_visible()
        page.get_by_role('button',name='3D 空間',exact=True).click()
        assert '尚未產出' in page.locator('#status').inner_text()
        assert page.locator('#model-controls').is_hidden()
        browser.close()
    result={'viewports':[320,768,1024,1440],'checks':['HD image','no overflow','plan','PDF download','GLB WebGL render','wall toggle','camera controls','keyboard','empty state','drawings-only fallback'],'console_errors':errors,'failed_requests':failed,'software_gpu_screenshot_warnings':gpu_warnings}
    (args.out/'result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))


if __name__=='__main__':main()
