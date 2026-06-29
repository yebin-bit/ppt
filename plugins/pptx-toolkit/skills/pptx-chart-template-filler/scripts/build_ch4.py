"""Driver: build Kiwoom ch4 본부실적 deck from a template using pptx_template.
This is the *template-specific config* (shape-id map + calibration + data).
The reusable plumbing lives in pptx_template.py."""
import sys, os, shutil
sys.path.insert(0, os.path.dirname(__file__))
import pptx_template as T

TEMPLATE_UNPACKED = sys.argv[1] if len(sys.argv) > 1 else '/tmp/tmpl_unpacked'
OUT = sys.argv[2] if len(sys.argv) > 2 else '/tmp/ch4_skill_out.pptx'
WORK = '/tmp/ch4_skill_work'

EMU = 9525
# --- ch4 template config (shape ids + chart frame tops for 달성률 calibration) ---
ID = dict(title='43', summary='20',
          perf=[('100','121'), ('122','124')], perf3='125',
          plan=[('136','138'), ('139','141')],
          suik_hdr='51', suik_unit='55',
          sk_line='52', sk_box_bg='53', sk_box_txt='54',
          sy_line='10', sy_box_bg='11', sy_box_txt='153')
SK_FRAME_TOP, SY_FRAME_TOP = 273, 520
PLOT_TOP_OFF, PLOT_H = 47.4, 134   # calibrated to this template's PowerPoint plot area

def line_y(frame_top, h1, axmax):
    return frame_top + PLOT_TOP_OFF + (1 - h1/axmax) * PLOT_H

def apply_division(work, slide_file, sk_chart, sy_chart, d):
    # charts
    T.edit_chart(work, sk_chart, d['sk'][:3], d['sk'][3], d['sk'][4])
    T.edit_chart(work, sy_chart, d['sy'][:3], d['sy'][3], d['sy'][4])
    # slide text + positions
    sp = os.path.join(work, 'ppt', 'slides', slide_file)
    s = T.load(sp)
    T.set_text(s, ID['title'], f'4. 본부실적 및 세부계획  {d["no"]} {d["name"]}')
    T.set_text(s, ID['summary'], d['summary'])
    T.set_text(s, ID['perf'][0][0], d['p1'][0]); T.set_text(s, ID['perf'][0][1], d['p1'][1])
    T.set_text(s, ID['perf'][1][0], d['p2'][0]); T.set_text(s, ID['perf'][1][1], d['p2'][1])
    T.set_text(s, ID['perf3'], d['p3'])
    T.set_text(s, ID['plan'][0][0], d['q1'][0]); T.set_text(s, ID['plan'][0][1], d['q1'][1])
    T.set_text(s, ID['plan'][1][0], d['q2'][0]); T.set_text(s, ID['plan'][1][1], d['q2'][1])
    T.set_text(s, ID['suik_hdr'], d['sy'][6])
    if d['sy'][7] != '억원':
        T.set_text(s, ID['suik_unit'], f'(단위 : {d["sy"][7]})')
    T.set_run_by_marker(s, ID['sk_box_txt'], '%', f'{d["sk"][5]}%')
    T.set_run_by_marker(s, ID['sy_box_txt'], '%', f'{d["sy"][5]}%')
    yk = line_y(SK_FRAME_TOP, d['sk'][1], d['sk'][3]); ys = line_y(SY_FRAME_TOP, d['sy'][1], d['sy'][3])
    for sid, y in [(ID['sk_line'],yk),(ID['sk_box_bg'],yk-21.4),(ID['sk_box_txt'],yk-21.4),
                   (ID['sy_line'],ys),(ID['sy_box_bg'],ys-21.4),(ID['sy_box_txt'],ys-21.4)]:
        T.set_shape_y(s, sid, y*EMU)
    T.save(s, sp)

from ch4_data import DIVS

def main():
    shutil.rmtree(WORK, ignore_errors=True)
    shutil.copytree(TEMPLATE_UNPACKED, WORK)
    for i, d in enumerate(DIVS):
        if i == 0:
            slide, sk_c, sy_c = 'slide1.xml', 'chart1.xml', 'chart2.xml'
        else:
            slide, cmap = T.clone_slide(WORK, 'slide1.xml')   # clones chart bundles automatically
            sk_c, sy_c = cmap['chart1.xml'], cmap['chart2.xml']
        apply_division(WORK, slide, sk_c, sy_c, d)
        print(f'{slide}: {d["name"]} -> {sk_c}/{sy_c}')
    issues = T.verify(WORK)
    print('VERIFY:', 'OK' if not issues else issues)
    T.pack(WORK, OUT)
    print('PACKED', OUT)

if __name__ == '__main__':
    main()
