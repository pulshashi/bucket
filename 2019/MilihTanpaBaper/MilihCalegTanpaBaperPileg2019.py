#!/usr/bin/env python
# coding: utf-8

# Author: Iq Reviessay Pulshashi <pulshashi@ideas.web.id>
# Crawler data calon legistatif + Local cache

# ## Konfigurasi Mining

# In[1]:


# Lihat di https://pemilu.info/caleg-dpr-ri-2019/
link = 'https://pemilu.info/calon-legislatif-dpr-ri-daerah-pemilihan-dki-jakarta-ii/'
#link = 'https://pemilu.info/calon-legislatif-dpr-ri-daerah-pemilihan-jawa-timur-i/'
baseDir = 'pileg2019'


# ### Mengunduh halaman utama

# In[2]:


import hashlib, os, urllib
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

def getCachedUri(url, path, tag, ext):
    urlHash = hashlib.md5(url.encode('utf-8')).hexdigest()
    cacheFile = baseDir + '/' + tag + '-' + urlHash + '.' + ext
    if not (path == ''):
        cacheFile = baseDir + '/' + path + '/' + tag + '-' + urlHash + '.' + ext
        try:
            os.mkdir(baseDir + '/' + path)
        except:
            print()
    if not (os.path.isfile(cacheFile)):
        try:
            urllib.request.urlretrieve(url, cacheFile)
        except:
            print()
    return cacheFile

def getCachedHtml(url, path, tag):
    cacheFile = getCachedUri(url, path, tag, 'html')
    if not (os.path.isfile(cacheFile)):
        return ''
    try:
        fr = open(cacheFile, 'r')
        html = str(fr.read())
        fr.close()
    except:
        fr.close()
        return ''
    return html

urlHash = hashlib.md5(link.encode('utf-8')).hexdigest()
html = getCachedHtml(link, '', 'base')
#print(html)


# ### Mencari data caleg

# In[3]:


def getSubHtml(html, startTag, endTag):
    hs = html.find(startTag)
    return html[hs + len(startTag):html.find(endTag, hs)]

table = getSubHtml(html, '"listCalon_info">', '</table>')
tbody = getSubHtml(table, '<tbody id="rowinfo">', '</tbody>')
rows = tbody.split('</tr>')
csvCacheFile = baseDir + '/base-' + urlHash + '.csv'
csv = 'id|parpol|no_urut|fotoUrl|nama|jk|domisili|detailUrl\n'
rcalegs = []
for ri, row in enumerate(rows):
    lines = row.split("\n")
    data = ['']
    for li, line in enumerate(lines):
        if (line[0:3] == '<td'):
            datum = line[line.find('>') + 1:-5]
            if (datum[0:4] == '<img'):
                se = datum.find('src="')
                datum = datum[se + 5:datum.find('"', se + 5)]
            if (datum[0:2] == '<a'):
                se = datum.find('href="')
                datum = datum[se + 6:datum.find('"', se + 6)]
                ids = datum.split('/')
                id = ids[len(ids) - 1]
                data[0] = id
            data.append(datum)
    csv = csv + '|'.join(data) + '\n'
    rcalegs.append(data)
file = open(csvCacheFile, "w+")
file.write(csv)
file.close()
#print(csv)
lrcalegs = len(rcalegs)
print(str(lrcalegs) + ' Data Caleg di Proses')


# In[4]:


### Proses Detil Data Caleg


# In[5]:


from IPython.display import clear_output, display, HTML
import time, os

calegBaseUri = 'https://infopemilu.kpu.go.id/pileg2019/pencalonan/calon/'
calegDocBaseUri = 'https://silonpemilu.kpu.go.id/publik/calon/'
cols = {}
calegs = []
# Caching data caleg
for ci, rcaleg in enumerate(rcalegs):
    id = rcaleg[0]
    sid = 'caleg-' + str(id)
    clear_output(wait=True)
    print('Proses data caleg ... ' + str(ci + 1) + '/' + str(lrcalegs) + ' (' + id + ')')
    chtml = getCachedHtml(calegBaseUri + id, sid, sid)
    getCachedUri(calegDocBaseUri + id + '/13', sid, sid + '-ktp', 'pdf')
    getCachedUri(calegDocBaseUri + id + '/19', sid, sid + '-foto', 'jpg')     
    html = getSubHtml(chtml, '<div class="ibox-content" style="background-color: #ffffcc;">', '<h2 class="page-header">')
    rows = html.split('<div class="row')
    if len(rcaleg) < 7:
        break
    data = {
        'Id': rcaleg[0],
        'Partai': rcaleg[1],
        'No Urut': rcaleg[2],
        'Link Foto': rcaleg[3],
        'Nama Lengkap': rcaleg[4],
        'Jenis Kelamin': rcaleg[5],
        'Tempat Lahir': rcaleg[6],
        'Link Detil': rcaleg[7],
    }
    
    for ri, row in enumerate(rows):
        ct = getSubHtml(row, '<strong>', '</strong>')
        cv = getSubHtml(row, '<div class="col-sm-9">', '</div>').replace('\n', ' ')
        data[ct] = cv
    for di, datum in data.items():
        cols[di] = 1
    calegs.append(data)
    time.sleep(0.01)
csvCacheFile = baseDir + '/base-' + urlHash + '-result.csv'
file = open(csvCacheFile, "w+")
csv = '|'.join(cols.keys()) + '\n'
file.write(csv)
for ci, caleg in enumerate(calegs):
    row = []
    for k, v in cols.items():
        c = ''
        if k in caleg.keys():
            c = caleg[k]
        row.append(c)
    csv = '|'.join(row) + '\n'
    file.write(csv)
file.close()
display(HTML('Hasil bisa dilihat di: <a target="_blank" href="files/' + csvCacheFile + '?download=1">' + csvCacheFile + '</a>'))

