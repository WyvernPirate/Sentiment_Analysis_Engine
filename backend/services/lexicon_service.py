from lexicon_manager import lexicon_manager

class LexiconService:
    def __init__(self):
        self._lexicon = None
        self.refresh_lexicon()

    def refresh_lexicon(self):
        """Refresh the legacy lexicon format from the lexicon manager"""
        lexicon = lexicon_manager.lexicon
        
        self._lexicon = {
            'common_words': set(),
            'positive': {},
            'negative': {},
            'political': {}
        }
        
        if 'common_words' in lexicon:
            self._lexicon['common_words'] = set(lexicon['common_words'].keys())
        
        for category in ['positive', 'negative', 'political']:
            if category in lexicon:
                self._lexicon[category] = {
                    word: details.get('meaning', '') 
                    for word, details in lexicon[category].items()
                }
        
        if 'botswana_specific' in lexicon:
            for word, details in lexicon['botswana_specific'].items():
                self._lexicon['political'][word] = details.get('meaning', '')

    @property
    def legacy_lexicon(self):
        return self._lexicon

    def get_stats(self):
        return {
            "setswana_lexicon": self._lexicon,
            "total_setswana_words": sum(len(v) for v in self._lexicon.values())
        }

lexicon_service = LexiconService()
