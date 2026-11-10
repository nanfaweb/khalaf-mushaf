import fitz, os, re, math, json
from fontTools.cffLib import CFFFontSet
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import cairosvg

pdf='/mnt/data/المصحف_برواية_خلف_عن_حمزة.pdf'
doc=fitz.open(pdf)
fontmap={}
for page in doc:
    for f in page.get_fonts(full=True): fontmap[f[0]]=f
# extract font bytes and font dictionary encoding differences
for xref,f in fontmap.items():
    name, ext, typ, buf=doc.extract_font(xref)
    open(f'/mnt/data/font_{xref}.{ext}','wb').write(buf)
    fontobj=doc.xref_object(xref,compressed=False)
    m=re.search(r'/Encoding\s+(\d+)\s+0\s+R',fontobj)
    code_to_glyph={}
    if m:
        encobj=doc.xref_object(int(m.group(1)),compressed=False)
        dm=re.search(r'/Differences\s*\[(.*?)\]',encobj,re.S)
        if dm:
            toks=re.findall(r'\d+|/[^\s\[\]]+',dm.group(1))
            cur=None
            for tok in toks:
                if tok.startswith('/'):
                    if cur is not None:
                        code_to_glyph[cur]=tok[1:]; cur+=1
                else: cur=int(tok)
    cff=CFFFontSet(); cff.decompile(BytesIO(buf),None)
    top=cff.topDictIndex[0]
    # use cmap code mapping / differences matched to original CFF glyph name
    pairs=[]
    for code,glyph in code_to_glyph.items():
        if glyph in top.charset:
            pairs.append((code,glyph,top.CharStrings[glyph]))
    fontmap[xref]={'file':f,'shortname':name.split('+')[-1], 'cff':cff,'top':top,'pairs':pairs,'fullinfo':f}

# render glyph grid via SVG path. Group fonts into a single labeled sheet each.
for xref,fi in fontmap.items():
    pairs=fi['pairs']
    if not pairs: continue
    cols=8; cellw=180; cellh=170
    rows=math.ceil(len(pairs)/cols)
    out=Image.new('RGB',(cols*cellw,rows*cellh),'white')
    draw=ImageDraw.Draw(out)
    labelfont=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',16)
    for idx,(code,glyph,cs) in enumerate(sorted(pairs)):
        r,c=divmod(idx,cols)
        x=c*cellw; y=r*cellh
        pen=SVGPathPen(None)
        try:
            cs.draw(pen)
            path=pen.getCommands()
            bp=BoundsPen(None); cs.draw(bp)
            if bp.bounds:
                x0,y0,x1,y1=bp.bounds
                bw=max(x1-x0,1); bh=max(y1-y0,1)
                # fit in 130x105
                scale=min(130/bw,105/bh)
                # map bounds to a local viewport; svg y inverted
                tx=25-x0*scale
                ty=120+y0*scale
                # path uses source coordinates; translation after y flip
                svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="{cellw}" height="{cellh}" viewBox="0 0 {cellw} {cellh}"><g transform="translate({tx:.3f},{ty:.3f}) scale({scale:.5f},{-scale:.5f})"><path d="{path}" fill="black"/></g></svg>'''
                png=cairosvg.svg2png(bytestring=svg.encode(),output_width=cellw,output_height=cellh)
                import io
                glyphimg=Image.open(io.BytesIO(png)).convert('RGBA')
                out.paste(glyphimg,(x,y),glyphimg)
        except Exception as e:
            pass
        draw.text((x+6,y+5),f'{code:02X}  {glyph}',fill='red',font=labelfont)
        draw.rectangle((x,y,x+cellw-1,y+cellh-1),outline=(180,180,180),width=1)
    out.save(f'/mnt/data/glyph_atlas_{xref}.png')
    print(xref,fi['shortname'],'codes',len(pairs),'glyphs',len(fi['top'].charset), 'atlas',out.size)
print('Fonts:')
for xref,fi in fontmap.items():
 if isinstance(fi,dict): print(xref,fi['shortname'],len(fi['pairs']), fi['top'].charset[:10])
