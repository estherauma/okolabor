from django import template
 
register = template.Library()
 
@register.filter
def preference_filter(questions, question_key):
    print(questions)
    for question in questions:
        if question.get('key') == question_key:
            return question.get('label')
    
    return ''