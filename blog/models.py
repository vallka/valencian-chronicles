import re
import requests

from bs4 import BeautifulSoup

from django.db import models
from django.utils.text import slugify
#from django.utils.translation import ugettext_lazy as _
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.urls import reverse
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify


def custom_slugify(s):
    replacements = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e',
        'ё': 'e', 'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k',
        'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r',
        'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'ts',
        'ч': 'ch', 'ш': 'sh', 'щ': 'shch', 'ъ': '', 'ы': 'y', 'ь': '',
        'э': 'e', 'ю': 'yu', 'я': 'ya',
    }

    def replace_char(c):
        return replacements.get(c.group(), '')

    s = re.sub('[а-яё]', replace_char, s.lower())
    s = re.sub(r'\W+', '-', s)
    s = s.strip('-')
    return s

# Create your models here.
class Category(models.Model):
    class Meta:
        ordering = ['slug']

    category = models.CharField(_("Category"), blank=True, max_length=100, unique=True)
    slug = models.SlugField(_("Slug"), unique=True, max_length=100, blank=True, null=False)
    is_default = models.BooleanField(_("Default Category"),default=False)

    def __str__(self):
        return str(self.slug) + ' -- ' + str(self.category)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = custom_slugify(self.category)
            
        super().save(*args, **kwargs)

class Post(models.Model):
    class Meta:
        ordering = ['-id']

    title = models.CharField(_("Title"), max_length=100, unique=True)
    slug = models.SlugField(_("Slug"), unique=True, max_length=100, blank=True, null=False)

    blog = models.BooleanField(_("Publish to blog"),default=False)
    blog_start_dt = models.DateTimeField(_("Publish Date/Time"), blank=True, null=True)
    email = models.BooleanField(_("Send as newsletter to UK customers"),default=False)
    email_send_dt = models.DateTimeField(_("Send Date/Time"), blank=True, null=True)

    class EmailStatus(models.IntegerChoices):
        NONE = 0
        SENDING = 1
        SENT = 2

    email_status = models.IntegerField(default=EmailStatus.NONE,choices=EmailStatus.choices)

    category = models.ManyToManyField(Category, )

    title_color = models.CharField(_("Title Color"),max_length=20, blank=True, null=False, default='#232323')
    title_bgcolor = models.CharField(_("Title Bg Color"),max_length=20, blank=True, null=False, default='#eeeeee')

    text = MarkdownxField(_("Text"), blank=True, null=False)

    created_dt = models.DateTimeField(_("Created Date/Time"), auto_now_add=True, null=True)
    updated_dt = models.DateTimeField(_("Updated Date/Time"), auto_now=True, null=True)

    description  = models.TextField(_("Meta Description"), blank=True, null=False, default='')
    keywords  = models.TextField(_("Meta Keywords"), blank=True, null=False, default='')
    json_ld  = models.TextField(_("script ld+json"), blank=True, null=False, default='')


    @property
    def formatted_markdown(self):
        return markdownify(self.text)

    def __str__(self):
        return str(self.id) + ':'+ str(self.slug)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = custom_slugify(self.title)

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return '/' + str(self.slug)        

    @property
    def first_image(self):
        img = re.search(r'\!\[\]\(([^)]+)\)',self.text)
        if img and img.group(1):
            return img.group(1)
        
        img = re.search(r'<img[^>]+src="(.*?)"',self.text)
        if img and img.group(1):
            return img.group(1)

        return None

    @property
    def first_p(self):
        text = re.sub('~~([^~]+)~~',r'<s>\1</s>',self.text) # not in standard extensions
        p = markdownify(text)
        
        p1 = ''
        n = 0
        while not p1 and p and n<=10:
            n += 1
            p = re.sub(r'^.*?<p>\s*','',p,flags=re.S)
            p1 = re.sub('</p>.*$','',p,flags=re.S)
            p1 = re.sub('<.*?>','',p1)
            p1 = p1.strip()
            if p1 and len(p1)>150: 
                return p1


        p2 = ''
        n = 0
        while not p2 and p and n<=10:
            n += 1
            p = re.sub(r'^.*?<p>\s*','',p,flags=re.S)
            p2 = re.sub('</p>.*$','',p,flags=re.S)
            p2 = re.sub('<.*?>','',p2)
            p2 = p2.strip()
            if p1 and p2: 
                return f'{p1}<br><br>{p2}'

        return p1 + ' ' + p2

    @property
    def text_imageazed(self):
        text = self.text
        imgsm = re.search(r'(\s*\!\[\]\(([^)]+)\))+\s*$',self.text)
        if imgsm:
            imgs = imgsm.group(0).strip().split('![]')
            #print (imgsm,imgsm.start(),imgs)
            imgdiv = '\n<div id="gallery">\n'
            for img in imgs:
                if img:
                    img = img.strip('() \n\r')
                    #print(img)
                    imgdiv += f'<a href="#"><img src="{img}" data-image="{img}" alt="" style="display: none;"></a>\n'

            imgdiv += '</div>'
            text = text[0:imgsm.start()] + imgdiv

        return text




