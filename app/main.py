from VideoEditor import MediaAdder, VideoResizer
from content_generator import ImageScraper, ImageToVideoCreator
from decoder import SentenceSubjectAnalyzer



def main():
    # Transcribe the audio file
    media = MediaAdder()
    # chunk into time segments - for now 8 seconds
    _chunk_array = []
    _chunk_array.append({'start_time': 0, 'end_time': 8, 'text': 'I saw a horse on the moon.'})
    _chunk_array.append({'start_time': 8, 'end_time': 16, 'text': f'I\'m playing flappy bird on my computer.'})
    
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
        
    





    
    
 
 
main()
    
    
    
