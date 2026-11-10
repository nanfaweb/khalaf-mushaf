import fitz, re, csv, json, collections, os, zipfile, shutil
PDF='/mnt/data/المصحف_برواية_خلف_عن_حمزة.pdf'
OUT='/mnt/data/khalaf_recovery_package'
os.makedirs(OUT,exist_ok=True)
doc=fitz.open(PDF)
# Find actual page font resources and differences code->glyph
fonts={}
for pg in doc:
    for row in pg.get_fonts(full=True):
        xref=row[0]
        if xref in fonts: continue
        name, ext, typ, buf=doc.extract_font(xref)
        obj=doc.xref_object(xref,compressed=False)
        m=re.search(r'/Encoding\s+(\d+)\s+0\s+R',obj)
        cmap={}
        enc_ref=None
        if m:
            enc_ref=int(m.group(1)); encobj=doc.xref_object(enc_ref,compressed=False)
            dm=re.search(r'/Differences\s*\[(.*?)\]',encobj,re.S)
            if dm:
                toks=re.findall(r'\d+|/[^\s\[\]]+',dm.group(1)); cur=None
                for tok in toks:
                    if tok.startswith('/'):
                        if cur is not None:
                            cmap[cur]=tok[1:]; cur+=1
                    else: cur=int(tok)
        fonts[xref]={'name':name,'short':name.split('+')[-1], 'ext':ext,'type':typ,'bytes':len(buf),'encoding_ref':enc_ref,'code_to_glyph':cmap, 'pdf_obj':obj}
# count code usage by font via text spans
counts=collections.Counter(); pages=collections.defaultdict(set)
for pno,pg in enumerate(doc,1):
    td=pg.get_text('dict')
    for b in td['blocks']:
        if b.get('type')!=0: continue
        for line in b['lines']:
            for span in line['spans']:
                fontname=span['font']
                s=span['text']
                # span char codes emerge as Latin1; the ord gives original byte code for these custom fonts
                for ch in s:
                    c=ord(ch)
                    counts[(fontname,c)]+=1
                    pages[(fontname,c)].add(pno)
# write csv
with open(OUT+'/font_code_inventory.csv','w',newline='',encoding='utf-8') as f:
    w=csv.writer(f); w.writerow(['font','pdf_code_hex','pdf_code_dec','glyph_name_from_Differences','occurrences','pages_used'])
    for (fn,c),n in sorted(counts.items(),key=lambda z:(z[0][0],z[0][1])):
        xref=next((x for x,v in fonts.items() if v['short']==fn),None)
        gl=fonts[xref]['code_to_glyph'].get(c,'') if xref else ''
        w.writerow([fn,f'0x{c:02X}',c,gl,n,len(pages[(fn,c)])])
# font summary
summary=[]
for xref,v in fonts.items():
    summary.append({'xref':xref,'font':v['short'],'postscript_name':v['name'],'type':v['type'],'embedded_bytes':v['bytes'],'pdf_encoding_ref':v['encoding_ref'],'mapped_codes_in_pdf':len(v['code_to_glyph']),'observed_code_count':sum(1 for (fn,c) in counts if fn==v['short']),'observed_glyph_count':sum(1 for (fn,c),n in counts.items() if fn==v['short'] and v['code_to_glyph'].get(c)),'total_occurrences':sum(n for (fn,c),n in counts.items() if fn==v['short'])})
with open(OUT+'/font_summary.json','w',encoding='utf-8') as f: json.dump(summary,f,ensure_ascii=False,indent=2)
# extract raw CFF subsets as-is
for xref,v in fonts.items():
    name,ext,typ,buf=doc.extract_font(xref)
    if buf: open(f'{OUT}/font_{xref}_{v["short"]}.{ext}','wb').write(buf)
# copy glyph atlases, and create page samples / OCR if present
for fn in os.listdir('/mnt/data'):
    if fn.startswith('glyph_atlas_') and fn.endswith('.png'):
        shutil.copy2('/mnt/data/'+fn,OUT+'/'+fn)
for fn in ['khalaf_page_2.png','khalaf_page_3.png','khalaf_page_604.png']:
    if os.path.exists('/mnt/data/'+fn): shutil.copy2('/mnt/data/'+fn,OUT+'/'+fn)
if os.path.exists('/mnt/data/ocr_hi/page3.png'): shutil.copy2('/mnt/data/ocr_hi/page3.png',OUT+'/page3_600dpi.png')
# create README
readme='''# Khalaf an Hamzah PDF encoding investigation\n\nThis is an extraction inventory and glyph-reference package, not a completed Unicode transcription.\n\n## Findings\n- The supplied PDF has 604 pages and is vector/text based rather than image-only.\n- The custom Arabic text layer extracts to low-byte/control characters because the embedded Type 1C/CFF fonts do not provide usable ToUnicode mappings.\n- The content uses multiple font subsets. The PDF Encoding Differences arrays map byte codes to CFF glyph names (for example `g197`), but that mapping only identifies the glyph, not the Unicode character represented.\n- The visible writing is layered: HQPB1/HQPB2/HQPB3 contain many base letter shapes; HQPB4/HQPB5 contain many small overlay/mark glyphs. Therefore there is not one universal byte-to-letter substitution.\n- `font_code_inventory.csv` lists each observed font/code pair, CFF glyph name, frequency, and number of pages on which it occurs.\n- `font_summary.json` summarizes embedded font subsets. The glyph atlases are visual references generated from the embedded CFF charstrings.\n\n## What remains to complete a decoder\n1. Establish the mapping from each relevant glyph (and overlay) to Arabic Unicode or a Unicode sequence.\n2. Reconstruct text order and combining-mark attachment from glyph positions / text-show operations.\n3. Validate against an authoritative Khalaf an Hamzah text, not just a Hafs Quran corpus.\n4. Rebuild the PDF text layer or produce an extracted UTF-8 transcript, then audit verse-by-verse.\n\n## OCR test\nA 600-DPI render of page 3 was tested with Tesseract Arabic OCR. It recovers much of the base wording but not all diacritics or special Qur'anic/recitation annotations. Treat OCR as a draft/validation signal, not an authoritative transcript.\n'''
open(OUT+'/README.md','w',encoding='utf-8').write(readme)
# Zip
zip_path='/mnt/data/khalaf_recovery_package.zip'
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as z:
    for fn in os.listdir(OUT): z.write(OUT+'/'+fn,arcname=fn)
print('pages',len(doc),'font subsets',len(fonts),'unique font/code pairs',len(counts),'total text char observations',sum(counts.values()))
for s in summary: print(s)
print('zip',zip_path,os.path.getsize(zip_path))
