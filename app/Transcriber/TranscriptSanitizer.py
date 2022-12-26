
# This could be useful for sanitizing text from the transcript
# some of the sanittizations are unnecessary for our purposes
# but I left them in in case we need them
class TranscriptSanitizer:
    def __init__(self):
        print("SubjectAnalyzer created");
    
    def sanitize_text(self, text):
        text = text.replace("um", "")
        text = text.replace("uh", "")
        text = text.replace("Um", "")
        text = text.replace("Uh", "")
        
        # Remove all punctuation
        text = text.translate(str.maketrans('', '', string.punctuation))
        
        # Remove all non-ASCII characters
        text = text.encode("ascii", "ignore").decode()
        
        # Convert all characters to lowercase
        text = text.lower()
        
        # Remove all leading and trailing whitespace
        text = text.strip()
        
        return text