from django import forms
from account.models import UserWorkExperience, UserJobExperience,UserJobExperienceDetails
from django.utils.translation import gettext_lazy as _

class RegistrationForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'input100',
            'placeholder': 'Username'
        })
    )
    email = forms.EmailField(
        max_length=150,
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'input100',
            'placeholder': 'Email'
        })
    )
    password = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'input100',
            'placeholder': 'Password'
        })
    )


class ResetPasswordForm(forms.Form):
    email = forms.EmailField(
        label='Email',
        max_length=100,
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 
        'placeholder': 'Enter Your Email'})
    )
class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    
    
class FilterWorkExperienceForm(forms.Form):
    crop_type = forms.ChoiceField(
        choices=[
            ('Oil palm fruit', _('oilPalmFruit')),
            ('Olives', _('olives')),
            ('Agave fibres', _('agaveFibres')),
            ('Avocados', _('avocados')),
            ('Chillies and peppers', _('chilliesAndPeppers')),
            ('Garlic', _('garlic')),
            ('Apricots', _('apricots')),
            ('Artichokes', _('artichokes')),
            ('Locust beans (carobs)', _('locustBeans(carobs)')),
            ('Cotton', _('cotton')),
            ('Almonds', _('almonds')),
            ('Canary seed', _('canarySeed')),
            ('Lupins', _('lupins')),
            ('Anise, badian, coriander, cumin, caraway, fennel and juniper berries', 
            _('aniseBadianBorianderCuminCarawayFennelAndJuniperBerries')),
            ('Blueberries', _('blueberries')),
            ('Cranberries', _('cranberries')),
            ('Rice', _('rice')),
            ('Hazelnuts', _('hazelnuts')),
            ('Oats', _('oats')),
            ('Sugar cane', _('sugarCane')),
            ('Bananas', _('bananas')),
            ('Sweet potatoes', _('sweetPotatoes')),
            ('Eggplants (aubergines)', _('eggplants(aubergines)')),
            ('Coir', _('coir')),
            ('Coffee', _('coffee')),
            ('Pumpkins, squash and gourds', _('pumpkinsSquashAndGourds')),
            ('Yautia', _('yautia')),
            ('True hemp', _('trueHemp')),
            ('Hempseed', _('hempseed')),
            ('Cinnamon', _('cinnamon')),
            ('Persimmons', _('persimmons')),
            ('Chestnuts', _('chestnuts')),
            ('Cashew nuts', _('cashewNuts')),
            ('Rubber', _('rubber')),
            ('Barley', _('barley')),
            ('Onions and shallots', _('onionsAndShallots')),
            ('Rye', _('rye')),
            ('Cherries', _('cherries')),
            ('Plums and sloes', _('plumsAndSloes')),
            ('Cloves', _('cloves')),
            ('Coconuts', _('coconuts')),
            ('Cauliflowers and broccoli', _('cauliflowersAndBroccoli')),
            ('Rape or colza seed', _('rapeOrColzaSeed')),
            ('Dates', _('dates')),
            ('Fonio', _('fonio')),
            ('Asparagus', _('asparagus')),
            ('Spinach', _('spinach')),
            ('Raspberries', _('raspberries')),
            ('Strawberries', _('strawberries')),
            ('Beans', _('beans')),
            ('Okra', _('okra')),
            ('Soya beans', _('soyaBeans')),
            ('Cocoa beans', _('cocoaBeans')),
            ('Currants', _('currants')),
            ('Sour cherries', _('sourCherries')),
            ('Peas', _('peas')),
            ('Broad beans and horse beans', _('broadBeansAndHorseBeans')),
            ('Hay', _('hay')),
            ('Figs', _('figs')),
            ('Tea leaves', _('teaLeaves')),
            ('Mushrooms and truffles', _('mushroomsAndTruffles')),
            ('Ginger', _('ginger')),
            ('Jojoba', _('jojoba')),
            ('String beans', _('stringBeans')),
            ('Kapok', _('kapok')),
            ('Kenaf', _('kenaf')),
            ('Kiwi fruit', _('kiwiFruit')),
            ('Lettuce and chicory', _('lettuceAndChicory')),
            ('Lentils', _('lentils')),
            ('Lemons and limes', _('lemonsAndLimes')),
            ('Linseed', _('linseed')),
            ('Flax', _('flax')),
            ('Hops', _('hops')),
            ('Wood', _('wood')),
            ('Maize (corn)', _('maize(corn)')),
            ('Mangoes, guavas and mangosteens', _('mangoesGuavasAndMangosteens')),
            ('Groundnuts', _('groundnuts')),
            ('Cashewapple', _('cashewapple')),
            ('Apples', _('apples')),
            ('Peaches and nectarines', _('peachesAndNectarines')),
            ('Cantaloupes', _('cantaloupes')),
            ('Quinces', _('quinces')),
            ('Peppermint, spearmint', _('peppermintSpearmint')),
            ('Millet', _('millet')),
            ('Yams', _('yams')),
            ('Oranges', _('oranges')),
            ('Walnuts', _('walnuts')),
            ('Areca nuts', _('arecaNuts')),
            ('Karite nuts (sheanuts)', _('kariteNuts(sheanuts)')),
            ('Tung nuts', _('tungNuts')),
            ('Brazil nuts', _('brazilNuts')),
            ('Kola nuts', _('kolaNuts')),
            ('Nutmeg', _('nutmeg')),
            ('Potatoes', _('potatoes')),
            ('Papayas', _('papayas')),
            ('Pyrethrum', _('pyrethrum')),
            ('Cucumbers and gherkins', _('cucumbersAndGherkins')),
            ('Pears', _('pears')),
            ('Pepper', _('pepper')),
            ('Pineapples', _('pineapples')),
            ('Pistachios', _('pistachios')),
            ('Plantains', _('plantains')),
            ('Pomelos and grapefruits', _('pomelosAndGrapefruits')),
            ('Leeks', _('leeks')),
            ('Quinoa', _('quinoa')),
            ('Chicory roots', _('chicoryRoots')),
            ('Ramie', _('ramie')),
            ('Cabbages', _('cabbages')),
            ('Watermelons', _('watermelons')),
            ('Poppy seed', _('poppySeed')),
            ('Safflower seed', _('safflowerSeed')),
            ('Sunflower seed', _('sunflowerSeed')),
            ('Mustard seed', _('mustardSeed')),
            ('Sesame seed', _('sesameSeed')),
            ('Castor oil seeds', _('castorOilSeeds')),
            ('Tallowtree seeds', _('tallowtreeSeeds')),
            ('Sisal', _('sisal')),
            ('Sorghum', _('sorghum')),
            ('Tobacco', _('tobacco')),
            ('Tangerines, mandarins, clementines', _('tangerinesMandarinsClementines')),
            ('Taro', _('taro')),
            ('Tomatoes', _('tomatoes')),
            ('Wheat', _('wheat')),
            ('Bulgur', _('bulgur')),
            ('Buckwheat', _('buckwheat')),
            ('Triticale', _('triticale')),
            ('Gooseberries', _('gooseberries')),
            ('Grapes', _('grapes')),
            ('Raisins', _('raisins')),
            ('Vanilla', _('vanilla')),
            ('Vetches', _('vetches')),
            ('Cassava', _('cassava')),
            ('Jute', _('jute')),
            ('Carrots and turnips', _('carrotsAndTurnips')),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control custom-dropdown'}),
        label=_("cropType"),
    )        
    experience_type = forms.ChoiceField(
        choices=[
            (_('Planting'), _('planting')),
            (_('Cultivating'), _('cultivating')),
            (_('Harvesting'), _('harvesting')),
            (_('Packaging'), _('packaging')),
            (_('Grading and sorting'), _('gradingAndSorting')),
            (_('Other'), _('other')),
        ],
        widget=forms.Select(attrs={'class': 'form-control custom-dropdown'}),
        label=_("experienceType")
    )
    minimum_experience = forms.ChoiceField(
        choices=[
            ('0', _('noExperience')),
            ('1', _('1year')),
            ('2', _('2years')),
            ('3', _('3years')),
            ('5', _('5+years')),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control custom-dropdown'}),
        label=_("minimumExperience")
    )


class DynamicWorkExperienceForm(forms.Form):
    SECTOR_CHOICES = [
        ('Animals', _('Animals')),
        ('Construction', _('Construction')),
        ('Crop and Horticulture', _('Crop and Horticulture')),
        ('Licensed Vehicle Operation', _('Licensed Vehicle Operation')),
        ('Mechanics', _('Mechanics')),
        ('Worker Supervision/Management', _('Worker Supervision/Management')),
        ('Other', _('Other')),
    ]

    TYPE_SPECIFIC_OPTIONS = {
        'Animals': {
            'second_label': _('Animal Type'),
            'second_choices': [
                ('Asses', _('Asses')),
                ('Bees', _('Bees')),
                ('Buffalo', _('Buffalo')),
            ],
            'third_label': _('Tasks'),
            'third_choices': [
                ('Breeding', _('Breeding')),
                ('Caring', _('Caring')),
                ('Packaging', _('Packaging')),
            ]
        },
        'Crop and Horticulture': {
            'second_label': _('Crop Type'),
            'second_choices': [
                ('Avocados', _('Avocados')),
                ('Bananas', _('Bananas')),
                ('Brazil nuts', _('Brazil nuts')),
            ],
            'third_label': _('Tasks'),
            'third_choices': [
                ('Cultivating', _('Cultivating')),
                ('Grading and sorting', _('Grading and sorting')),
                ('Harvesting', _('Harvesting')),
                ('Other', _('Other')),
            ]
        },
        'Mechanics': {
            'second_label': _('Tasks'),
            'second_choices': [
                ('Car', _('Car')),
                ('Agricultural Equipment/Machinery', _('Agricultural Equipment/Machinery')),
            ],
            'third_label': None,
            'third_choices': None
        },
        'Worker Supervision/Management': {
            'second_label': _('Tasks'),
            'second_choices': [
                ('Animals', _('Animals')),
                ('Crop and Horticulture', _('Crop and Horticulture')),
                ('Other', _('Other')),
            ],
            'third_label': None,
            'third_choices': None
        }
        # Construction, Licensed Vehicle Operation, Other => no other fields
    }

    type_sector = forms.ChoiceField(
        choices=SECTOR_CHOICES,
        label=_("Type / Sector"),
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_type_sector'}),
    )

    # These are dynamic placeholders; values will be updated client-side via JavaScript
    dynamic_field_1 = forms.ChoiceField(
        choices=[],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_dynamic_field_1'}),
        label=_(""),
    )

    dynamic_field_2 = forms.ChoiceField(
        choices=[],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_dynamic_field_2'}),
        label=_(""),
    )

        
class AdvancedFilterForm(forms.Form):
    choices = [
        ('no_experience', 'No experience'),
        ('1_week', '1 week'),
        ('2_weeks', '2 weeks'),
        ('3_weeks', '3 weeks'),
        ('1_month', '1 month'),
        ('2_months', '2 months'),
        ('3_months', '3 months'),
        ('1_year', '1 year'),
        ('2_years', '2 years'),
        ('3_years', '3 years'),
    ]
    
    # experience = forms.ChoiceField(
    #     choices=choices,
    #     widget=forms.Select(attrs={'class': 'form-control'}),
    #     label='H2A Experience'
    # )

    english_proficiency = forms.ChoiceField(
        choices=[
            ('fluent', 'Fluent'),
            ('advanced', 'Advanced'),
            ('intermediate', 'Intermediate'),
            ('basic', 'Basic'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='English proficiency'
    )

    availability = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'placeholder': 'Select availability',
            'type': 'date'  
        }),
        label='Availability'
    )

    location_preference = forms.ChoiceField(
        choices=[
            ('mexico', 'Mexico'),
            ('united_states', 'United States'),
            ('afghanistan', 'Afghanistan'),
            ('albania', 'Albania'),
            ('algeria', 'Algeria'),
            ('american_samoa', 'American Samoa'),
            ('andorra', 'Andorra'),
            ('angola', 'Angola'),
            ('anguilla', 'Anguilla'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control',
            'placeholder': 'Location preference'
        }),
        label='Location preference'
    )

    driver_license = forms.ChoiceField(
        choices=[
            ('united_states', 'United States'),
            ('mexico', 'Mexico'),
            ('afghanistan', 'Afghanistan'),
            ('albania', 'Albania'),
            ('algeria', 'Algeria'),
            ('american_samoa', 'American Samoa'),
            ('andorra', 'Andorra'),
            ('angola', 'Angola'),
            ('anguilla', 'Anguilla'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control',
            'placeholder': 'Driver license'
        }),
        label='Driver license'
    )

    lifting = forms.ChoiceField(
        choices=[
            ('yes', 'Yes'),
            ('no', 'No'),
        ],
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'placeholder': 'Able to lift 27kgs'
        }),
        label='Able to lift 27kgs?'
    )

    time_on_feet = forms.ChoiceField(
        choices=[
            ('yes', 'Yes'),
            ('no', 'No'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control',
            'placeholder': 'Will spend time on feet'
        }),
        label='Will spend time on feet?'
    )

    weather = forms.ChoiceField(
        choices=[
            ('yes', 'Yes'),
            ('no', 'No'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control',
            'placeholder': 'Will work in hot & cold?'
        }),
        label='Will work in hot & cold?'
    )

    offer_status = forms.ChoiceField(
        choices=[
            ('pending', 'Pending'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control',
            'placeholder': 'Offer status'
        }),
        label='Offer status'
    )

    # 👇👇 These fields are moved to the bottom 👇👇

    # total_experience = forms.ChoiceField(
    #     choices=[
    #         ('no_experience', 'No experience'),
    #         ('1_week', '1 week'),
    #         ('2_weeks', '2 weeks'),
    #         ('3_weeks', '3 weeks'),
    #         ('1_month', '1 month'),
    #         ('2_months', '2 months'),
    #         ('3_months', '3 months'),
    #         ('1_year', '1 year'),
    #         ('2_years', '2 years'),
    #         ('3_years', '3 years'),
    #     ],
    #     widget=forms.Select(attrs={'class': 'form-control'}),
    #     label='Total years of experience'
    # )

    # documented_experience = forms.ChoiceField(
    #     choices=[
    #         ('yes', 'Yes'),
    #         ('no', 'No'),
    #     ],
    #     widget=forms.Select(attrs={'class': 'form-control'}),
    #     label='Documented experience'
    # )

    # from_worker_order = forms.ChoiceField(
    #     choices=[
    #         ('322543', '322543'),
    #         ('123456', '123456'),
    #         ('654321', '654321'),
    #         ('987654', '987654'),
    #         ('112233', '112233'),
    #     ],
    #     widget=forms.Select(attrs={
    #         'class': 'form-control',
    #         'placeholder': 'From worker order'
    #     }),
    #     label='From worker order'
    # )

    # requested_employer = forms.ChoiceField(
    #     choices=[
    #         ('utah_farms', 'Utah Farms'),
    #         ('employer_1', 'Employer 1'), 
    #         ('employer_2', 'Employer 2'),
    #         ('employer_3', 'Employer 3'),
    #     ],
    #     widget=forms.Select(attrs={
    #         'class': 'form-control',
    #         'placeholder': 'Requested employer'
    #     }),
    #     label='Requested employer'
    # )
