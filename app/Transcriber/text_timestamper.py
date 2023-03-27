

class TextTimeStamper:

    def __init__(self):
        pass

    def timestamp_chunk_of_text(self, transcription, chunk_length):
        stamped_words = self.organize_transcript(transcription)
        return self.create_word_chunks(stamped_words, chunk_length)

    def organize_transcript(self, transcript):
        stamped_words = []
        words_info = transcript['word_segments']
        for word_info in words_info:
            word_object = {}
            word_object['word'] = word_info['text']
            word_object['start_time'] = round(word_info['start'], 2)
            word_object['end_time'] = round(word_info['end'], 2)
            stamped_words.append(word_object)
        return stamped_words

    def create_word_chunks(self, stamped_words, chunk_length):
        stamped_texts = []
        words = []
        text_object = {}
        text_object['start_time'] = 0
        text_object['end_time'] = 0
        text_object['text'] = ''
        text_object['words'] = words
        current_text_start_time = 0
        last_text_end_time = 0
        for word_object in stamped_words:
            if abs(word_object['end_time'] - current_text_start_time) <= chunk_length:
                if text_object['text'] != '':
                    text_object['text'] = f'{text_object["text"]} {word_object["word"]}'
                else:
                    text_object['text'] = word_object['word']
                text_object['end_time'] = word_object['end_time']
                last_text_end_time = word_object['end_time']
                words.append(word_object)
                text_object['words'] = words
            else:
                text_object['end_time'] = last_text_end_time
                stamped_texts.append(text_object)
                current_text_start_time = word_object['start_time']
                text_object = {}
                text_object['start_time'] = word_object['start_time']
                text_object['end_time'] = word_object['end_time']
                text_object['text'] = word_object['word']
                last_text_end_time = word_object['end_time']
                words = [word_object]
                text_object['words'] = words
        stamped_texts.append(text_object)
        return stamped_texts


# beginning end_time gets stuck at 0 and time = 11, end_time gets stuck at 12


