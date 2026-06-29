"""Turn a pptxgenjs deck into a THEME-ENGINE deck:
- write design tokens into theme1.xml (clrScheme + fontScheme)
- rewrite slide/master/layout colors from hardcoded srgb -> schemeClr references
So one theme change in PowerPoint recolors the whole deck."""
import sys, json, os, glob, re, subprocess, shutil
from defusedxml.minidom import parse

deck = sys.argv[1]; tokens = json.load(open(sys.argv[2])); out = sys.argv[3]
C = tokens["colors"]; F = tokens["fonts"]
work = deck + ".un"
shutil.rmtree(work, ignore_errors=True)
subprocess.run(["python","/mnt/skills/public/pptx/scripts/office/unpack.py", deck, work], check=True, capture_output=True)

# token hex -> theme scheme slot used in slides
HEX2SLOT = {
  C["primary"].upper():"accent1", C["secondary"].upper():"accent2", C["accent"].upper():"accent3",
  C["surface"].upper():"accent4", C["muted"].upper():"accent5", C["ink"].upper():"accent6",
}
# clrScheme definition (slots -> hex)
SCHEME = {"dk1":C["ink"],"lt1":C["bg"],"dk2":C["primary"],"lt2":C["surface"],
  "accent1":C["primary"],"accent2":C["secondary"],"accent3":C["accent"],
  "accent4":C["surface"],"accent5":C["muted"],"accent6":C["ink"],
  "hlink":C["primary"],"folHlink":C["accent"]}

# 1) theme1.xml: clrScheme + fontScheme
themePath = os.path.join(work,"ppt","theme","theme1.xml")
tx = open(themePath, encoding="utf-8").read()
def sysOrSrgb(slot,hex_):
    # dk1/lt1 are often sysClr in default theme; force srgbClr so our token shows
    return f'<a:{slot}><a:srgbClr val="{hex_.upper()}"/></a:{slot}>'
# replace each clrScheme slot's inner color
for slot,hexv in SCHEME.items():
    tx = re.sub(rf'<a:{slot}>.*?</a:{slot}>', sysOrSrgb(slot,hexv), tx, flags=re.S)
# fonts: majorFont/minorFont latin typeface
tx = re.sub(r'(<a:majorFont>\s*<a:latin typeface=")[^"]*(")', rf'\g<1>{F["head"]}\g<2>', tx)
tx = re.sub(r'(<a:minorFont>\s*<a:latin typeface=")[^"]*(")', rf'\g<1>{F["body"]}\g<2>', tx)
open(themePath,"w",encoding="utf-8").write(tx)

# 2) slides/masters/layouts: srgbClr token hex -> schemeClr slot
targets = glob.glob(os.path.join(work,"ppt","slides","*.xml")) + \
          glob.glob(os.path.join(work,"ppt","slideLayouts","*.xml")) + \
          glob.glob(os.path.join(work,"ppt","slideMasters","*.xml"))
for fp in targets:
    s = open(fp, encoding="utf-8").read()
    for hexv, slot in HEX2SLOT.items():
        s = re.sub(rf'<a:srgbClr val="{hexv}"\s*/>', f'<a:schemeClr val="{slot}"/>', s, flags=re.I)
        s = re.sub(rf'<a:srgbClr val="{hexv}">(.*?)</a:srgbClr>', rf'<a:schemeClr val="{slot}">\1</a:schemeClr>', s, flags=re.I|re.S)
    open(fp,"w",encoding="utf-8").write(s)

# 3) repack
subprocess.run(["python","/mnt/skills/public/pptx/scripts/office/pack.py", work, out], check=True, capture_output=True)
print("themed ->", out)
