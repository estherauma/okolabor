from django import forms
from account.models import UserWorkExperience, UserJobExperience,UserJobExperienceDetails


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
            ('Oil palm fruit', 'Oil palm fruit'),
            ('Olives', 'Olives'),
            ('Agave fibres', 'Agave fibres'),
            ('Avocados', 'Avocados'),
            ('Chillies and peppers', 'Chillies and peppers'),
            ('Garlic', 'Garlic'),
            ('Apricots', 'Apricots'),
            ('Artichokes', 'Artichokes'),
            ('Locust beans (carobs)', 'Locust beans (carobs)'),
            ('Cotton', 'Cotton'),
            ('Almonds', 'Almonds'),
            ('Canary seed', 'Canary seed'),
            ('Lupins', 'Lupins'),
            ('Anise, badian, coriander, cumin, caraway, fennel and juniper berries', 
            'Anise, badian, coriander, cumin, caraway, fennel and juniper berries'),
            ('Blueberries', 'Blueberries'),
            ('Cranberries', 'Cranberries'),
            ('Rice', 'Rice'),
            ('Hazelnuts', 'Hazelnuts'),
            ('Oats', 'Oats'),
            ('Sugar cane', 'Sugar cane'),
            ('Bananas', 'Bananas'),
            ('Sweet potatoes', 'Sweet potatoes'),
            ('Eggplants (aubergines)', 'Eggplants (aubergines)'),
            ('Coir', 'Coir'),
            ('Coffee', 'Coffee'),
            ('Pumpkins, squash and gourds', 'Pumpkins, squash and gourds'),
            ('Yautia', 'Yautia'),
            ('True hemp', 'True hemp'),
            ('Hempseed', 'Hempseed'),
            ('Cinnamon', 'Cinnamon'),
            ('Persimmons', 'Persimmons'),
            ('Chestnuts', 'Chestnuts'),
            ('Cashew nuts', 'Cashew nuts'),
            ('Rubber', 'Rubber'),
            ('Barley', 'Barley'),
            ('Onions and shallots', 'Onions and shallots'),
            ('Rye', 'Rye'),
            ('Cherries', 'Cherries'),
            ('Plums and sloes', 'Plums and sloes'),
            ('Cloves', 'Cloves'),
            ('Coconuts', 'Coconuts'),
            ('Cauliflowers and broccoli', 'Cauliflowers and broccoli'),
            ('Rape or colza seed', 'Rape or colza seed'),
            ('Dates', 'Dates'),
            ('Fonio', 'Fonio'),
            ('Asparagus', 'Asparagus'),
            ('Spinach', 'Spinach'),
            ('Raspberries', 'Raspberries'),
            ('Strawberries', 'Strawberries'),
            ('Beans', 'Beans'),
            ('Okra', 'Okra'),
            ('Soya beans', 'Soya beans'),
            ('Cocoa beans', 'Cocoa beans'),
            ('Currants', 'Currants'),
            ('Sour cherries', 'Sour cherries'),
            ('Peas', 'Peas'),
            ('Broad beans and horse beans', 'Broad beans and horse beans'),
            ('Hay', 'Hay'),
            ('Figs', 'Figs'),
            ('Tea leaves', 'Tea leaves'),
            ('Mushrooms and truffles', 'Mushrooms and truffles'),
            ('Ginger', 'Ginger'),
            ('Jojoba', 'Jojoba'),
            ('String beans', 'String beans'),
            ('Kapok', 'Kapok'),
            ('Kenaf', 'Kenaf'),
            ('Kiwi fruit', 'Kiwi fruit'),
            ('Lettuce and chicory', 'Lettuce and chicory'),
            ('Lentils', 'Lentils'),
            ('Lemons and limes', 'Lemons and limes'),
            ('Linseed', 'Linseed'),
            ('Flax', 'Flax'),
            ('Hops', 'Hops'),
            ('Wood', 'Wood'),
            ('Maize (corn)', 'Maize (corn)'),
            ('Mangoes, guavas and mangosteens', 'Mangoes, guavas and mangosteens'),
            ('Groundnuts', 'Groundnuts'),
            ('Cashewapple', 'Cashewapple'),
            ('Apples', 'Apples'),
            ('Peaches and nectarines', 'Peaches and nectarines'),
            ('Cantaloupes', 'Cantaloupes'),
            ('Quinces', 'Quinces'),
            ('Peppermint, spearmint', 'Peppermint, spearmint'),
            ('Millet', 'Millet'),
            ('Yams', 'Yams'),
            ('Oranges', 'Oranges'),
            ('Walnuts', 'Walnuts'),
            ('Areca nuts', 'Areca nuts'),
            ('Karite nuts (sheanuts)', 'Karite nuts (sheanuts)'),
            ('Tung nuts', 'Tung nuts'),
            ('Brazil nuts', 'Brazil nuts'),
            ('Kola nuts', 'Kola nuts'),
            ('Nutmeg', 'Nutmeg'),
            ('Potatoes', 'Potatoes'),
            ('Papayas', 'Papayas'),
            ('Pyrethrum', 'Pyrethrum'),
            ('Cucumbers and gherkins', 'Cucumbers and gherkins'),
            ('Pears', 'Pears'),
            ('Pepper', 'Pepper'),
            ('Pineapples', 'Pineapples'),
            ('Pistachios', 'Pistachios'),
            ('Plantains', 'Plantains'),
            ('Pomelos and grapefruits', 'Pomelos and grapefruits'),
            ('Leeks', 'Leeks'),
            ('Quinoa', 'Quinoa'),
            ('Chicory roots', 'Chicory roots'),
            ('Ramie', 'Ramie'),
            ('Cabbages', 'Cabbages'),
            ('Watermelons', 'Watermelons'),
            ('Poppy seed', 'Poppy seed'),
            ('Safflower seed', 'Safflower seed'),
            ('Sunflower seed', 'Sunflower seed'),
            ('Mustard seed', 'Mustard seed'),
            ('Sesame seed', 'Sesame seed'),
            ('Castor oil seeds', 'Castor oil seeds'),
            ('Tallowtree seeds', 'Tallowtree seeds'),
            ('Sisal', 'Sisal'),
            ('Sorghum', 'Sorghum'),
            ('Tobacco', 'Tobacco'),
            ('Tangerines, mandarins, clementines', 'Tangerines, mandarins, clementines'),
            ('Taro', 'Taro'),
            ('Tomatoes', 'Tomatoes'),
            ('Wheat', 'Wheat'),
            ('Bulgur', 'Bulgur'),
            ('Buckwheat', 'Buckwheat'),
            ('Triticale', 'Triticale'),
            ('Gooseberries', 'Gooseberries'),
            ('Grapes', 'Grapes'),
            ('Raisins', 'Raisins'),
            ('Vanilla', 'Vanilla'),
            ('Vetches', 'Vetches'),
            ('Cassava', 'Cassava'),
            ('Jute', 'Jute'),
            ('Carrots and turnips', 'Carrots and turnips'),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control custom-dropdown',
        }),
        label="Crop Type"
        )
        
    experience_type = forms.ChoiceField(
    choices=[
        ('Planting', 'Planting'),
        ('Cultivating', 'Cultivating'),
        ('Harvesting', 'Harvesting'),
        ('Packaging', 'Packaging'),
        ('Grading and sorting', 'Grading and sorting'),
        ('Other', 'Other'),
    ], 
    widget=forms.Select(attrs={
         'class': 'form-control custom-dropdown',
    }),
    label="Experience Type"
    )
    minimum_experience = forms.ChoiceField(
        choices=[
            ('0', 'No Experience'),
            ('1', '1 Year'),
            ('2', '2 Years'),
            ('3', '3 Years'),
            ('5', '5+ Years'),
        ],
        required=False,
        widget=forms.Select(attrs={
             'class': 'form-control custom-dropdown',
        }),
        label="Minimum Experience"
    )
    