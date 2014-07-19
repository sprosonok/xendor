# -*- coding: utf-8 -*-
import os
import urllib2

from PIL import Image, ImageDraw
from django.conf import settings

#Смещение по y для водяных знаков
WATERMARK_X_SHIFT = 20
#Смещение по y для водяных знаков
WATERMARK_Y_SHIFT = 20


def image_process(image, width, height, opt = []):
    """ Xendor thumbnail: Процессинг для картинок """
    
    for effect in opt:
        if effect == 'resize':
            image = image.resize((width, height), Image.ANTIALIAS)
        
        elif effect == 'fix':
            w,h = image.size
            
            scale = 1.0 * width / height * h / w
            
            if scale>1:
                image = image.crop([0, 0, w-1, int(h/scale)-1])
            else:
                image = image.crop([int(1.0*w/2-1.0*w*scale/2), 0, int(1.0*w/2+1.0*w*scale/2), h-1])
            
        elif 'blank' in effect:
            opt = effect.split(':')
            if len(opt) == 4:
                blank = Image.new('RGBA', [width, height], (int(opt[1]), int(opt[2]), int(opt[3]), 0))
            else:
                blank = Image.new('RGBA', [width, height], (255, 255, 255, 0))
            
            image.thumbnail((width, height), Image.ANTIALIAS)
            w,h = image.size
            
            blank.paste(image, ((width-w)/2, (height-h)/2, w + (width-w)/2, h + (height-h)/2))
            
            image = blank
        
        elif effect == 'wtm':
            try:
                watermark = Image.open(os.path.join(settings.MEDIA_ROOT, 'watermark/watermark.png')) #open the filter
    
                watermark.thumbnail([image.size[0]/2, image.size[1]/2], Image.ANTIALIAS)
    
                image.paste(watermark,(
                    image.size[0]-watermark.size[0] - WATERMARK_X_SHIFT,
                    image.size[1]-watermark.size[1] - WATERMARK_Y_SHIFT), watermark)
    
            except IOError:
                pass

        elif effect == 'wtm-center':
            try:
                watermark = Image.open(os.path.join(settings.MEDIA_ROOT, 'watermark/watermark.png')) #open the filter
    
                watermark.thumbnail([image.size[0]/2, image.size[1]/2], Image.ANTIALIAS)
    
                image.paste(watermark,(
                    image.size[0]-watermark.size[0] - (image.size[0]-watermark.size[0])/2,
                    image.size[1]-watermark.size[1] - (image.size[1]-watermark.size[1])/2), watermark)
    
            except IOError:
                pass
        
    # Всегда подгоняем
    image.thumbnail((width, height), Image.ANTIALIAS) 
    return image


def thumbnail(file, size='200;200'):
    """ 
      fix, blank, wtm
    """
    
    correct_suff = ['fix', 'blank', 'wtm', 'resize']
    
    # defining the size
    width = int(size.split(';')[0])
    height = int(size.split(';')[1])
    opt = size.split(';')[2:]
    size = unicode(width)+'x'+unicode(height)
    
    suff = ''
    
    for su in opt:
        if su in correct_suff: suff += unicode(su)
    
    # defining the filename and the miniature filename
    try:
        basename, format = file.rsplit('.', 1)
    except:
        basename, format = 'no_img', 'jpg'
    
    if opt:
        miniature = basename + '_thm_'+unicode(suff)+'_' + size + '.' +  format
    else:
        miniature = basename + '_thm_' + size + '.' +  format
        
    miniature_filename = os.path.join(settings.MEDIA_ROOT, miniature)
    miniature_url = os.path.join(settings.MEDIA_URL, miniature)
    
    if not os.path.exists(miniature_filename):
        try:
            filename = os.path.join(settings.MEDIA_ROOT, file)
            image = Image.open(filename)
            
            image = image_process(image, width, height, opt)
            
            image.save(miniature_filename, image.format)
        except: #IOError
            filename = os.path.join(settings.MEDIA_ROOT, settings.NO_IMG_PATH)
            basename, format = settings.NO_IMG_PATH.rsplit('.', 1)
            
            if opt:
                opt = [el for el in opt if el != 'wtm']
                miniature = basename + '_thm_' + unicode(suff) + '_' + size + '.' +  format
            else:
                miniature = basename + '_thm_' + size + '.' + format
                
            miniature_filename = os.path.join(settings.MEDIA_ROOT, miniature)
            miniature_url = os.path.join(settings.MEDIA_URL, miniature)
            
            if not os.path.exists(miniature_filename):
                try:            
                    image = Image.open(filename)
                except IOError:
                    if settings.DEBUG:
                        raise IOError(u"Сan't find stuff file (check NO_IMG_PATH in settings.py)")
                    return miniature_url
                
                opt = ['blank',]
                
                image = image_process(image, width, height, opt)
                
                image.save(miniature_filename, image.format)
                
            return miniature_url
        
    return miniature_url

def xendor_dummy(line_size, size='200;200'):
    width = int(size.split(';')[0])
    height = int(size.split(';')[1])
    
    try:
        color = size.split(';')[2]
    except:
        color = '#000000'
    
    sizex = unicode(width)+'x'+unicode(height)
    
    try:
        background = size.split(';')[3]
        miniature = 'xdummy_' + line_size + '_ ' + color.replace('#', '') + '_ ' + background.replace('#', '') + '_ ' + sizex + '.png'
    except:
        background = (255,255,255,0)
        miniature = 'xdummy_' + line_size + '_ ' + color.replace('#', '') + '_ ' + sizex + '.png'
    
    miniature_filename = os.path.join(settings.MEDIA_ROOT, miniature)
    miniature_url = os.path.join(settings.MEDIA_URL, miniature)
    
    if not os.path.exists(miniature_filename):
        im = Image.new("RGBA", (width, height), background)
        draw = ImageDraw.Draw(im)
        #draw.ellipse((10,10,width-10,height-10), fill="red", outline="silver")
        draw.line((0, 0, width, height), width=int(line_size), fill = color)
        draw.line((width, 0, 0, height), width=int(line_size), fill = color)
        
        draw.line((0, 0, 0, height-1), width=int(line_size), fill = color)
        draw.line((0, 0, width-1, 0), width=int(line_size), fill = color)
        draw.line((width-1, 0, width-1,  height-1), width=int(line_size), fill = color)
        draw.line((0, height-1, width-1,  height-1), width=int(line_size), fill = color)
        
        del draw
        
        im.save(miniature_filename, im.format)
        
    return miniature_url

def download(url, file_name, proxy_addres=None,proxy_user=None,proxy_pass=None):
    if url[:7]!='http://':
                url='http://'+url    
    if proxy_addres!=None:
        proxy= urllib2.ProxyHandler({"http" : "http://"+proxy_addres})
        proxy_auth_handler = urllib2.ProxyBasicAuthHandler(DumbProxyPasswordMgr ())
        proxy_auth_handler.add_password(None, None, proxy_user, proxy_pass)
        opener = urllib2.build_opener(proxy,proxy_auth_handler)
        urllib2.install_opener(opener)
        src = urllib2.urlopen(url)
    else:
        src = urllib2.urlopen(url)
    data = src.read()
    dst = open(file_name,"wb"); 
    dst.write(data)


def internet_fix_thumbnail(file, size='200x200'):   
    filename = ''
    
    for item in file.rsplit('/', 3)[1:]:
        filename = filename + item
     
    file_url = os.path.join('uploads/internet/', filename)   
    filename = os.path.join(settings.MEDIA_ROOT, 'uploads/internet/', filename)
    
    if not os.path.exists(filename):
        download(file, filename)
    
    return fix_thumbnail(file_url, size)


def internet_thumbnail(file, size='200x200'):   
    filename = ''
    
    for item in file.rsplit('/', 3)[1:]:
        filename = filename + item
     
    file_url = os.path.join('uploads/internet/', filename)   
    filename = os.path.join(settings.MEDIA_ROOT, 'uploads/internet/', filename)
    
    if not os.path.exists(filename):
        download(file, filename)
    
    return file_url

