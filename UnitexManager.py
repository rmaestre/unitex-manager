# -*- coding: utf-8 -*-
""" 
Unitex utils

"""
from unitex_tools import *
import yaml
import pyunitex
import uuid

class UniteManager():
    
    def __init__(self):
        # Create a Unitex binding object
        self.manager = pyunitex.Unitex()
        
    def tokenizer(self, input_str, lang):
        """
        Whole process to extract tokens from an input text.
        
        Returns:
        List of tokens
        """
        # Load tokenizer configuration
        f = open('conf/UnitexTokenizer.yml')
        self.conf = yaml.load(f)
        f.close()
        # Assertions
        assert(lang in self.conf['supported_langs'])
        # Create process id
        self.process_id = str(uuid.uuid1())
        # Destroy environment if exists and creat dir
        detroy_unitex_env(self.conf, self.process_id)
        # Create file with input text
        input_txt = file(os.path.join(self.conf['tmp_dir'], self.process_id),'w')
        input_txt.write(input_str.encode('utf-8'))
        input_txt.close()
        # Create environment 
        os.mkdir(os.path.join(self.conf['tmp_dir'], '%s_converted_snt' % self.process_id))
        # Unitex commands execution
        self.manager.Convert('-s','UTF8', os.path.join(self.conf['tmp_dir'], self.process_id),'-o', os.path.join(self.conf['tmp_dir'], '%s_converted' % self.process_id))
        self.manager.Normalize(os.path.join(self.conf['tmp_dir'], '%s_converted'% self.process_id),'-r%s'%os.path.join(self.conf['unitex_dir'], 'Norms', lang, 'Norm.txt'))
        self.manager.Tokenize(os.path.join(self.conf['tmp_dir'], '%s_converted.snt'% self.process_id),'-a%s'%os.path.join(self.conf['unitex_dir'], 'Alphabets', lang, 'Alphabet.txt'))
        # Get tokens from file
        tokens_file = open(os.path.join(self.conf['tmp_dir'], '%s_converted_snt/tokens.txt' % self.process_id), "r")
        tokens = re.split('\r\n', unicode(tokens_file.read().decode('utf-16')), re.U)
        tokens.remove(tokens[0])
        tokens = unitex_tokens(self.conf['tmp_dir'], self.process_id, tokens)
        try:
            while True:
                tokens.remove('')
        except:
            pass
        try:
            while True:
                tokens.remove(' ')
        except:
            pass
        # Clean temporal files
        detroy_unitex_env(self.conf, self.process_id)
        # Return tokens
        return tokens
        
        
        
        
    def postagger(self, tokenss, lang):
        """
        
        """
        # Load tokenizer configuration
        f = open('conf/UnitexPOSTTagger.yml')
        self.conf = yaml.load(f)
        f.close()
        # Assertions
        assert(lang in self.conf['supported_langs'])
        # Unitex commands execution
        pos = []
        tokens_flatten = list(set(tokens))
        if not ' ' in tokens_flatten:
            tokens_flatten.append(' ')
        # Create process id
        process_id = str(uuid.uuid1())
        # Destroy environment if exists and creat dir
        detroy_unitex_env(self.conf, process_id)
        #Check if tmpdir exists
        if not os.path.exists(self.conf['tmp_dir']):
            os.mkdir(self.conf['tmp_dir'])
        os.mkdir(os.path.join(self.conf['tmp_dir'], '%s_converted_snt' % process_id))
        unitex_text_cod(self.conf['tmp_dir'], process_id, tokens, tokens_flatten)
        converted = open(os.path.join(self.conf['tmp_dir'], '%s_converted.snt' % process_id), 'w')
        tokens_file = file(os.path.join(self.conf['tmp_dir'], '%s_converted_snt/tokens.txt' % process_id), 'w')
        output = "%010d\n"%len(tokens_flatten)
        for token in tokens_flatten:
            output += "%s\n"%token
        tokens_file.write(output.encode('utf-16'))
        tokens_file.close()
        delas_conf = self.conf['delas_applied'][lang]
        delas = []
        for dela in delas_conf:
            dela_path = os.path.join(self.conf['unitex_dir'], 'Dela', dela)
            if os.path.exists(dela_path):
                delas.append(dela_path)
            else:
                print "[ERROR] Dico %s doesn't exist." % dela_path
        # Apply dico using Unitex command
        self.manager.Dico('-t%s'%os.path.join(self.conf['tmp_dir'], '%s_converted.snt' % process_id), '-a%s'%os.path.join(self.conf['unitex_dir'], 'Alphabets', lang, 'Alphabet.txt'), *delas)
        # Debug
        print "Tokens calculated %s" % str(pos)
        print "Processed"
        # Extract tags
        tags = []
        tags_file = open(os.path.join(self.conf['tmp_dir'], '%s_converted_snt/dlf'%process_id), "r")
        tags.extend(re.split('\r\n', unicode(tags_file.read().decode('utf-16')), re.U))
        tags_file.close()
        tags_file = open(os.path.join(self.conf['tmp_dir'], '%s_converted_snt/dlc'%process_id), "r")
        tags.extend(re.split('\r\n', unicode(tags_file.read().decode('utf-16')), re.U))
        tags_file.close()
        tags_file = open(os.path.join(self.conf['tmp_dir'], '%s_converted_snt/err'%process_id), "r")
        unknowns = re.split('\r\n', unicode(tags_file.read().decode('utf-16')), re.U)
        for unknown in unknowns:
            if unknown != "":
                tags.append("%s,.UNKNOWN"%unknown)
        tags_file.close()
        return generate_pos(tags, tokens, self.conf['allowed_flex_codes'], self.conf['allowed_pos_tags'])
        
        
        
        
# Instanciate an object
unitexManager = UniteManager()

# Get tokens
tokens = unitexManager.tokenizer("Spain and england are different countries", "es")
print tokens

# Apply POSTtagging
post = unitexManager.postagger(tokens, "es")
print post

# Apply Grammar
#post = unitexManager.grammar(tokens, "es")
#print post








