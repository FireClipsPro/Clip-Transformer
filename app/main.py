
from ContentGenerator import ImageScraper
from Decoder import SentenceSubjectAnalyzer

def main():
    # Transcribe the audio file
    
    # chunk into time segments - for now 8 seconds
    # make an array called _chunk_array of dictionaries with the following
    # keys: start_time, end_time, text
    _chunk_array = []
    _chunk_array.append({'start_time': 0, 'end_time': 8, 'text': 'I love to eat pizza'})
    _chunk_array.append({'start_time': 8, 'end_time': 16, 'text': 'I love to eat watermelon'})
    
    # initialize the sentence subject analyzer and image scraper
    analyzer = SentenceSubjectAnalyzer()
    _image_scraper = ImageScraper()
    print("Initialized the sentence subject analyzer and image scraper")
    # for each segment:
    # parse the sentence subject
    # search for and download an image and save the imageID
    # to the _time_stamped_images array
    _time_stamped_images = []
    for chunk in _chunk_array:
        _sentence_subject = analyzer.parse_sentence_subject(chunk['text'])
        
        _image_id = _image_scraper.search_and_download(_sentence_subject, _image_scraper.PATH)
        
        _time_stamped_images.append({'start_time': chunk['start_time'], 'end_time': chunk['end_time'], 'imageID': _image_id})
    
    # print the _time_stamped_images array
    print(_time_stamped_images)
        

#run the main function
main()
    