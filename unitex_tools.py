# -*- coding: utf-8 -*-
""" 
Unitex utils
"""
import os
import re
from struct import pack, calcsize
import binascii


def create_unitex_env(conf, process_id, tokens_flatten, tokens, lang):
    """ 
    Creates Unitex Environment, minimum files needed to apply Unitex's methods.
    
    Files/Dirs needed:
    {process_id}_converted_snt Directory which contains all internal Unitex files.
    {process_id}_converted.snt File which contains converted text. It can be an empty file.
    {process_id}_converted_snt/text.cod Binary file which contains the text codification based on tokens.txt file.
    {process_id}_converted_snt/tokens.txt List of non-repeated tokens. The first value is the number of tokens
        expressed in 10 digits (zero left). The white-space token is added if it's not present.
    
    Keyword arguments:
    process_id -- Random unique identifier (used to create temporary files).
    tokens_flatten -- List of non-repeated tokens.
    tokens -- List of tokens which represent the text. 
    lang -- Language of the text.
    
    Returns:
    List of DELA dictionaries to apply.
    
    See also:
    pypeline/utils/unitex_utils -> unitex_text_cod()
    
    """
    #Check if tmpdir exists
    if not os.path.exists(conf['tmp_dir']):
        os.mkdir(conf['tmp_dir'])
        
    os.mkdir(os.path.join(conf['tmp_dir'], '%s_converted_snt'%process_id))
    unitex_text_cod(conf['tmp_dir'], process_id, tokens, tokens_flatten)
    converted = open(os.path.join(conf['tmp_dir'], '%s_converted.snt'%process_id), 'w')
    tokens_file = file(os.path.join(conf['tmp_dir'], '%s_converted_snt/tokens.txt'%process_id), 'w')
    output = "%010d\n"%len(tokens_flatten)
    for token in tokens_flatten:
        output += "%s\n"%token
    tokens_file.write(output.encode('utf-16'))
    tokens_file.close()
    print conf
    delas_conf = conf['delas_applied'][lang]
    delas = []
    for dela in delas_conf:
        dela_path = os.path.join(self.unitex_dir, 'Dela', dela)
        if os.path.exists(dela_path):
            delas.append(dela_path)
        else:
            self.logger.error("[ERROR] Dico %s doesn't exist."%dela_path)
    return delas
    
    
    
def detroy_unitex_env(conf, process_id):
    """
    Removes the temporal environment used by Unitex.
    
    Keyword arguments:
    process_id -- Random unique identifier (used to create temporary files).
    tmp_dir -- Temporary directory where Unitex files are located.
    
    """
    if os.path.exists(os.path.join(conf['tmp_dir'], '%s_converted_snt'%process_id)):
        dirList = os.listdir(os.path.join(conf['tmp_dir'], '%s_converted_snt'%process_id))
        for fname in dirList:
            os.remove(os.path.join(conf['tmp_dir'], '%s_converted_snt/%s'%(process_id, fname)))
        os.rmdir(os.path.join(conf['tmp_dir'], '%s_converted_snt'%process_id))
    if os.path.exists(os.path.join(conf['tmp_dir'], '%s_converted.snt'%process_id)):
        os.remove(os.path.join(conf['tmp_dir'], '%s_converted.snt'%process_id))
    if os.path.exists(os.path.join(conf['tmp_dir'], '%s_converted.csc'%process_id)):
        os.remove(os.path.join(conf['tmp_dir'], '%s_converted.csc'%process_id))
    if os.path.exists(os.path.join(conf['tmp_dir'], '%s_converted'%process_id)):
        os.remove(os.path.join(conf['tmp_dir'], '%s_converted'%process_id))
    if os.path.exists(os.path.join(conf['tmp_dir'], process_id)):
        os.remove(os.path.join(conf['tmp_dir'], process_id))
    if os.path.exists(os.path.join(conf['tmp_dir'], '%s_out'%process_id)):
        os.remove(os.path.join(conf['tmp_dir'], '%s_out'%process_id))
        
        
def unitex_text_cod(tmp_dir, process_id, tokens, tokens_txt):
    """
    Create a special file "text.cod" file using by Unitex process.
    This file contains the position of each token of file "tokens.txt"
    Each integer "i" means the position of the token in the file "tokens.txt" and must be packaged with
    4 bytes. The first token is #0. We use calcsize "Return the size of the struct corresponding to the 
    given format" for choose the appropiate representation.

    Keyword arguments: 
    tmp_dir -- Temporary directory where Unitex files are located.
    process_id -- Random unique identifier (used to create temporary files).
    tokens -- Result of the tokenization process apply to the text. 
        e.g.: tokens = ['este','es','un','texto','de','prueba','y','es','lo','que','es']
    tokens_txt -- List of non-repeated tokens.
        e.g.: tokens_txt = ['este','es','un','texto','de','prueba','y', 'lo','que',' ']
        
    See also:
    unitex_tokens()
    
    """
    #Create files and folders
    if not os.path.exists(os.path.join(tmp_dir, '%s_converted_snt'%process_id)):
        os.mkdir(os.path.join(tmp_dir, '%s_converted_snt'%process_id))
    text_code_file = file(os.path.join(tmp_dir, '%s_converted_snt/text.cod'%process_id),'wb')
    #Proccesing
    fmt = 'l'
    if calcsize(fmt) > 4:
        fmt = 'i'
    for token in tokens:
        if token != "":
            text_code_file.write('%s'%pack(fmt, tokens_txt.index(token)))
            text_code_file.write('%s'%pack(fmt, tokens_txt.index(' ')))
    text_code_file.close()
    
def unitex_tokens(tmp_dir, process_id, tokens):
    """
    Extracts the raw tokens from the text codification (text.cod (binary file))
    
    Keyword arguments: 
    tmp_dir -- Temporary directory where Unitex files are located.
    process_id -- Random unique identifier (used to create temporary files).
    tokens -- List of non-repeated tokens.
        e.g.: tokens_txt = ['este','es','un','texto','de','prueba','y', 'lo','que',' ']
    
    Returns:
    Result of the tokenization process apply to the text. 
        e.g.: tokens = ['este','es','un','texto','de','prueba','y','es','lo','que','es']
        
    See also:
    unitex_text_cod()
    
    """
    tokens_file = open(os.path.join(tmp_dir, '%s_converted_snt/text.cod'%process_id), "r")
    tokens_out = []
    hex_pos = tokens_file.read(4)
    while hex_pos != "":
        data = binascii.hexlify(hex_pos)
        hex_pos = tokens_file.read(4)
        tokens_out.append(tokens[int('%s%s%s%s'%(data[6:8], data[4:6], data[2:4], data[0:2]), 16)])
    return tokens_out

def generate_pos(tags, tokens, allowed_flex_codes, allowed_pos_tags):
    """
    Translates a list of Unitex POS tags into Pypeline POS format. 
    
    Input format: list of Unitex Dela format tags
    para,parar.V:1s:J2s
    para,.ADV:ms
    
    Output format: List/hash of POS tags
    pos: [{
        'form': 'para'
        'pos': [{
            'lemma': 'parar',
            'pos': 'V',
            'flex': ['1s', 'J2s'] 
        },
        {
            'lemma': 'para',
            'pos': 'ADV',
            'flex': ['ms'] 
        }
        ]
    }
    ]
    
    Keyword arguments:
    tags -- List (String) of Unitex POS tags.
    tokens -- Result of the tokenization process apply to the text. 
        e.g.: tokens = ['este','es','un','texto','de','prueba','y','es','lo','que','es']
    allowed_flex_codes -- Allowed flex codes on the POS (right side)
    allowed_pos_tags -- Allowed flex codes on the POS (left side)
    
    Returns:
    List of Part-Of-Speech tags.
    
        
    See also:
    tags_from_list_to_dict()
    generate_pos_tags()
    generate_dlf_dlc_from_pos()
    
    """
    try:
        while True:
            tags.remove('')
    except:
        pass
    tags = tags_from_list_to_dict(tags)
    pos = []
    index = 0
    while index < len(tokens):
        tag = []
        if tokens[index] in tags:
            tag = tags[tokens[index]]
        if tokens[index].lower() in tags:
            tag = tags[tokens[index].lower()]
        form = tokens[index]
        pos_tag = {}
        if len(tag) > 1:
            pos_tag = generate_pos_tags(tag[2], allowed_flex_codes, allowed_pos_tags)
            if tag[0] > 1:
                counter = 1
                while counter < tag[0]:
                    index += 1
                    counter += 1
                    form = "%s %s"%(form, tokens[index])
        if len(pos_tag) == 0:
            pos_tag = [{'lemma': form,
                        'pos': 'UNKNOWN',
                        'flex': []}]
        pos.append({'form' : form,
                    'pos' : pos_tag})
        index += 1
    return pos
    
def tags_from_list_to_dict(tags_list):
    """
    Translates the list of "string" Unitex POS tags into a dictionary.
    The indexes are the first word (lowercased).
    
    Input format: list of Unitex Dela format tags
    para,parar.V:1s:J2s
    para,.ADV:ms
    will smith,Will Smith.ACTOR:ms
    
    Output format: List/hash of POS tags
    {word}: [len(word), word, {lemma: [tags]}]
    {'para': [1, 'para', {'parar': ['V:1s:J2s'], 'para':['ADV:ms']}]}
    {'will': [2, 'will smith', {'Will Smith': ['ACTOR:ms']}]}
    
    Keyword arguments:
    tags -- List (String) of Unitex POS tags.
    
    Returns:
    List of Part-Of-Speech tags (dictionary format), word, lemma, length, pos and flex.
    
    """
    tags_dict = {}
    for tag in tags_list:
        tag_splitted = re.split('[.,]', tag, re.U)
        form_splitted = re.split(' ', tag_splitted[0], re.U)
        lemma = tag_splitted[1]
        if lemma == "":
            lemma =  tag_splitted[0]
        if tag_splitted[0] in tags_dict:
            if tags_dict[form_splitted[0]][0] == len(form_splitted):
                if lemma in tags_dict[form_splitted[0]][2]:
                    tags_dict[form_splitted[0]][2][lemma].append(tag_splitted[2])
                else:
                    tags_dict[form_splitted[0]][2][lemma] = [tag_splitted[2]]
            if tags_dict[form_splitted[0]][0] < len(form_splitted):
                tags_dict[form_splitted[0]] = [len(form_splitted), tag_splitted[0], {lemma: [tag_splitted[2]]}]
        else:
            tags_dict[form_splitted[0]] = [len(form_splitted), tag_splitted[0], {lemma: [tag_splitted[2]]}]
    return tags_dict
    
def generate_pos_tags(pos, allowed_flex_codes, allowed_pos_tags):
    """
    Translates the list of "string" Unitex POS tags into a dictionary.
    
    Input format: list of Unitex Dela format tags
    {lemma: [tags]}
    {'parar': ['V:1s:J2s'], 'para':['ADV:ms']}
    
    Output format: List/hash of POS tags
    [{
        'lemma': 'parar',
        'pos': 'V',
        'flex': ['1s', 'J2s'] 
    },
    {
        'lemma': 'para',
        'pos': 'ADV',
        'flex': ['ms'] 
    }]
    
    Keyword arguments:
    pos -- List (String) of Unitex POS tags.
    allowed_flex_codes -- Allowed flex codes on the POS (right side)
    allowed_pos_tags -- Allowed flex codes on the POS (left side)
    
    Returns:
    List of Part-Of-Speech tags (dictionary format), lemma, pos and flex.
    
    """
    tags_out = []
    tags = {}
    for lemma in pos:
        tag_options = pos[lemma]
        for tag in tag_options:
            flex = re.split(':', tag.replace("\r\n", ''), re.U)
            left_side = re.split('\+', flex.pop(0), re.U)
            flex_codes = []
            for f in flex:
                valid = True
                for index in range(len(f)):
                    if not f[index] in allowed_flex_codes:
                        valid = False
                        break
                if valid:
                    flex_codes.append(f)
            for label in left_side:
                if label in allowed_pos_tags:
                    if label in tags:
                        if lemma in tags[label]:
                            for f_code in flex_codes:
                                if not f_code in tags[label][lemma]:
                                    tags[label][lemma].append(f_code)
                        else:
                            tags[label][lemma] = flex_codes
                    else:
                        tags[label] = {}
                        tags[label][lemma] = flex_codes
    for label in tags:
        for lemma in tags[label]:
            tags_out.append({'pos': label, 
                             'lemma': lemma,
                              'flex': tags[label][lemma]})
    return tags_out
    
def generate_dlf_dlc_from_pos(tmp_dir, process_id, pos):
    """
    Creates Unitex tags temporary files: dlf (simple tags),
    dlc (compound tags) and err (not found). 
    
    Keyword arguments:
    tmp_dir -- Temporary directory where Unitex files are located.
    process_id -- Random unique identifier (used to create temporary files).
    pos -- List (String) of Unitex POS tags.
    
    Returns:
    List of Part-Of-Speech tags in list(String) Unitex format.
    
    See also:
    pos_flatten()
    generate_pos()
    
    """
    dlcs, dlfs, errs = pos_flatten(pos)
    dlc = open(os.path.join(tmp_dir, '%s_converted_snt/dlc'%process_id), 'w')
    output = ""
    while len(dlcs) > 0:
        output += "%s\n"%dlcs.pop(0)
    dlc.write(output.encode('utf-16'))
    dlc.close()
    dlf = open(os.path.join(tmp_dir, '%s_converted_snt/dlf'%process_id), 'w')
    output = ""
    while len(dlfs) > 0:
        output += "%s\n"%dlfs.pop(0)
    dlf.write(output.encode('utf-16'))
    err = open(os.path.join(tmp_dir, '%s_converted_snt/err'%process_id), 'w')
    output = ""
    while len(errs) > 0:
        output += "%s\n"%errs.pop(0)
    err.write(output.encode('utf-16'))
    err.close()
    
def pos_flatten(pos):
    """
    Translates a list of Pypeline POS format into Unitex POS tags. 
    
    Input format: List/hash of POS tags
    Format:
    pos: [{
        'form': 'para'
        'pos': [{
            'lemma': 'parar',
            'pos': 'V',
            'flex': ['1s', 'J2s'] 
        },
        {
            'lemma': 'para',
            'pos': 'ADV',
            'flex': ['ms'] 
        }
        ]
    }
    ]
    
    Output format: list of Unitex Dela format tags
    para,parar.V:1s:J2s
    para,.ADV:ms
    
    Keyword arguments:
    pos -- List (String) of Unitex POS tags.
    
    Returns:
    List of Part-Of-Speech tags in list(String) Unitex format.
    
    See also:
    generate_dlf_dlc_from_pos()
    
    """
    dlfs = []
    dlcs = []
    errs = []
    for token in pos:
        form = token['form']
        for tag in token['pos']:
            pos_tag = tag['pos']
            if pos_tag == "UNKNOWN":
                errs.append(form)
            else:
                if len(tag['flex']) > 0:
                    pos_tag = '%s:%s'%(pos_tag, ':'.join(tag['flex']))
                text = "%s,%s.%s"%(form, tag['lemma'], pos_tag)
                #print text
                if len(re.split('\s', form, re.U)) > 1:
                    dlcs.append(text)
                else:
                    dlfs.append(text)
    print dlcs
    print dlfs
    print errs
    return dlcs, dlfs, errs
