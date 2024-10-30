from django import forms


class StarRatingWidget(forms.widgets.NumberInput):
    template_name = "store/star_rating_widget.html"

    # class Media:
    #     css = {
    #         'all': ('css/star_rating.css',)
    #     }
    #     js = ('js/star_rating.js',)
