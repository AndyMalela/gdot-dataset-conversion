"""Template look: level-1 bullet dots in the sidebar red (pptxgenjs colours bullets like the text)."""
import re, sys, zipfile, shutil
src = sys.argv[1]; tmp = src + ".tmp"
zin = zipfile.ZipFile(src); zout = zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED)
for item in zin.infolist():
    data = zin.read(item.filename)
    if item.filename.startswith("ppt/slides/slide") and item.filename.endswith(".xml"):
        x = data.decode()
        x = x.replace('<a:buSzPct val="100000"/><a:buChar char="&#x25CF;"/>',
                      '<a:buClr><a:srgbClr val="A52026"/></a:buClr><a:buSzPct val="100000"/><a:buChar char="&#x25CF;"/>')
        data = x.encode()
    if not item.filename.endswith("/"):
        zout.writestr(item, data)
zout.close(); shutil.move(tmp, src); print("recoloured", src)
