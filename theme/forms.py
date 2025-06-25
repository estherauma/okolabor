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
        ('', 'Please select...'),
        ('Animals', _('filterSectionAnimals')),
        ('Construction', _('filterSectionConstruction')),
        ('Crop and Horticulture', _('filterSectionCropAndHorticulture')),
        ('Licensed Vehicle Operation', _('filterSectionLicensedVehicleOperation')),
        ('Mechanics', _('filterSectionMechanics')),
        ('Worker Supervision/Management', _('filterSectionWorkerSupervision/Management')),
        ('Other', _('filterSectionOther')),
    ]

    TYPE_SPECIFIC_OPTIONS = {
        'Animals': {
            'second_label': _('filterSectionAnimalType'),
            'second_choices': [
                ('Asses', _('filterSectionAsses')),
                ('Bees', _('filterSectionBees')),
                ('Buffalo', _('filterSectionBuffalo')),
            ],
            'third_label': _('filterSectionTasks'),
            'third_choices': [
                ('Breeding', _('filterSectionBreeding')),
                ('Caring', _('filterSectionCaring')),
                ('Packaging', _('filterSectionPackaging')),
            ]
        },
        'Crop and Horticulture': {
            'second_label': _('filterSectionCropType'),
            'second_choices': [
                ('Avocados', _('filterSectionAvocados')),
                ('Bananas', _('filterSectionBananas')),
                ('Brazil nuts', _('filterSectionBrazilNuts')),
            ],
            'third_label': _('filterSectionTasks'),
            'third_choices': [
                ('Cultivating', _('filterSectionCultivating')),
                ('Grading and sorting', _('filterSectionGradingAndSorting')),
                ('Harvesting', _('filterSectionHarvesting')),
                ('Other', _('filterSectionOther')),
            ]
        },
        'Mechanics': {
            'second_label': _('filterSectionTasks'),
            'second_choices': [
                ('Car', _('filterSectionCar')),
                ('Agricultural Equipment/Machinery', _('filterSectionAgriculturalEquipment/Machinery')),
            ],
            'third_label': None,
            'third_choices': None
        },
        'Worker Supervision/Management': {
            'second_label': _('filterSectionTasks'),
            'second_choices': [
                ('Animals', _('filterSectionAnimals')),
                ('Crop and Horticulture', _('filterSectionCropAndHorticulture')),
                ('Other', _('filterSectionOther')),
            ],
            'third_label': None,
            'third_choices': None
        }
        # Construction, Licensed Vehicle Operation, Other => no other fields
    }

    type_sector = forms.ChoiceField(
        choices=SECTOR_CHOICES,
        label=_("filterSectionType/Sector"),
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
        ('', 'Please select...'),
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
            ('', _('filterSectionPleaseSelect...')),
            ('fluent', _('filterSectionFluent')),
            ('advanced', _('filterSectionAdvanced')),
            ('intermediate', _('filterSectionIntermediate')),
            ('basic', _('filterSectionBasic')),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label=_('filterSectionEnglishProficiency')
    )

    availability = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'placeholder': _('filterSectionSelectAvilability'),
            'type': 'date'  
        }),
        label=_('filterSectionAvailability')
    )

    location_preference = forms.ChoiceField(
        choices=[
            ('', _('filterSectionPleaseSelect...')),
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
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'placeholder': _('filterSectionLocationPreference')
        }),
        label=_('filterSectionLocationPreference')
    )

    driver_license = forms.ChoiceField(
        choices=[
            ('', _('filterSectionPleaseSelect...')),
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
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'placeholder': _('filterSectionDriverLicense')
        }),
        label=_('filterSectionDriverLicense')
    )

    lifting = forms.ChoiceField(
        choices=[
            ('', _('filterSectionPleaseSelect...')),
            ('yes', _('filterSectionYes')),
            ('no', _('filterSectionNo')),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'placeholder': _('filterSectionAbleToLift27kgs?')
        }),
        label=_('filterSectionAbleToLift27kgs?')
    )

    time_on_feet = forms.ChoiceField(
        choices=[
            ('',  _('filterSectionPleaseSelect...')),
            ('yes',  _('filterSectionYes')),
            ('no', _('filterSectionNo')),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'placeholder': _('filterSectionWillSpendTimeOnFeet?')
        }),
        label=_('filterSectionWillSpendTimeOnFeet?')
    )

    weather = forms.ChoiceField(
        choices=[
            ('', _('filterSectionPleaseSelect...')),
            ('yes', _('filterSectionYes')),
            ('no', _('filterSectionNo')),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'placeholder': _('filterSectionWillWorkInHot&Cold?')
        }),
        label=_('filterSectionWillWorkInHot&Cold?')
    )

    offer_status = forms.ChoiceField(
        choices=[
            ('', _('filterSectionPleaseSelect...')),
            ('pending', _('filterSectionPending')),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'placeholder': _('filterSectionOfferStatus')
        }),
        label=_('filterSectionOfferStatus')
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
