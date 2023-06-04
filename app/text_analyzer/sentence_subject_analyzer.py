import openai
import os
from math import ceil
import logging
import re
import json

logging.basicConfig(level=logging.INFO)

class SentenceSubjectAnalyzer:
    def __init__(self,
                 queries_folder_path,
                 openai_api):
        self.queries_folder_path = queries_folder_path
        self.openai_api = openai_api
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

            for word in transcription:
                if ((word['start'] >= time_chunk_start and word['start'] <= time_chunk_end)
                    or (word['end'] >= time_chunk_start and word['end'] <= time_chunk_end)
                    or (word['start'] <= time_chunk_start and word['end'] >= time_chunk_end)):
                    sentence += word['text'] + " "

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
        if cleaned_sentence == "" or cleaned_sentence == None:
            return None

        model = "gpt-3.5-turbo"
        system_prompt = ("You are a google images search query generator. "
                        "Given a video description and a transcript excerpt, identify the main subject or object within the excerpt and ignore the video description. "
                        "Generate a relevant and interesting query for Google Images based on the main subject or object from the excerpt. "
                        "If the excerpt is about a concept, generate a query that represents people embodying the concept through their actions rather than an image that might contain text. "
                        "If the excerpt is about a concrete subject or object, prioritize it. "
                        "Reply only with the search query or 'null query' if you need more context.")
        # Add a check for NoneType before concatenation
        user_prompt = ("Video description: " + (video_description if video_description is not None else "") +
                    " Make an image query that is relevant only to the transcript excerpt. "
                    "Transcript excerpt: " + (cleaned_sentence if cleaned_sentence is not None else ""))

        
        response = self.openai_api.query(system_prompt, user_prompt, model)
        
        logging.info(f"Response: {response}") 

        if (("null" in response or "Null" in response)
            and ("query" in response or "Query" in response)):
            logging.info("Received null query")
            return None

        query = response.replace('"', '').replace("query", "").replace("Query", "").replace("query:", "").replace("Query:", "").replace("/", " or ")
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