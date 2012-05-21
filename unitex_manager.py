#!/usr/bin/env python2.7-32
# -*- coding: utf-8 -*-
""" 
Unitex manager

"""
from unitex_tools import *
import yaml
import pyunitex
import uuid

class UnitexManager():
    
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
        
        
        
    def postagger(self, tokens, lang):
        """
        Whole process to apply posttagging to a list of tokens
        
        Returns:
        Documents with POSTTagging
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
        #Destroy unitex environment
        detroy_unitex_env(self.conf, process_id)
        aux = generate_pos(tags, tokens, self.conf['allowed_flex_codes'], self.conf['allowed_pos_tags'])
        # Clean temporal files
        detroy_unitex_env(self.conf, self.process_id)
        return aux
        
        
    def grammar(self, tokens, pos, lang):
        """
        Whole process to apply posttagging to a list of tokens

        Returns:
        Documents with POSTTagging
        """
        # Load tokenizer configuration
        f = open('conf/UnitexGrammar.yml')
        self.conf = yaml.load(f)
        f.close()
        # Assertions
        assert(lang in self.conf['supported_langs'])
        assert(type(tokens) == list)
        assert(type(pos) == list)
        # Process tokens
        tokens_flatten = list(set(tokens))
        if not ' ' in tokens_flatten:
            tokens_flatten.append(' ')
        # Create process id
        process_id = str(uuid.uuid1())
        #Check if tmpdir exists
        if not os.path.exists(self.conf['tmp_dir']):
            os.mkdir(self.conf['tmp_dir'])
        os.mkdir(os.path.join(self.conf['tmp_dir'], '%s_converted_snt' % process_id))
        #Processing the file unitex.cod from tokens
        unitex_text_cod(self.conf['tmp_dir'], process_id, tokens, tokens_flatten)
        open(os.path.join(self.conf['tmp_dir'], '%s_converted_snt/enter.pos' % process_id),'w').close()
        tokens_file = file(os.path.join(self.conf['tmp_dir'], '%s_converted_snt/tokens.txt' % process_id), 'w')

        #The tokens.txt file should start with the number (a number) of tokens that appears in the file
        output_tokens = "%010d\n"%int(len(tokens_flatten))
        for token in tokens_flatten:
            output_tokens += "%s\n"%(token)
        #Save the strings in each files, and close the files.
        tokens_file.write(output_tokens.encode('utf-16'))
        tokens_file.close()
        generate_dlf_dlc_from_pos(self.conf['tmp_dir'], process_id, pos)
        
        # Apply delas
        delas_conf = self.conf['delas_applied'][lang]
        delas = []
        for dela in delas_conf:
            dela_path = os.path.join(self.conf['unitex_dir'], 'Dela', dela)
            if os.path.exists(dela_path):
                delas.append("-m%s"%dela_path)
            else:
                self.logger.error("[ERROR] Dico %s doesn't exist." % dela_path)
                
        #Execute UNITEX commands, first engine locate, after engine concord
        self.grammar = self.conf['grammar_applied'][0]
        self.manager.Locate('-t%s/%s_converted.snt'%(self.conf['tmp_dir'], process_id),'%s/Graphs/%s'%(self.conf['unitex_dir'], self.grammar),'-a%s/Alphabets/%s/Alphabet.txt'%(self.conf['unitex_dir'], lang),'-L','-R','-n200','-z','-Y', *delas)
        self.manager.Concord('%s/%s_converted_snt/concord.ind'%(self.conf['tmp_dir'], process_id),'-m%s/%s_out'%(self.conf['tmp_dir'], process_id))
        #The output of previus commands is in s_out+process_id.
        out_file = file(os.path.join(self.conf['tmp_dir'], '%s_out' % process_id), 'r')
        salida = ''
        for line in out_file:
                salida += line.decode('utf-16')    
        out_file.close() #Close output file
        #Destroy unitex environment
        detroy_unitex_env(self.conf, process_id)
        return salida
        
        
def main():
    """ Main procedure
    """
    # Instanciate an object
    unitexManager = UnitexManager()

    # Get tokens
    tokens_result = unitexManager.tokenizer("me gusta mucho esto, pero lo otro me disgusta", "es")
    print 'Tokens: ',tokens_result

    # Apply POSTtagging
    pos_tagging = unitexManager.postagger(tokens_result, "es")
    print 'Pos tagging: ',pos_tagging

    # Apply Grammar
    grammar = unitexManager.grammar(tokens_result, pos_tagging, "es")
    print '=> ',grammar

if __name__ == '__main__':
    main()




