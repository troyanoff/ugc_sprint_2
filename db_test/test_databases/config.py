
es_setting = {
    'refresh_interval': '1s',
    'analysis': {
        'filter': {
            'english_stop': {
                'type': 'stop',
                'stopwords': '_english_'
            },
            'english_stemmer': {
                'type': 'stemmer',
                'language': 'english'
            },
            'english_possessive_stemmer': {
                'type': 'stemmer',
                'language': 'possessive_english'
            },
            'russian_stop': {
                'type': 'stop',
                'stopwords': '_russian_'
            },
            'russian_stemmer': {
                'type': 'stemmer',
                'language': 'russian'
            }
        },
        'analyzer': {
            'ru_en': {
                'tokenizer': 'standard',
                'filter': [
                    'lowercase',
                    'english_stop',
                    'english_stemmer',
                    'english_possessive_stemmer',
                    'russian_stop',
                    'russian_stemmer'
                ]
            }
        }
    }
}

es_mapping_reviews = {
    'dynamic': 'strict',
    'properties': {
        'user_id': {
            'type': 'keyword'
        },
        'filmwork_id': {
            'type': 'keyword'
        },
        'datetime': {
            'type': 'keyword'
        },
        'like_id': {
            'type': 'keyword'
        },
        'text': {
            'type': 'text',
            'analyzer': 'ru_en',
            'fields': {
                'raw': {
                    'type':  'keyword'
                }
            }
        }
    }
}


es_mapping_bookmarks = {
    'dynamic': 'strict',
    'properties': {
        'user_id': {
            'type': 'keyword'
        },
        'filmwork_id': {
            'type': 'keyword'
        }
    }
}


es_mapping_likes = {
    'dynamic': 'strict',
    'properties': {
        'user_id': {
            'type': 'keyword'
        },
        'filmwork_id': {
            'type': 'keyword'
        },
        'estimation': {
            'type': 'integer'
        },
    }
}