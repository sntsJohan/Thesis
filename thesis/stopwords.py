TAGALOG_STOP_WORDS = {
    # -------------------------------------------------
    # Common Tagalog Stop Words (Pronouns, Particles, Conjunctions, etc.)
    # -------------------------------------------------
    'akin', 'ako', 'alin', 'amin', 'ang', 'ano', 'atin', 'at', 'ay', 'ayan', 
    'ba', 'bakit', 'basta', 'bukod', 'bilang',
    'dahil', 'dalawa', 'daw', 'dapat', 'din', 'dito', 'doon', 'dyan', # dyan = diyan variation
    'eh', 'eto', 'ewan',
    'gaano', 'gayunman', 'ganito', 'ganyan', 'ganoon', 'ganun', # ganun = ganoon variation
    'habang', 'hala', 'halos', 'hanggang', 'hay', 'heto', # heto = eto variation
    'iba', 'ikaw', 'in Suffixyo', 'isa', 'isinasaad', 'itaas', 'ito', 'iyo',
    'ka', 'kahit', 'kailangan', 'kailan', 'kami', 'kanila', 'kanino', 'kanya', 
    'kapag', 'kapwa', 'kasi', 'katulad', 'kaya', 'kayo', 'kita', 'ko', 'konti',
    'kong', 'kulang', 'kumusta', 'kung', 'kundi', 'kaysa',
    'lang', # Very common minimizer
    'laban', 'lahat', 'lamang', 'lubos',
    'maari', 'maaari', 'mag', 'maging', 'magkano', 'may', 'mayroon', 'mga', 
    'minsan', 'mismo', 'mo', 'mong', 'mula', 'muli', 'musta', # musta = kumusta variation
    'na', 'naging', 'nais', 'naku', 'naman', 'nang', 'nasaan', 'nasa', 'ni',
    'nila', 'ninyo', 'nito', 'niya', 'niyan', 'niyon', 'non', 'noon', # non = noon variation
    'nung', # colloquial version of 'noong'
    'ng', 'nga', 'ngayon', 'ngunit',
    'o', 'oo', 'opo', # Yes variations
    'pa', 'paano', 'pala', 'pati', 'para', 'paraan', 'pareho', 'pataas', 
    'pero', 'po', 'prin', # prin = rin/din variation
    'puede', 'puwede', 'pwede', # Puede/Puwede variations
    'raw', # variation of daw
    'rin',
    'sa', 'saan', 'sabi', 'sabihin', 'sarili', 'saka', 'salamat', 'samantala', 
    'sana', 'sila', 'sino', 'siya', 'siyempre', 'syempre', # Siyempre variation
    'talaga', # Can be emphatic, but often filler
    'tatlo', 'tayo', 'tao', 'tapos', 'teka', # Teka = wait
    'tulad', 'tungkol', 'tsaka', # Tsaka = at saka / and then
    'ulit',
    'una',
    'upang',
    'wala',
    'yan', 'yata', 'yo', # yo = iyo/kayo abbreviation
    'yun', # colloquial version of 'iyon'

    # -------------------------------------------------
    # Common English Stop Words Frequently Used in Taglish
    # -------------------------------------------------
    'a', 'about', 'actually', 'after', 'again', 'all', 'also', 'am', 'an', 'and', 
    'any', 'are', "aren't", 'as', 'at',
    'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by',
    'can', "can't", 'cannot', 'could', "couldn't",
    'did', "didn't", 'do', 'does', "doesn't", 'doing', 'down', 'during',
    'each',
    'feel', 'few', 'for', 'from', 'further',
    'get', 'gets', 'got',
    'had', "hadn't", 'has', "hasn't", 'have', "haven't", 'having', 'he', "he'd", 
    "he'll", "he's", 'her', 'here', "here's", 'hers', 'herself', 'him', 'himself', 
    'his', 'how', "how's",
    'i', "i'd", "i'll", "i'm", "i've", 'if', 'in', 'into', 'is', "isn't", 'it', 
    "it's", 'its', 'itself',
    'just', 'know',
    'let', "let's", 'like', # Often used as a filler "like, ano..."
    'me', 'more', 'most', "mustn't", 'my', 'myself',
    'need', 'no', 'nor', 'not', 'now',
    'of', 'off', 'on', 'once', 'only', 'or', 'other', 'ought', 'our', 'ours', 
    'ourselves', 'out', 'over', 'own',
    'same', 'see', "shan't", 'she', "she'd", "she'll", "she's", 'should', "shouldn't", 
    'so', 'some', 'such',
    'than', 'that', "that's", 'the', 'their', 'theirs', 'them', 'themselves', 'then', 
    'there', "there's", 'these', 'they', "they'd", "they'll", "they're", "they've", 
    'this', 'those', 'though', 'through', 'to', 'too',
    'under', 'until', 'up', 'us', 'use',
    'very',
    'want', 'was', "wasn't", 'we', "we'd", "we'll", "we're", "we've", 'well', 'were', 
    "weren't", 'what', "what's", 'when', "when's", 'where', "where's", 'which', 
    'while', 'who', "who's", 'whom', 'why', "why's", 'will', 'with', "won't", 
    'would', "wouldn't",
    'yes', # English 'yes'
    'you', "you'd", "you'll", "you're", "you've", 'your', 'yours', 'yourself', 
    'yourselves',

    # -------------------------------------------------
    # Common Chat/Internet Slang, Expressions, and Fillers (FB Context)
    # -------------------------------------------------
    'afaik', # As far as I know
    'amp', # Short for 'ampota/ampotek', mild curse often used as filler/exclamation
    'ano', # Often used as a filler "uhm"
    'anyways', 'anyway',
    'ask', 'asking',
    'bes', 'beshie', 'beshy', # Friend terms, often filler
    'bet', # Slang for 'I agree' or 'I like'
    'brb', # Be right back
    'btw', # By the way
    'char', 'charot', 'chos', 'chz', # Joke/Just kidding variations
    'comment', 'comments',
    'ctto', # Credit to the owner
    'di', # Short for 'hindi' (no/not)
    'dm', # Direct message
    'dun', # Short for 'doon' (there)
    'edi', # "So / Then" conjunction
    'fb', # Facebook
    'follow', 'following', 'followers',
    'fyi', # For your information
    'g', # Game (used like 'I'm in')
    'grabe', # Exclamation (Wow/OMG), often filler
    'haha', 'hahaha', 'hahahahaha', # Laughing variations
    'hayst', # Sigh expression
    'hehe', 'hehehe', 'hehehehe', # Laughing variations
    'hi', 'hello', 'hey',
    'hm', 'hmm', # Thinking sounds
    'hoy', 'oi', 'uy', # Calling attention
    'huh', 'huhuhu', # Crying/Sad expression or confusion
    'idol', # Term of address, often filler
    'ig', # Instagram
    'ikr', # I know right
    'imo', 'imho', # In my opinion / In my humble opinion
    'jan', # jan = diyan/dyan variation
    'k', 'kk', 'ok', 'oki', 'okay', 'okies', # Okay variations
    'kala', 'akala', # Thought / Assumed
    'kanina', # A while ago
    'kc', # kc = kasi variation
    'kekeke', # Laughing variation (from K-culture)
    'kita', # See you / also pronoun
    'klang', # klang = ok lang / okay only
    'kuya', 'ate', 'tito', 'tita', 'manong', 'manang', # Address terms, often filler
    'legit', # Legitimate, often used for emphasis/agreement
    'link', 'linked',
    'lods', 'lodi', # 'idol' reversed, term of address, often filler
    'lol', 'lmao', 'lul', 'lolz', # Laughing variations
    'mamaya', # Later
    'medyo', # Kind of / Sort of
    'minsan', # Sometimes
    'much', 'many',
    'muna', # For now / First
    'nag', # Verb prefix, very common
    'nako', 'naku', # Expression (Oh my / Oh dear)
    'nays', # nice
    'ngl', # Not gonna lie
    'np', # No problem
    'nyahaha', 'nyeh', # Laughing/Mischief variations
    'omg', 'omgg', 'omz', # Oh my god variations
    'opo', # Yes (polite)
    'orayt', # alright
    'paps', 'pops', # Term of address (male), often filler
    'parang', # Like / As if / Seems
    'pasok', # Enter / Included
    'pati', # Also / Including
    'pede', # pede = pwede variation
    'pic', 'picture',
    'pl', 'pls', 'plz', # Please variations
    'pm', # Private message
    'post', 'posted',
    'pre', # Friend/Bro term
    'reply', 'replied',
    'sali', # Join
    'share', 'shared',
    'shoutout', 'shout out',
    'sige', 'ge', # Okay / Go ahead variations
    'sis', 'sisz', 'mumsht', # Female term of address, often filler
    'skL', # Share ko lang / Just sharing
    'slmt', # salamat variation
    'si','nyo','nya','nia', 'lng', # Term of address (female), often filler
    'smh', # Shaking my head
    'sorry', 'pasensya',
    'sure',
    'sus', # Expression of disbelief/doubt (short for Jesus)
    'tau', # tau = tayo variation
    'thanks', 'thank', 'thx', 'tnx', 'ty', # Thank you variations
    'tldr', # Too long; didn't read
    'totoo', # True / Real
    'true', 'tru', 'truelaloo', # True variations
    'try',
    'tsk', 'tss', # Sound of disapproval/annoyance
    'ung', # ung = ang variation
    'u', # you variation
    'ur', # your variation
    'wag', # Don't (short for huwag)
    'wait', 'wey', 'wait lang', # Wait variations
    'wala', 'wla', # Nothing / None variations
    'weh', # Expression of disbelief
    'wow', 'woah',
    'wth', 'wtf', # Exclamations/Questions (What the...)
    'yah', 'yeah', 'yep', 'yup', # Yes variations
    'yun', # That
    'yung', # yung = ang variation
    'yt', # YouTube
    'nyan',
    'yang', # yang = ang variation
    'yung', # yung = ang variation
    'pag', # Short for 'kapag' (when)
    'kaso', # Short for 'kasi' (because)
    'kasi', # Because
    'niyo', # You (plural) variation
    'naka', # Short for 'nakaka' (able to)
    'ha', # Sound of confusion or surprise
    'hindi', # No / Not
    'baka', # Maybe / Perhaps
    'yang', # That (colloquial)
    'yon', # That (colloquial)
    'dahil', # Because
    'sana', # Hopefully / I wish
    'kasi', # Because
    'nalang', # Just / Only
    'lang', # Just / Only
    'kayo', # You (plural) variation
    'sige', # Okay / Go ahead

    # -------------------------------------------------
    # Numbers (Digits and Words) - Add more if needed
    # -------------------------------------------------
    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
    'isa', 'dalawa', 'tatlo', 'apat', 'lima', 'anim', 'pito', 'walo', 'siyam', 'sampu',
    'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten',
    'first', 'second', 'third', 
    
    # -------------------------------------------------
    # Common Hashtags (Often noisy) - Use with caution
    # -------------------------------------------------
    # '#fyp', '#foryoupage', '#tiktok', '#facebook', '#viral', '#trending' 
    # (Consider if hashtags themselves should be removed entirely or treated separately)
}