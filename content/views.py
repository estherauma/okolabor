from decouple import config
from django.utils.dateparse import parse_datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
import re

from content.models import AggregatedContent
from content.serializers import AggregatedContentSerializer
from drf_yasg.utils import swagger_auto_schema


class ContentAPI():
    def __init__(self) -> None:
        self.api_url = config('CMS_API_URL')
        self.media_url = self.api_url.split('/api/okolabors')[0]
        self.access_token = config('CMS_API_TOKEN')
        self.headers = {
                "Authorization": f"Bearer {self.access_token}"
            }
        self.languages = []
        self.start_content_fetch()
        self.documents = {}

    def start_content_fetch(self):
        try:
            response = requests.get(self.api_url, headers=self.headers)
            self.content = response.json()
            self.languages = self.content['locales']
            self.documents = self.start_document_fetch()
        except requests.RequestException as e:
            return {
                "error": str(e)
            }
        except ValueError as e:
            print("Error: ", e)

    def start_document_fetch(self):
        documents = {}
        for language in self.languages:
            url = f"{self.api_url}?locale={language['code']}"
            language_docs = requests.get(url, headers=self.headers).json()
            documents[language['code']] = self.aggregate_content(language_docs)
        # save content to the database
        aggregated_content = AggregatedContent()
        aggregated_content.content = documents
        aggregated_content.save()
        return documents

    def aggregate_content(self, lang_content):
        aggregated_content = {}
        aggregated_content['languages'] = self.languages

        def aggregate_form_questions(form_qn_data):
            question_data = []
            additional_text = []
            for item in form_qn_data['dynamic_zone']:
                if item['__component'] == 'okolabor.form-questions':
                    question_options = []
                    if item['Options'] and item['OptionTranslations']:
                        question_options = generate_select_options(
                            item['Options'], item['OptionTranslations'])
                    question_data.append({
                        'key': item['Key'],
                        'label': item['Label'],
                        'category': item['Category'],
                        'help_text': item['HelpText'],
                        'required': item['Required'],
                        'placeholder': item['Placeholder'],
                        'question_type': item['QuestionType'],
                        'options': question_options
                    })

                if item['__component'] == 'okolabor.additional-text':
                    additional_text = aggregate_key_value_text(
                        item['repeatable_zone']
                    )
            return question_data, additional_text

        def aggregate_key_value_text(common_text_data):
            common_texts = []
            for item in common_text_data:
                common_texts.append({
                    'key': item['key'],
                    'value': item['value']
                })
            return common_texts

        def generate_select_options(options, options_translations):
            options = re.split(r',\s*|\s*,\s*', options)
            options_translations = re.split(
                r',\s*|\s*,\s*', options_translations)
            final_options_array = [
                    {"value": value, "label": key}
                    for key, value in zip(options_translations, options)
            ]
            return final_options_array

        def aggregate_menu_content(menu_content_data):
            menu_content = []
            for item in menu_content_data:
                menu_content.append({
                    'url': item.get('Url', None),
                    'icon': item.get('Icon', None),
                    'title': item.get('Title', None),
                    'enabled': item.get('Enabled', None),
                    'label': item.get('Label(Translate)', None),
                    'order': item.get('Order', None),
                })
            return menu_content

        def aggregate_media_data(media_data):
            try:
                if not media_data or not media_data.get('url'):
                    return None

                return {
                    'name': media_data.get('name', None),
                    'mime': media_data.get('mime', None),
                    'hash': media_data.get('hash', None),
                    'url': f'{self.media_url}{media_data["url"]}',
                    'size': media_data.get('size', None),
                    'ext': media_data.get('ext', None),
                    'kind': media_data['mime'].split('/')[0] if media_data.get('mime') else None,
                }
            except Exception as e:
                print(f'Could not aggregate media data: {media_data}', e)
                return None

        def aggregate_clickable_lists(list_data, layout):
            try:
                items = []
                if not list_data:
                    return []

                if layout == 'grid':
                    i = 0
                    while i < len(list_data):
                        row = []
                        for j in range(2):
                            if i < len(list_data):
                                row.append({
                                    'icon': aggregate_media_data(list_data[i]['icon']) if list_data[i]['icon'] else None,
                                    'label': list_data[i].get('label', ''),
                                    'page': list_data[i].get('page', ''),
                                })
                                i += 1
                            else:
                                break
                        items.append(row)
                        i -= 1
                else:
                    for item in list_data:
                        items.append({
                            'icon': aggregate_media_data(item['icon']) if item.get('icon') else None,
                            'label': item.get('label', None),
                            'page': item.get('page', None),
                        })
                return items
            except Exception as e:
                print('Could not aggregate list data', e)
                return None

        def aggregate_non_clickable_lists(list_data):
            try:
                items = []
                if not list_data:
                    return items

                for item in list_data:
                    items.append({
                        # TODO: check description # use agg text area
                        'description': aggregate_text_area(item['description']) if item.get('description') else None,
                        # TODO: check strapi, also media_url...
                        'icon': f'{self.media_url}{item["icon"][0]["url"]}' if item.get('icon') else None,
                    })
                return items
            except Exception as e:
                print('Could not aggregate non-clickable list data', e)
                return None

        def agg_rich_text(data):
            try:
                formatted_text = ''
                if not data:
                    return formatted_text

                for item in data:
                    if item['type'] == 'text' and item.get('text'):
                        item['text'] = item['text'].replace('\n', '<br>')

                        if item.get('bold'):
                            formatted_text += f'<b>{item["text"]}</b>'
                        elif item.get('italic'):
                            formatted_text += f'<i>{item["text"]}</i>'
                        elif item.get('underline'):
                            formatted_text += f'<u>{item["text"]}</u>'
                        elif item.get('strikethrough'):
                            formatted_text += f'<s>{item["text"]}</s>'
                        elif item.get('code'):
                            formatted_text += f'<code>{item["text"]}</code>'
                        else:
                            formatted_text += item['text']
                    if item['type'] == 'link' and item.get('url'):
                        url = item.get('url')
                        link_text = item['children'][0]['text']
                        formatted_text += f'<a href="{url}">{link_text}</a>'
                return formatted_text
            except Exception as e:
                print(f'Could not aggregate rich text data: {data}.', e)
                return None

        def aggregate_text_area(text_area_data):
            try:
                result_data = []

                if not text_area_data:
                    return result_data

                for item in text_area_data:
                    if item['type'] == 'heading':
                        level = item.get('level')
                        text = agg_rich_text(item['children']) if item['children'] else ''
                        result_data.append({
                            f'heading{level}': f'<h{level}>{text}</h{level}>'
                        })
                    elif item['type'] == 'quote':
                        text = agg_rich_text(item['children']) if item['children'] else ''
                        result_data.append({
                            'quote': f'<blockquote>{text}</blockquote>'
                        })
                    elif item['type'] == 'code':
                        text = agg_rich_text(item['children']) if item['children'] else ''
                        result_data.append({
                            'code': f'<code>{text}</code>'
                        })
                    elif item['type'] == 'paragraph':
                        result_data.append({
                            'paragraph': agg_rich_text(item['children']) if item['children'] else ''
                        })
                    elif item['type'] == 'image' and item.get('image'):
                        result_data.append({
                            'image': item['image'].get('url', None)
                        })
                    elif item['type'] == 'list':
                        list_format = item['format']
                        list_data = []
                        for y in item['children']:
                            if y['type'] == 'list-item' and y['children']:
                                agg_text = agg_rich_text(y['children']) if y['children'] else ''
                                list_data.append(agg_text)

                        if list_format == 'unordered':
                            result_data.append({
                                'unorderedList': list_data
                            })
                        elif list_format == 'ordered':
                            result_data.append({
                                'orderedList': list_data
                            })
                return result_data
            except Exception as e:
                print(f'Could not aggregate text area data: {text_area_data}', e)
                return None

        def aggregate_drop_down_content(drop_down_data):
            try:
                drop_down_content = []
                if not drop_down_data:
                    return drop_down_content

                for item in drop_down_data:
                    drop_down_content.append({
                        'title': agg_rich_text(item['title'][0]['children']) if item.get('title') else None,
                        'titleAudioUrl': item.get('dd_title_audio', None),
                        'titleAudio': {
                            'url': item.get('dd_title_audio', None),
                        },
                        'showDescription': False,
                        'description': aggregate_text_area(item['description']) if item.get('description') else None,
                    })
                return drop_down_content
            except Exception as e:
                print('Could not aggregate drop down content', e)
                return None

        def aggregate_images_slider(slider_data):
            try:
                slider_content = []
                if not slider_data:
                    return slider_content

                for item in slider_data:
                    slider_content.append({
                        'title': item.get('title', None),
                        # TODO: check image url, media url
                        'imageUrl': f'{self.media_url}{item["image"]["url"]}' if item.get('image') else None,
                        'description': aggregate_text_area(item['description']) if item.get('description') else None,
                    })
                return slider_content
            except Exception as e:
                print('Could not aggregate images slider content', e)
                return None

        def aggregate_case_study(case_study_data, sub_chapter_id=None):
            result_case_study = {
                'page_id': case_study_data.get('page_id', None),
                'page_title': case_study_data.get('page_title', None),
                'preview_title': case_study_data.get('preview_title', None),
                'last_updated': case_study_data.get('last_published_at', None),
                'analytics_event_name': case_study_data.get('analytics_event_name', None),
                'sub_chapter': sub_chapter_id,
                'type':  'case_study',
                'page_content': [],
                # TODO: add aggregation when data below is returned
                'description': [],
                # 'image': '',
                # 'page_icon': '',
                # 'pageTitleAudio': '',
            }
            if len(case_study_data['dynamic_zone']):
                components = case_study_data['dynamic_zone']
                comp_agg = aggregate_components(components)
                if not result_case_study['description']:
                    for i in comp_agg:
                        if i['type'] == 'text_area':
                            result_case_study['description'] = i['description']
                result_case_study['page_content'].extend(comp_agg)
            return result_case_study

        def aggregate_components(data, raw_page_data=None):
            agg_result = []
            for item in data:
                component_type = item['__component']
                try:
                    if component_type == 'okolabor.clickable-list' or\
                            component_type == 'common.clickable-list':
                        layout = item.get('layout', 'flow')
                        list_data = {
                            'type': 'clickable_list',
                            'layout': layout,
                            'list': aggregate_clickable_lists(item['repeatable_zone'], layout)
                        }
                        agg_result.append(list_data)
                    if component_type == 'common.non-clickable-list':
                        list_data = {
                            'type': 'non-clickable-list',
                            'heading': item.get('heading', None),
                            'list': aggregate_non_clickable_lists(item['repeatable_zone'])
                        }
                        agg_result.append(list_data)
                    if component_type == 'okolabor.illustration':
                        image_data = {
                            'type': 'illustration',
                            'mediaData': aggregate_media_data(item['image']) if item.get('image') else None,
                        }
                        agg_result.append(image_data)
                    if component_type == 'okolabor.additional-text':
                        result = aggregate_key_value_text(item['repeatable_zone'])
                        additional_text = {
                            'type': 'additional_text',
                            'additional_text': result
                        }
                        agg_result.append(additional_text)
                    if component_type == 'common.text-area':
                        text_area_data = {
                            'type': 'text_area',
                            'title': item.get('h2_title_area', None),
                            'description': aggregate_text_area(item['text_area']) if item.get('text_area') else None
                        }
                        agg_result.append(text_area_data)
                    if component_type == 'common.audio':
                        audio_data = {
                            'type': 'audio',
                            'title': item.get('audio_title', None),
                            'url': item.get('audio_link', None),
                            # TODO: check description  # use agg text area
                            'description': agg_rich_text(item['audio_description'][0]['children'])
                            if item.get('audio_description') else None,
                            'mediaData': {
                                'url': item.get('audio_link', None),
                            }
                        }
                        agg_result.append(audio_data)
                    if component_type == 'common.video-area':
                        video_data = {
                            'type': 'video',
                            'title': item.get('video_title', None),
                            'url': item.get('video_link', None),
                            'mediaData': {
                                'url': item.get('video_link', None),
                            },
                            # TODO: change when data is available
                            'thumbnail': {
                                'url': item.get('video_thumbnail', None),
                            },
                        }
                        agg_result.append(video_data)
                    if component_type == 'common.highlighted-link':
                        highlighted_link_data = {
                            'type': 'highlighted_link',
                            # TODO: test icon when data is available
                            'icon': aggregate_media_data(item['icon'][0]) if item.get('icon') else None,
                            # TODO: check description  # use agg text area
                            'description': aggregate_text_area(item['link_description']) if item.get('link_description') else None,
                            'link': item.get('highlighted_link', None),
                        }
                        agg_result.append(highlighted_link_data)
                    if component_type == 'common.case-study':
                        raw_case_study = next((el for el in lang_content['data'] if el['page_id'] == item.get('link')), None) if\
                            item.get('link') else None
                        agg_res = aggregate_case_study(raw_case_study, raw_page_data.get('page_id')) if raw_case_study else None
                        agg_result.append(agg_res)
                    if component_type == 'common.warning-box':
                        # TODO: check title & icon when data is available
                        warning_box_data = {
                            'type': 'warning_box',
                            'icon': aggregate_media_data(item['warning_icon'][0]) if item.get('warning_icon') else None,
                            'title': item.get('warning_title', None),
                            'description': aggregate_text_area(item['warning_text']) if item.get('warning_text') else None,
                        }
                        agg_result.append(warning_box_data)
                    if component_type == 'common.drop-down-content':
                        drop_down_content_data = {
                            'type': 'drop_down_content',
                            'data': aggregate_drop_down_content(item['repeatable_zone'])
                        }
                        agg_result.append(drop_down_content_data)
                    if component_type == 'common.images-slider':
                        images_slider_data = {
                            'type': 'images_slider',
                            'sliderContent': aggregate_images_slider(item['repeatable_zone'])
                        }
                        agg_result.append(images_slider_data)
                    if component_type == 'common.question':
                        # TODO: update qtn when data is updated
                        qtn_data = {
                            'type': 'question',
                            'question': agg_rich_text(item['question'][0]['children']) if item.get('question') else None,
                            'questionKey': item.get('question_key', None),
                            'questionType': item.get('question_type', None),
                            'isRequired': item.get('is_required', False),
                            'displayQuestion': item.get('display_question', False),
                        }
                        agg_result.append(qtn_data)
                except Exception as e:
                    print(f'Could not aggregate {component_type} component.', e)
                    return None
            return agg_result

        for item in lang_content['data']:
            if item['custom_type'] == 'form_questions':
                aggregation_response = aggregate_form_questions(item)
                page_data = {
                    'page_id': item['id'],
                    'page_title': item.get('page_title', None),
                    'preview_title': item.get('preview_title', None),
                    'form_questions': aggregation_response[0],
                    'additional_text': aggregation_response[1]
                }
                aggregated_content[item['page_id']] = page_data

            if item['custom_type'] == 'common_text':
                aggregation_response = aggregate_key_value_text(
                    item['dynamic_zone'])
                page_data = {
                    'page_id': item.get('page_id', None),
                    'page_title': item.get('page_title', None),
                    'preview_title': item.get('preview_title', None),
                    'data': aggregation_response
                }
                aggregated_content[item['page_id']] = page_data

            if item['custom_type'] == 'menu_content':
                aggregation_response = aggregate_menu_content(item['dynamic_zone'])
                page_data = {
                    'page_id': item.get('page_id', None),
                    'page_title': item.get('page_title', None),
                    'preview_title': item.get('preview_title', None),
                    'last_updated': item.get('last_published_at', None),
                    'data': aggregation_response
                }
                aggregated_content[item['page_id']] = page_data

            if item['custom_type'] == 'sub_chapter_list' or\
                    item['custom_type'] == 'create_content_area':
                aggregation_response = aggregate_components(item['dynamic_zone'], item)
                page_data = {
                    'page_id': item.get('page_id', None),
                    'page_title': item.get('page_title', None),
                    'preview_title': item.get('preview_title', None),
                    'last_updated': item.get('last_published_at', None),
                    'analytics_event_name': item.get('analytics_event_name', None),
                    'page_content': aggregation_response
                    # TODO: add aggregation when data below is returned
                    # 'page_icon': '',
                    # 'pageTitleAudio': '',
                }
                aggregated_content[item['page_id']] = page_data

            if item['custom_type'] == 'case_study':
                cs_agg_resp = aggregate_case_study(item)
                aggregated_content[item['page_id']] = cs_agg_resp

        return aggregated_content


class AggregatedContentView(APIView):
    @swagger_auto_schema(
        operation_summary="Retrieve aggregated content",
        tags=["Content"]
    )
    def get(self, request):
        try:
            latest = AggregatedContent.objects.latest('created_at')
            serializer = AggregatedContentSerializer(latest, many=False)
            return Response({
                'data': [serializer.data],
                'error_messages': []
            }, status.HTTP_200_OK)
        except AggregatedContent.DoesNotExist:
            return Response({}, status.HTTP_200_OK)


class StartContentAggregation(APIView):
    @swagger_auto_schema(
        operation_summary="Trigger content aggregation",
        tags=["Content"]
    )
    def get(self, request):
        api = ContentAPI()
        documents = api.start_content_fetch()
        return Response(documents, status.HTTP_200_OK)


class ContentUpdateView(APIView):
    @swagger_auto_schema(
        operation_summary="Content webhook",
        tags=["Content"]
    )
    def post(self, request):
        return Response({}, status.HTTP_200_OK)


class CompareContent(APIView):
    @swagger_auto_schema(
        operation_summary="Compare content",
        tags=["Content"]
    )
    def get(self, request):
        app_content_created_at = request.query_params.get(
            'app_content_created_at'
        )
        parsed_app_content_created_at = parse_datetime(app_content_created_at)
        latest_content = AggregatedContent.objects.order_by(
            '-created_at')[:1].get()
        serializer = AggregatedContentSerializer(latest_content, many=False)
        latest_content_created_at = parse_datetime(
            serializer.data['created_at']
        )
        if latest_content_created_at == parsed_app_content_created_at:
            return Response({
                'data': "",
                'new': False,
                'error_messages': []
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'data': serializer.data,
                'new': True,
                'error_messages': []
            }, status=status.HTTP_200_OK)
