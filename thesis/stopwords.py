# REVISED TAGALOG_STOP_WORDS - Avoiding filtering of potential hate/bullying words

TAGALOG_STOP_WORDS = {
    # -------------------------------------------------
    # Common Tagalog Stop Words (Pronouns, Particles, Conjunctions, etc.)
    # -------------------------------------------------
    'akin', 'ako', 'alin', 'amin', 'ang', 'ano', 'anong', 'anyong', 'apat', 'atin', 'at', 'ay', 'ayan',
    'ba', 'baka', 'bakit', 'balang', 'bale', 'basta', 'bawat', 'bilang', 'bukod',
    'dahil', 'dalawa', 'dalawang', 'dapat', 'daw', 'din', 'dito', 'doon', 'dyan', # dyan = diyan variation
    'eh', 'eto', 'ewan',
    'gaano', 'gayon', 'gayunman', 'ganito', 'ganyan', 'ganoon', 'ganun', # ganun = ganoon variation
    'gawin', 'ginagawa', 'ginawa', 'gumawa', 'gumagawa',
    'ha', # Exclamation/question particle
    'habang', 'hala', 'halos', 'hanggang', 'hay', 'heto', # heto = eto variation
    'hindi', 'hintay', 'huwag',
    'iba', 'ibaba', 'ibabaw', 'ibig', 'ikaw', 'ikayo', 'ilagay', 'ilalim', 'ilan', 'inyo', 'isa', 'isang', 'isinasaad', 'itaas', 'ito', 'iyo',
    'ka', 'kadalasang', 'kahit', 'kailangan', 'kailan', 'kaisa', 'kala', 'akala', 'kami', 'kanila', 'kanilang', 'kanino', 'kanya', 'kanyang',
    'kapag', 'kapwa', 'karaniwang', 'kasi', 'kasama', 'kaysa', 'katulad', 'kaya', 'kayo', 'kayong', 'kita', 'kina', 'ko', 'kong',
    'konti', 'kulang', # Note: 'kulang' kept as it's often functional ('kulang sa pansin' could be bullying, but word itself is broad)
    'kumusta', 'kung', 'kundi',
    'laban', 'labas', 'lahat', 'lamang', 'lang', # Very common minimizer
    'loob', 'lubha', 'lubos',
    'maari', 'maaari', 'maaga', 'mabuti', 'mag', 'maging', 'magka', 'magkano', 'mang', 'manga', # manga = mga variation
    'marami', 'maraming', 'marapat', 'mas', 'masyado', 'may', 'maya', 'mayroon', 'mga',
    'mismo', 'mo', 'mong', 'mula', 'muli', 'muna', 'musta', # musta = kumusta variation
    'na', 'namin', 'naging', 'nais', 'nakita', 'nako', 'naku', # Expression (Oh my / Oh dear) - Kept as generally not aggressive insult
    'nalang', 'naman', 'nang', 'napaka', 'narito', 'nasaan', 'nasa', 'naten', 'natin', # naten = natin variation
    'ni', 'nia', 'nila', 'nilang', 'ninyo', 'ninyong', 'nire', 'nito', 'niya', 'niyan', 'niyang', 'niyon', 'non', 'noon', # non = noon variation
    'nung', # colloquial version of 'noong'
    'ng', 'nga', 'ngayon', 'ngunit',
    'o', 'oo', 'opo', # Yes variations
    'pa', 'paano', 'pababa', 'paggawa', 'pagitan', 'pagkatapos', 'pahingi', 'paksa', 'pala', 'palagay',
    'pamamagitan', 'panahon', 'panay', 'panloob', 'papaano', 'papunta', 'para', 'paraan', 'parang', # parang = like/seems
    'pareho', 'pataas', 'pati', 'pero', 'pinaka', 'piraso', 'po', 'prin', # prin = rin/din variation
    'puede', 'puwede', 'pwede', # Puede/Puwede variations
    'raw', # variation of daw
    'rin',
    'sa', 'saan', 'sabi', 'sabihin', 'sarili', 'saka', 'saka', 'salamat', 'samantala', 'samin', # samin = sa amin variation
    'sana', 'sapat', 'sarado', 'saten', # saten = sa atin variation
    'say', 'says', 'sayo', # sayo = sa iyo variation
    'si', 'sila', 'silang', 'sinabi', 'sinasabi', 'sino', 'siya', 'siyang', 'siya', 'siyempre', 'syempre', # Siyempre variation
    'sobra',
    'subalit',
    'taas', 'tabi', 'talaga', # Can be emphatic, but often filler
    'tanong', 'tao', 'tapos', 'tatlo', 'tatlong', 'tayo', 'tayong', 'teka', # Teka = wait
    'tingin', 'totoo', # Often filler 'sa totoo lang'
    'tulad', 'tungkol', 'tsaka', # Tsaka = at saka / and then
    'ulit', 'uli', # Uli = ulit variation
    'una',
    'upang',
    'ulit',
    'wala', 'walang', 'wla', # wla = wala variation
    'wag', # Short for huwag
    'yan', 'yang', # yan/yang = iyan/iyang variations
    'yata', 'yo', # yo = iyo/kayo abbreviation
    'yun', 'yung', # yun/yung = iyon/iyong variations
    'yon', # yon = iyon variation
    'nyan', # nyan = niyan variation
    'nyo', # nyo = ninyo variation
    'nya', # nya = niya variation

    # -------------------------------------------------
    # Common English Stop Words Frequently Used in Taglish
    # (Keeping the extensive English list as these are mostly functional)
    # -------------------------------------------------
    'a', 'about', 'above', 'actually', 'after', 'again', 'against', 'all', 'almost', 'alone', 'along', 'already', 'also', 'although', 'always', 'am', 'an', 'and',
    'another', 'any', 'anyhow', 'anyone', 'anything', 'anyway', 'anyways', 'anywhere', 'are', "aren't", 'around', 'as', 'at',
    'be', 'because', 'become', 'becomes', 'been', 'before', 'behind', 'being', 'below', 'beside', 'besides', 'between', 'beyond', 'both', 'but', 'by',
    'can', "can't", 'cannot', 'com', # common in urls, sometimes detached
    'could', "couldn't",
    'did', "didn't", 'do', 'does', "doesn't", 'doing', 'done', 'down', 'during',
    'each', 'either', 'else', 'elsewhere', 'enough', 'etc', 'even', 'ever', 'every', 'everyone', 'everything', 'everywhere',
    'except',
    'feel', 'feels', 'felt', 'few', 'find', 'for', 'from', 'further',
    'get', 'gets', 'getting', 'go', 'goes', 'going', 'gone', 'got', 'gotten',
    'had', "hadn't", 'has', "hasn't", 'have', "haven't", 'having', 'he', "he'd", "he'll", "he's", 'hence', 'her', 'here', "here's", 'hereafter', 'hereby', 'herein', 'hereupon', 'hers', 'herself', 'him', 'himself',
    'his', 'how', "how's", 'however', 'http', 'https', # often appear in links
    'i', "i'd", "i'll", "i'm", "i've", 'ie', 'if', 'in', 'inc', 'indeed', 'instead', 'into', 'is', "isn't", 'it', "it's", 'its', 'itself',
    'just', 'keep', 'kept',
    'know', 'knows',
    'last', 'later', 'least', 'less', 'let', "let's", 'like', # Often used as a filler "like, ano..." - Keeping 'like' as it's very common filler, less likely a direct insult itself
    'ltd',
    'made', 'make', 'makes', 'making', 'many', 'may', 'maybe', 'me', 'meanwhile', 'might', 'mine', 'more', 'moreover', 'most', 'mostly', 'move', 'much', 'must', "mustn't", 'my', 'myself',
    'namely', 'near', 'need', 'needs', 'neither', 'never', 'nevertheless', 'next', 'no', 'nobody', 'none', 'noone', 'nor', 'not', 'nothing', 'now', 'nowhere',
    'of', 'off', 'often', 'on', 'once', 'one', 'only', 'onto', 'or', 'org', # common in urls
    'other', 'others', 'otherwise', 'ought', 'our', 'ours', 'ourselves', 'out', 'over', 'own',
    'part', 'per', 'perhaps', 'please', 'put',
    'rather', 'really',
    'same', 'say', 'says', 'see', 'seem', 'seemed', 'seeming', 'seems', 'seen', 'several', 'shan\'t', 'she', "she'd", "she'll", "she's", 'should', "shouldn't", 'show', 'shown', 'since', 'so', 'some', 'somehow', 'someone', 'something', 'sometime', 'sometimes', 'somewhere', 'still', 'such',
    'take', 'taken', 'taking',
    'than', 'that', "that's", 'the', 'their', 'theirs', 'them', 'themselves', 'then', 'thence', 'there', "there's", 'thereafter', 'thereby', 'therefore', 'therein', 'thereupon', 'these', 'they', "they'd", "they'll", "they're", "they've",
    'thing', 'things', 'think', 'thinks', 'this', 'those', 'though', 'through', 'throughout', 'thus', 'to', 'together', 'too', 'top', 'toward', 'towards',
    'try', 'tries', 'trying',
    'under', 'unless', 'until', 'up', 'upon', 'us', 'use', 'used', 'uses', 'using',
    'various', 'very', 'via',
    'want', 'wants', 'was', "wasn't", 'we', "we'd", "we'll", "we're", "we've", 'well', 'were', "weren't", 'what', "what's", 'whatever', 'when', "when's", 'whence', 'whenever', 'where', "where's", 'whereafter', 'whereas', 'whereby', 'wherein', 'whereupon', 'wherever', 'whether', 'which',
    'while', 'whither', 'who', "who's", 'whoever', 'whole', 'whom', 'whose', 'why', "why's", 'will', 'with', 'within', 'without', "won't", 'work', 'works', 'would', "wouldn't", 'www', # common in urls
    'yes',
    'yet', 'you', "you'd", "you'll", "you're", "you've", 'your', 'yours', 'yourself', 'yourselves',

    # -------------------------------------------------
    # Common Chat/Internet Slang, Expressions, and Fillers (FB Context)
    # (REMOVING terms commonly used in insults/hate speech)
    # -------------------------------------------------
    'afaik', # As far as I know
    'ahaha', 'ahahaha', # Laugh variations
    # 'amp', # REMOVED - Potential hate speech element
    'anooo', 'anu', 'ano po', # ano variations
    'ask', 'asking', 'asked',
    'ate', 'ateh', # Address term
    # 'aw', 'awit', 'awts', # REMOVED - Can be used mockingly
    'ayaw',
    'aysus', # Expression (like 'oh my')
    'bal', # Short for 'subalit'? or just filler
    'bes', 'besh', 'beshie', 'beshy', # Friend terms, often filler
    'bet', # Slang for 'I agree' or 'I like'
    'brb', # Be right back
    'bro', 'bruh', # Male address term
    'btw', # By the way
    'char', 'charot', 'charz', 'chos', 'chz', # Joke/Just kidding variations - Kept as typically self-deprecating or light-hearted joking marker
    'cge', 'cgeh', # sige variations
    'click',
    'comment', 'comments', 'commented',
    'congrats', 'congratulations',
    'ctto', # Credit to the owner
    'dami', # Short for 'marami'
    'de', 'deh', # Filler particle
    'dba', # diba = di ba (right?)
    'diba',
    'di', # Short for 'hindi' (no/not)
    'din', 'dn', # dn = din/rin variation
    'dito', 'dto', # dto = dito variation
    'dm', # Direct message
    'dun', # Short for 'doon' (there)
    'edi', # "So / Then" conjunction
    'ee', 'eee', # Filler sound / expression
    'ehem', # Clearing throat sound
    'eme', 'emz', # Filler, like 'chos' or 'whatever'
    'ern', # Filler sound
    'fb', # Facebook
    'fave', # favorite
    'follow', 'following', 'followers', 'followed',
    'fyi', # For your information
    'g', # Game (used like 'I'm in')
    # 'gagi', 'gago', # REMOVED - Potential hate speech / insult
    'ganern', # ganern = ganoon/ganun variation
    'ganon', # ganon = ganoon/ganun variation
    'ge', # Short for 'sige'
    'gets', 'getz', # get/understand variations
    'gg', # good game, sometimes used as 'it's over' or filler
    'giv', # give
    'grabe', 'grabeh', # Exclamation (Wow/OMG), often filler - Kept as generally expression of intensity, not direct insult
    'gud', # good
    'gusto', 'gs2', # gs2 = gusto variation
    'haha', 'hahaha', 'hahahaha', 'hahah', # Laughing variations - Kept, though can be mocking, very frequent neutral use
    'hai', # hi variation
    'hayst', 'hayz', # Sigh expression variations
    'hehe', 'hehehe', 'hehehehe', 'hehez', # Laughing variations - Kept
    'hi', 'hii', 'hihi', 'hihihi', 'hello', 'hellow', 'hey', 'heyy',
    'hirap', # Kept - general term
    'hm', 'hmm', 'hmmm', # Thinking sounds
    'hmp', # Sound of disapproval
    'hoy', 'hoi', 'oi', 'oy', 'uy', # Calling attention - Kept as neutral attention getters
    'huh', 'huhuhu', # Crying/Sad expression or confusion - Kept
    'huhu',
    'idol', # Term of address, often filler
    'ig', # Instagram
    'ikr', # I know right
    'iloveyou', # Often used casually
    'imo', 'imho', # In my opinion / In my humble opinion
    'ingat', 'ingats', # take care variations
    'jan', # jan = diyan/dyan variation
    'jaja', 'jajaja', # Spanish-style laugh, sometimes used
    'joke', 'jowk', # joke variations
    'k', 'kk', 'ok', 'oki', 'okay', 'okey', 'okies', 'okie', # Okay variations
    'kaayo', # Visayan word for 'very', often used in Taglish
    'kain', # eat - Kept
    # 'kainis', # REMOVED - Potential negative element
    'kala', 'akala', # Thought / Assumed
    'kami', 'kame', # kame = kami variation
    'kanina', # A while ago
    'kapatid', # sibling, sometimes used as address term
    'kaso', # but/except
    'kau', # kau = kayo variation
    'kaya', 'kayat', # so/therefore
    'kc', 'kse', # kc/kse = kasi variation
    'kekeke', 'keke', # Laughing variation (from K-culture)
    'kelan', # kelan = kailan variation
    'khit', # khit = kahit variation
    'kht', # kht = kahit variation
    'kinain', 'kumain',
    'kita', # See you / also pronoun
    'klang', # klang = ok lang / okay only
    'knina', # knina = kanina variation
    'kong', # kong = ko + ng
    'kuha', 'kumuha', 'kinuha',
    # 'kulit', # REMOVED - Potential negative element
    'kunwari',
    'kuya', 'kuyz', # Address term
    'ky', # ky = kay/kina variation
    'la', # Short for 'wala'
    'lakas',
    'lam', # lam = alam (know) variation
    'legit', # Legitimate, often used for emphasis/agreement
    'like', 'likes', 'liked', # FB actions + filler
    'link', 'linked',
    'lng', # lng = lang variation
    'lods', 'lodi', 'lodz', # 'idol' reversed, term of address, often filler
    'lol', 'lols', 'lolz', 'lmao', 'lmaoo', 'lul', 'lulz', # Laughing variations - Kept
    'mahal', # love/expensive, can be filler in greetings
    'makita',
    'mali', # Kept - general term
    'mama', 'mamsh', 'mamshie', # mum/female address term variations
    'man', # Particle 'even'/'also'
    'manong', 'manang', # Address terms
    'mas', # more
    'masyadong',
    'matagal',
    'medyo', # Kind of / Sort of
    'meron', # meron = mayroon variation
    'minsan', # Sometimes
    'miss', # miss (longing for / title)
    'mom', 'mommy',
    'mr', 'mrs', 'ms', # Titles
    'much',
    'mukha', 'mukhang', # face/looks like
    'nag', # Verb prefix, very common
    'naka', # Verb prefix, very common
    'nako', 'naku', 'nakupo', # Expression (Oh my / Oh dear) - Kept
    'naman', 'nmn', # nmn = naman variation
    'nanaman', # again
    'nasa', 'nasan', # nasan = nasaan variation
    'nays', # nice
    'neto', # neto = nito variation
    'nga', 'nge', 'ngek', # Expression of surprise/disbelief - Kept as generally mild
    'ngl', # Not gonna lie
    'ngunit',
    'nila',
    'nito',
    'niya',
    'niyo',
    'nmn', # naman variation
    'noh', # noh = no? (right?)
    'np', # No problem
    'nu', # nu = ano variation
    'nyahaha', 'nyeh', # Laughing/Mischief variations - Kept
    'oh', 'ooh', 'ohh',
    'omg', 'omgg', 'omz', # Oh my god variations - Kept as general exclamation
    'onga', # oo nga (yes indeed)
    'opo', # Yes (polite)
    'orayt', # alright
    'pack', 'pak', # Sound effect/exclamation
    'pag', # Short for 'kapag' (when)
    'pala', # Particle indicating realization
    'pang', # prefix
    'paps', 'papsi', 'pops', # Term of address (male), often filler
    'para', # for/like
    'parang', # Like / As if / Seems
    'pasensya', 'pasensiya', # Sorry variations
    'pasok', # Enter / Included
    'pati', # Also / Including
    'pede', # pede = pwede variation
    'pero',
    'pic', 'pics', 'picture',
    'pindot', # press/click
    'pl', 'pls', 'plz', 'please', # Please variations
    'pm', # Private message
    'post', 'posted', 'posting',
    'po',
    'pre', 'pare', 'par', # Friend/Bro term variations
    'problema',
    'punta', 'pumunta',
    'puro', # pure/all
    # 'putek', 'potek', # REMOVED - Potential hate speech element
    'pwedeng',
    'reply', 'replied', 'replying',
    'sabi',
    'sakanya', # sakanya = sa kanya variation
    'sakto', # exact/just right
    'sali', # Join
    'salamat', 'salamatpo', 'salamaat', # Thank you variations
    'san', # san = saan variation
    'sana', # Hopefully / I wish
    'sarap', # delicious
    'sayang', # waste/pity
    'send', 'sent',
    'share', 'shared', 'sharing',
    'shocks', # Expression of surprise - Kept
    'shoutout', 'shout out',
    'si',
    'sige', 'sge', 'ge', 'cge', # Okay / Go ahead variations
    'sila',
    'sinasabi',
    'sine', # sine = sino variation
    'sino',
    'sinu', # sinu = sino variation
    'siya',
    'sis', 'sisz', 'sissy', 'mumsht', 'mima', # Female term of address, often filler
    'skL', # Share ko lang / Just sharing
    'slmt', # salamat variation
    'smh', # Shaking my head
    'soon',
    'sorry', 'sori',
    'sya', 'xa', # sya/xa = siya variations
    'syempre', # siyempre variation
    'sure', 'surely',
    'sus', # Expression of disbelief/doubt (short for Jesus) - Kept as often mild
    'tag', 'tagged',
    'tagal', # long time
    'taka', # wonder
    'talaga', 'tlga', # tlga = talaga variation
    'tama', # correct/right
    # 'tangina', 'tang ina', # REMOVED - Definite hate speech element
    'tanong', 'tatanong',
    'tapos',
    'tau', # tau = tayo variation
    'tawa', # laugh
    'tayo',
    'tayo',
    'thanks', 'thank', 'thankyou', 'thx', 'tnx', 'ty', 'tysm', # Thank you variations
    'tignan', 'tingnan', # look variation
    'tito', 'tita', # Address term
    'tldr', # Too long; didn't read
    'totoo', # True / Real
    'treat',
    'true', 'tru', 'truu', 'truelaloo', # True variations
    'try', 'trying', 'tried',
    'tsk', 'tss', 'tsktsk', # Sound of disapproval/annoyance - Kept as mild
    'tulong', # help
    'u', # you variation
    'uh', 'uhm', 'umm', 'um', # Filler sounds
    'ulit', 'ulet', # ulet = ulit variation
    'ung', # ung = ang variation
    'ur', # your variation
    'us',
    'uusap', # talk
    'uy',
    'video', 'vid',
    'wag', # don't
    'wait', 'wey', 'waitlang', 'wt', # Wait variations
    'wala', 'wla', # Nothing / None variations
    'waley', # Slang for 'wala' or 'failed' - Kept as often light filler
    'watch', 'watching', 'watched',
    'weh', 'wehh', # Expression of disbelief - Kept as mild
    'welcome', # You're welcome
    'what', 'whats',
    'when',
    'where',
    'who',
    'why',
    'wish',
    'with',
    'wow', 'woah', 'woow', # Kept as general exclamation
    'wth', 'wtf', # Exclamations/Questions (What the...) - Kept as general exclamation, though context matters
    'yah', 'yeah', 'yehey', 'yey', 'yep', 'yes', 'yess', 'yup', # Yes variations
    'yun', 'yung', 'yon', # That variations
    'yiee', 'yii', # Expression of excitement/teasing - Kept
    'yt', # YouTube

    # -------------------------------------------------
    # Numbers (Digits and Words) - Keeping these as they are unlikely hate speech
    # -------------------------------------------------
    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '1st', '2nd', '3rd', '4th', '5th', # etc.
    'isa', 'dalawa', 'tatlo', 'apat', 'lima', 'anim', 'pito', 'walo', 'siyam', 'sampu',
    'isang', 'dalawang', 'tatlong', 'apat na', 'limang', 'anim na', 'pitong', 'walong', 'siyam na', 'sampung',
    'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten',
    'first', 'second', 'third', 'fourth', 'fifth', # etc.

    # -------------------------------------------------
    # Common Hashtags - Still recommend preprocessing hashtags separately
    # -------------------------------------------------
}
