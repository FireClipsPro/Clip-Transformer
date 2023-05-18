import openai
import os
from math import ceil
import logging
import re
import json

logging.basicConfig(level=logging.INFO)

class SentenceSubjectAnalyzer:
    def __init__(self,
                 queries_folder_path):
        self.queries_folder_path = queries_folder_path
        logging.info("SubjectAnalyzer created")
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~      
    def process_transcription(self, 
                              transcription,
                              transcription_length_sec,
                              seconds_per_query,
                              video_description,
                              output_file_name="queries.json"):
        
        if os.path.exists(self.queries_folder_path + output_file_name[:-4] + '.json'):
            with open(self.queries_folder_path + output_file_name[:-4] + '.json', "r") as f:
                query_list = json.load(f)
            return query_list
        
        logging.info("Processing transcription")
        query_list = []
        sentence_list = []

        # Create sentence_list
        for time_chunk_start in range(0, ceil(transcription_length_sec), seconds_per_query):
            time_chunk_end = time_chunk_start + seconds_per_query
            sentence = ""

            for text_segment in transcription:
                if ((text_segment['start'] >= time_chunk_start and text_segment['start'] <= time_chunk_end)
                    or (text_segment['end'] >= time_chunk_start and text_segment['end'] <= time_chunk_end)
                    or (text_segment['start'] <= time_chunk_start and text_segment['end'] >= time_chunk_end)):
                    sentence += text_segment['text'] + " "

            sentence_list.append(sentence)

        # Create query_list using sentence_list
        for i, sentence in enumerate(sentence_list):
            time_chunk_start = i * seconds_per_query
            time_chunk_end = time_chunk_start + seconds_per_query

            if sentence == "":
                continue

            query = self.assign_query_to_time_chunk(sentence_list, i, video_description)
            query_list.append({'query': query, 'start': time_chunk_start, 'end': time_chunk_end, 'sentence': sentence})
            logging.info(f"Time chunk: {time_chunk_start}-{time_chunk_end}, Query: {query}")

        query_list = self.create_queries_for_null_time_chunks(query_list)
        self.save_queries(query_list, output_file_name)
        return query_list
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def assign_query_to_time_chunk(self, sentence_list, i, video_description):
        current_sentence = sentence_list[i]
        query = self.parse_sentence_subject(current_sentence, video_description)

        j = 1
        while query is None and (i - j >= 0 or i + j < len(sentence_list)):
            if i - j >= 0:
                current_sentence = sentence_list[i - j] + " " + current_sentence
                query = self.parse_sentence_subject(current_sentence, video_description)

            if query is None and i + j < len(sentence_list):
                current_sentence += " " + sentence_list[i + j]
                query = self.parse_sentence_subject(current_sentence, video_description)

            j += 1

        return query
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def save_queries(self, query_list, file_name="queries.json"):
        logging.info("Saving queries to file")
        print(os.getcwd())
        with open(self.queries_folder_path + file_name[:-4] + '.json', "w") as f:
            json.dump(query_list, f)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def create_queries_for_null_time_chunks(self, query_list):
        logging.info("Creating queries for null time chunks")
        closest_right_non_null_query = ""
        for i in range(len(query_list)):
            if query_list[i]['query'] == None:
                if i == 0:
                    if query_list[i]['query'] != None:
                            closest_right_non_null_query = query_list[j]['query']
                    query_list[i]['query'] = closest_right_non_null_query
                elif i == len(query_list) - 1:
                    query_list[i]['query'] = query_list[i-1]['query']
                else:
                    for j in range(i+1, len(query_list)):
                        if query_list[j]['query'] != None:
                            closest_right_non_null_query = query_list[j]['query']
                            break
                    query_list[i]['query'] = query_list[i-1]['query'] + " " + closest_right_non_null_query
        return query_list
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~          
    def remove_repeated_phrases(self, text):
        pattern = re.compile(r'\b(\w[\w\s]*\w)\b(?=.*\b\1\b)')
        cleaned_text = re.sub(pattern, '', text)
        return cleaned_text.strip()

    def parse_sentence_subject(self, sentence, video_description):
        cleaned_sentence = self.remove_repeated_phrases(sentence)
        logging.info(f"Parsing sentence subject: {cleaned_sentence}")

        openai.api_key = os.getenv("OPENAI_API_KEY")

        response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
                {"role": "system", "content": """You are a google images search query generator.
                    Given a video description and a transcript excerpt, identify the main subject or object within the excerpt and ignore the video description.
                    Generate a relevant and interesting query for Google Images based on the main subject or object from the excerpt.
                    If the excerpt is about a concept, generate a query that represents people embodying the concept through their actions rather than an image that might contain text.
                    If the excerpt is about a concrete subject or object, prioritize it.
                    Reply only with the search query or 'null query' if you need more context.
                    """},
                {"role": "user", "content": f"""Video description: {video_description}
                Make an image query that is relevant only to the transcript excerpt.
                Transcript excerpt: {cleaned_sentence}"""}
            ]
        )
        logging.info(f"Response: {response['choices'][0]['message']['content']}") 

        if (("null" in response['choices'][0]['message']['content'] or "Null" in response['choices'][0]['message']['content'])
            and ("query" in response['choices'][0]['message']['content'] or "Query" in response['choices'][0]['message']['content'])):
            logging.info("Received null query")
            return None
 
        query = response['choices'][0]['message']['content'].replace('"', '').replace("query", "").replace("Query", "")
        logging.info(f"Generated query: {query}")

        return query

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# video_description = "The speaker shares a story of encountering a jaguar while alone in the jungle and how it energized and motivated him to continue his journey."
# cleaned_sentence = "  I felt like I understood the intentions of the cat.  If she was hunting, I'd already be dead.  She was curious. "


# openai.api_key = os.getenv("OPENAI_API_KEY")
# for i in range(5):
    # response = openai.ChatCompletion.create(
    # model="gpt-3.5-turbo",
    # messages=[
    #     ]
    # )
    # logging.info(f"Response: {response['choices'][0]['message']['content']}")