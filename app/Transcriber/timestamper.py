

class TextTimeStamper:

    def __init__(self):
        pass

    def timestamp_chunk_of_text(self, transcription, chunk_length):
        stamped_words = self.organize_transcript(transcription)
        return self.create_word_chunks(stamped_words, chunk_length)

    def organize_transcript(self, transcript):
        stamped_words = []
        for result in transcript.results:
            alternative = result.alternatives[0]
            for word_info in alternative.words:
                word_object = {}
                word_object['word'] = word_info.word
                word_object['start_time'] = word_info.start_time.seconds
                word_object['end_time'] = word_info.start_time.seconds
                stamped_words.append(word_object)

        return stamped_words

    def create_word_chunks(self, stamped_words, chunk_length):
        stamped_texts = []
        text_object = {}
        text_object['start_time'] = 0
        text_object['end_time'] = 0
        text_object['text'] = ''
        current_text_start_time = 0
        for word_object in stamped_words:
            if abs(word_object['end_time'] - current_text_start_time) < chunk_length:
                if text_object['text'] != '':
                    text_object['text'] = f'{text_object["text"]} {word_object["word"]}'
                else:
                    text_object['text'] = word_object['word']
                text_object['end_time'] = word_object['end_time']
            else:
                text_object['end_time'] = word_object['end_time']
                stamped_texts.append(text_object)
                current_text_start_time = word_object['end_time']
                text_object = {}
                text_object['start_time'] = word_object['end_time']
                text_object['end_time'] = word_object['end_time']
                text_object['text'] = word_object['word']
        stamped_texts.append(text_object)
        return stamped_texts







