from PIL import Image, ImageDraw, ImageFont
import numpy as np
W,H=1200,630
y,x=np.mgrid[0:H,0:W]
d=np.clip(np.sqrt((x-600)**2+((y-60)*1.3)**2)/760,0,1)
c0=np.array([42,36,86]);c1=np.array([18,18,38])
img=Image.fromarray((c0+(c1-c0)*d[...,None]).astype('uint8'),'RGB')
dr=ImageDraw.Draw(img)
dr.rectangle([20,20,W-21,H-21],outline=(124,92,255),width=1)
tf=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',72)
sf=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',34)
ef=ImageFont.truetype('/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf',109)
em=Image.new('RGBA',(140,140),(0,0,0,0))
ImageDraw.Draw(em).text((0,0),'\U0001F6E0',font=ef,embedded_color=True)
em=em.crop(em.getbbox()).resize((76,76),Image.LANCZOS)
t='ToolDrop';tw=dr.textlength(t,font=tf);gap=22
total=76+gap+tw;x0=(W-total)/2
ty=255
img.paste(em,(int(x0),ty+6),em)
dr.text((x0+76+gap,ty),t,font=tf,fill=(232,234,246))
s='AI tools for vibe coders and indie game devs'
dr.text(((W-dr.textlength(s,font=sf))/2,355),s,font=sf,fill=(34,211,238))
img.save('static/img/share.png',optimize=True)
