"""
pptx_template.py — Fill a PowerPoint template that contains NATIVE charts by
duplicating a master slide and injecting per-item data.

Why this exists: PowerPoint native charts are a *bundle* (chart + colors + style
+ rels [+ embedded data]). Duplicating a slide must clone the WHOLE bundle and
rewire every relationship/Content-Types entry, or PowerPoint will "repair" the
file and silently drop slides. add_slide.py (pptx skill) does the slide-level
plumbing but NOT the chart bundle — this module fills that gap.

Template-agnostic. You supply: which shapes/charts to edit (by cNvPr id / chart
auto-discovery) and the data. See SKILL.md for the gotcha checklist.
"""
import os, re, glob, shutil, subprocess
from defusedxml.minidom import parse

# ---------------- low-level XML ----------------
def _write(dom, path):
    with open(path, 'wb') as f:
        f.write(dom.toxml(encoding='UTF-8'))

def load(path):
    return parse(path)

def save(dom, path):
    _write(dom, path)

# ---------------- shape / text editing ----------------
def find_shape(dom, sid):
    """Find any shape (p:sp / p:cxnSp / p:graphicFrame / p:pic) by cNvPr id."""
    for tag in ('p:sp', 'p:cxnSp', 'p:graphicFrame', 'p:pic'):
        for el in dom.getElementsByTagName(tag):
            cn = el.getElementsByTagName('p:cNvPr')
            if cn and cn[0].getAttribute('id') == str(sid):
                return el
    return None

def set_shape_y(dom, sid, y_emu):
    find_shape(dom, sid).getElementsByTagName('a:off')[0].setAttribute('y', str(int(y_emu)))

def set_shape_x(dom, sid, x_emu):
    find_shape(dom, sid).getElementsByTagName('a:off')[0].setAttribute('x', str(int(x_emu)))

def _rebuild_paragraph(p, text, doc):
    rs = p.getElementsByTagName('a:r')
    rpr = rs[0].getElementsByTagName('a:rPr')[0].cloneNode(True) if (rs and rs[0].getElementsByTagName('a:rPr')) else None
    for r in list(rs): p.removeChild(r)
    for e in list(p.getElementsByTagName('a:endParaRPr')): p.removeChild(e)
    r = doc.createElement('a:r')
    if rpr is not None: r.appendChild(rpr)
    t = doc.createElement('a:t'); t.appendChild(doc.createTextNode(text)); r.appendChild(t)
    p.appendChild(r)

def set_text(dom, sid, lines):
    """Rewrite a text box's paragraphs cleanly (handles fragmented runs).
    `lines` = list of strings, one per paragraph. Preserves each paragraph's
    style by cloning its first run's rPr."""
    if isinstance(lines, str): lines = [lines]
    el = find_shape(dom, sid)
    tb = el.getElementsByTagName('p:txBody')[0]
    ps = tb.getElementsByTagName('a:p')
    while len(ps) < len(lines):
        tb.appendChild(ps[-1].cloneNode(True)); ps = tb.getElementsByTagName('a:p')
    while len(ps) > len(lines):
        tb.removeChild(ps[-1]); ps = tb.getElementsByTagName('a:p')
    for i, line in enumerate(lines):
        _rebuild_paragraph(ps[i], line, dom)

def set_run_by_marker(dom, sid, marker, new_text):
    """Robustly set the run whose text contains `marker` (e.g. '%')."""
    el = find_shape(dom, sid)
    ts = el.getElementsByTagName('a:t')
    for t in ts:
        if t.firstChild and marker in (t.firstChild.nodeValue or ''):
            t.firstChild.nodeValue = new_text; return
    if ts and ts[-1].firstChild:
        ts[-1].firstChild.nodeValue = new_text

# ---------------- chart editing ----------------
def edit_chart(unpacked, chart_name, values, axis_max=None, major_unit=None):
    """Set the cached values of the chart's first c:val series; optionally axis
    max / major unit. Always strips externalData (dead network links)."""
    path = os.path.join(unpacked, 'ppt', 'charts', chart_name)
    c = parse(path)
    vals = c.getElementsByTagName('c:val')
    if vals:
        vs = vals[0].getElementsByTagName('c:v')
        for v, nv in zip(vs, values):
            if v.firstChild: v.firstChild.nodeValue = str(nv)
            else: v.appendChild(c.createTextNode(str(nv)))
    if axis_max is not None:
        for mx in c.getElementsByTagName('c:max'): mx.setAttribute('val', str(axis_max))
    if major_unit is not None:
        for m in c.getElementsByTagName('c:majorUnit'): m.setAttribute('val', str(major_unit))
    for ed in c.getElementsByTagName('c:externalData'): ed.parentNode.removeChild(ed)
    _write(c, path)

def set_chart_categories(unpacked, chart_name, cats):
    """Rename the category labels (c:cat strCache pts). Useful for breakdown charts."""
    path = os.path.join(unpacked, 'ppt', 'charts', chart_name)
    c = parse(path)
    catEl = c.getElementsByTagName('c:cat')
    if catEl:
        pts = catEl[0].getElementsByTagName('c:pt')
        for pt, name in zip(pts, cats):
            vs = pt.getElementsByTagName('c:v')
            if vs and vs[0].firstChild: vs[0].firstChild.nodeValue = name
    _write(c, path)

# ---------------- Content_Types ----------------
def _ct_path(unpacked): return os.path.join(unpacked, '[Content_Types].xml')

def _ct_get_type(unpacked, partname):
    s = open(_ct_path(unpacked), encoding='utf-8').read()
    m = re.search(r'PartName="%s" ContentType="([^"]+)"' % re.escape(partname), s)
    return m.group(1) if m else None

def _ct_add(unpacked, partname, ctype):
    p = _ct_path(unpacked); s = open(p, encoding='utf-8').read()
    if partname not in s:
        s = s.replace('</Types>', '<Override PartName="%s" ContentType="%s"/></Types>' % (partname, ctype))
        open(p, 'w', encoding='utf-8').write(s)

# ---------------- chart bundle cloning ----------------
def _max_num(dirpath, prefix):
    n = 0
    for f in glob.glob(os.path.join(dirpath, prefix + '*.xml')):
        m = re.match(prefix + r'(\d+)\.xml$', os.path.basename(f))
        if m: n = max(n, int(m.group(1)))
    return n

def clone_chart_bundle(unpacked, src_chart):
    """Clone chart{N}.xml + its colors/style parts as NEW independent parts.
    Returns the new chart filename. Each clone gets its OWN colors/style
    (PowerPoint requires this — shared color/style parts cause repair)."""
    charts = os.path.join(unpacked, 'ppt', 'charts')
    rels = os.path.join(charts, '_rels')
    dst_n = _max_num(charts, 'chart') + 1
    src_base = src_chart[:-4]               # 'chart1'
    dst_chart = f'chart{dst_n}.xml'
    shutil.copy(os.path.join(charts, src_chart), os.path.join(charts, dst_chart))
    _ct_add(unpacked, f'/ppt/charts/{dst_chart}', _ct_get_type(unpacked, f'/ppt/charts/{src_chart}'))
    # clone its rels, and any colors/style targets
    src_rels = os.path.join(rels, f'{src_base}.xml.rels')
    dst_rels = os.path.join(rels, f'{dst_chart}.rels')
    if os.path.exists(src_rels):
        shutil.copy(src_rels, dst_rels)
        rl = parse(dst_rels)
        for r in list(rl.getElementsByTagName('Relationship')):
            tgt = r.getAttribute('Target'); typ = r.getAttribute('Type')
            if r.getAttribute('TargetMode') == 'External' or 'oleObject' in typ:
                r.parentNode.removeChild(r); continue
            for kind in ('colors', 'style'):
                if os.path.basename(tgt).startswith(kind):
                    new_k = f'{kind}{dst_n}.xml'
                    shutil.copy(os.path.join(charts, os.path.basename(tgt)), os.path.join(charts, new_k))
                    _ct_add(unpacked, f'/ppt/charts/{new_k}', _ct_get_type(unpacked, f'/ppt/charts/{os.path.basename(tgt)}'))
                    r.setAttribute('Target', new_k)
        _write(rl, dst_rels)
    return dst_chart

# ---------------- slide cloning (auto-clones chart bundles) ----------------
def _next_slide_num(unpacked):
    return _max_num(os.path.join(unpacked, 'ppt', 'slides'), 'slide') + 1

def _pres_add_slide(unpacked, slide_file):
    prels = os.path.join(unpacked, 'ppt', '_rels', 'presentation.xml.rels')
    s = open(prels, encoding='utf-8').read()
    rid = max([int(x) for x in re.findall(r'Id="rId(\d+)"', s)] or [0]) + 1
    s = s.replace('</Relationships>',
        f'<Relationship Id="rId{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/{slide_file}"/></Relationships>')
    open(prels, 'w', encoding='utf-8').write(s)
    pres = os.path.join(unpacked, 'ppt', 'presentation.xml')
    p = open(pres, encoding='utf-8').read()
    sid = max([int(x) for x in re.findall(r'<p:sldId[^>]*id="(\d+)"', p)] or [255]) + 1
    p = p.replace('</p:sldIdLst>', f'<p:sldId id="{sid}" r:id="rId{rid}"/></p:sldIdLst>')
    open(pres, 'w', encoding='utf-8').write(p)

def clone_slide(unpacked, src_slide='slide1.xml'):
    """Duplicate a slide AND every native-chart bundle it references.
    Returns (new_slide_file, {old_chart_name: new_chart_name}).
    Always clone from a PRISTINE master slide, not one already edited."""
    slides = os.path.join(unpacked, 'ppt', 'slides')
    srels = os.path.join(slides, '_rels')
    n = _next_slide_num(unpacked)
    dst = f'slide{n}.xml'
    shutil.copy(os.path.join(slides, src_slide), os.path.join(slides, dst))
    shutil.copy(os.path.join(srels, f'{src_slide}.rels'), os.path.join(srels, f'{dst}.rels'))
    _ct_add(unpacked, f'/ppt/slides/{dst}', _ct_get_type(unpacked, f'/ppt/slides/{src_slide}'))
    # clone each chart this slide points to, repoint its rels
    chart_map = {}
    rl = parse(os.path.join(srels, f'{dst}.rels'))
    for r in rl.getElementsByTagName('Relationship'):
        if r.getAttribute('Type').endswith('/chart'):
            old = os.path.basename(r.getAttribute('Target'))
            new = clone_chart_bundle(unpacked, old)
            chart_map[old] = new
            r.setAttribute('Target', f'../charts/{new}')
    _write(rl, os.path.join(srels, f'{dst}.rels'))
    _pres_add_slide(unpacked, dst)
    return dst, chart_map

# ---------------- packing (bypasses pack.py vendor-ext false positive) ----------------
def pack(unpacked, out_pptx):
    """Zip the package with [Content_Types].xml first. Use this instead of
    pack.py when charts carry c15/c16 vendor extensions (pack.py flags them as
    false-positive 'empty' errors, but PowerPoint accepts them)."""
    if os.path.exists(out_pptx): os.remove(out_pptx)
    cwd = os.getcwd(); os.chdir(unpacked)
    try:
        subprocess.run(['zip', '-X', '-q', out_pptx, '[Content_Types].xml'], check=True)
        subprocess.run(['zip', '-rX', '-q', out_pptx, '_rels', 'docProps', 'ppt'], check=True)
    finally:
        os.chdir(cwd)

def verify(unpacked):
    """Quick integrity check: dangling rels + unregistered parts. Returns issues list."""
    issues = []
    for rels in glob.glob(os.path.join(unpacked, 'ppt', '**', '_rels', '*.rels'), recursive=True):
        base = os.path.dirname(os.path.dirname(rels))
        for r in parse(rels).getElementsByTagName('Relationship'):
            if r.getAttribute('TargetMode') == 'External': continue
            tgt = os.path.normpath(os.path.join(base, r.getAttribute('Target')))
            if not os.path.exists(tgt): issues.append(f'dangling: {rels} -> {r.getAttribute("Target")}')
    ct = open(_ct_path(unpacked), encoding='utf-8').read()
    for f in glob.glob(os.path.join(unpacked, 'ppt', 'charts', '*.xml')) + glob.glob(os.path.join(unpacked, 'ppt', 'slides', 'slide*.xml')):
        pn = '/' + os.path.relpath(f, unpacked).replace(os.sep, '/')
        if pn not in ct: issues.append(f'unregistered: {pn}')
    return issues
