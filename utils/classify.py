#hide_output
from transformers import pipeline
from utils.labels import labels
import time
# Change `transformersbook` to your Hub username
model_id = "TieIncred/distilbert-base-uncased-finetuned-walden"
classifier = pipeline("text-classification", model=model_id)

classifier_zeroshot = pipeline("zero-shot-classification", model="facebook/bart-large-mnli", device=0)



def classify_faqs(input_text, prev_class=None):
    result = classifier_zeroshot(input_text, candidate_labels=['Request to Repeat','studies','no'], multi_class=True)
    if result['scores'][result['labels'].index("Request to Repeat")] > 0.8:
        return prev_class
    if result['scores'][result['labels'].index("no")] > 0.8:
        return 'no'
    print(result['labels'], result['scores'])
    preds = classifier(input_text)
    predicted_label = labels[int(preds[0]['label'].split('_')[-1])]
    if predicted_label == 'Walden University Online Learning Overview':
        if 'library' in input_text.lower():
            return 'Online Library Resources Query'
        else:
            return 'Online Student Technology Requirements'
    if predicted_label == 'Practical Experience Opportunities Checker':
        keywords = ['focus', 'special', 'concent']
    
        # Check if any of the keywords exist in the input text
        if any(keyword in input_text.lower() for keyword in keywords):
            return 'Communication Program Specializations Query'
    if predicted_label == 'Communication Skills Development':
        if 'application' in input_text.lower():
            return "Walden University BS Communication Application Process"

    if predicted_label == 'Workforce Preparation In Communication Program':
        return 'Walden University Career Placement Services For Communication Graduates Query'   
    return predicted_label

