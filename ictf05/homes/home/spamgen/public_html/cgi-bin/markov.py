import random
#from os import path

def mtext():
	stopword = "\n" # Since we split on whitespace, this can never be a word
	stopsentence = (".", "!", "?",) # Cause a "new sentence" if found at the end of a word
	sentencesep  = "\n" #String used to seperate sentences 

	# GENERATE TABLE
	w1 = stopword
	w2 = stopword
	table = {}


	for l in os.listdir('user_db'):

	  if getsize('user_db/'+l)<100: continue
	  f=open('user_db/'+l)
	  for line in f.readlines():
	    if line.find('-'*20+'END') != -1 : continue
	    for word in line.split():
	        if word[-1] in stopsentence:
	            table.setdefault( (w1, w2), [] ).append(word[0:-1])
	            w1, w2 = w2, word[0:-1]
	            word = word[-1]
	        table.setdefault( (w1, w2), [] ).append(word)
	        w1, w2 = w2, word
	  f.close()

 	table.setdefault( (w1, w2), [] ).append(stopword) 

	maxsentences  = 30

	w1 = stopword
	w2 = stopword
	sentencecount = 0
	sentence = []

        text=""
	while sentencecount < maxsentences: 
	    newword = random.choice(table[(w1, w2)])
	    if newword == stopword: continue
	    if newword in stopsentence:
	       text+= "%s%s%s" % (" ".join(sentence), newword, sentencesep)
	       sentence = []
	       sentencecount += 1
	    else:    
		sentence.append(newword)

	    w1, w2 = w2, newword
	return text.replace('\n','<BR>')

