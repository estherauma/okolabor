from django import template

register = template.Library()

@register.filter
def experience_filter(questions, question_key):
    for question in questions:
        if question.get('key') == question_key:
            return question.get('label') 
    return ''
