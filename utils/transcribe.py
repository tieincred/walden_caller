import torch
# import nltk
from transformers import BertModel, BertTokenizer
from faster_whisper import WhisperModel
# from nltk.corpus import stopwords

# Load NLTK stopwords
# nltk.download('stopwords')
# nltk.download('punkt')
# stopwords = set(stopwords.words('english'))

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")


transcript_model = WhisperModel("large-v2")
# transcript_model = WhisperModel("medium.en", device="cuda", compute_type="float16")
def transcript(audio_path):
  transcription = ""
  segments, info = transcript_model.transcribe(audio_path, language='en')
#   print(info)
  for segment in segments:
    #   print(segment)
      transcription = transcription + segment.text
  return transcription
import time

# start = time.time()
# print(start)
# print(transcript('check.wav'))
# end = time.time()
# time_taken = f"{end-start}"
# print(time_taken)