from django import forms
from .models import Match

class MatchForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = ['league', 'home_team', 'away_team', 'match_date', 'status']

        widgets = {
            # 🗓️ HTML5 datetime-local widget for date + time
            'match_date': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'class': 'border border-gray-300 rounded-md p-2 w-full focus:ring-2 focus:ring-indigo-500',
                },
                format='%Y-%m-%dT%H:%M'
            ),
            'league': forms.Select(attrs={
                'class': 'border border-gray-300 rounded-md p-2 w-full focus:ring-2 focus:ring-indigo-500'
            }),
            'home_team': forms.Select(attrs={
                'class': 'border border-gray-300 rounded-md p-2 w-full focus:ring-2 focus:ring-indigo-500'
            }),
            'away_team': forms.Select(attrs={
                'class': 'border border-gray-300 rounded-md p-2 w-full focus:ring-2 focus:ring-indigo-500'
            }),
            'status': forms.TextInput(attrs={
                'class': 'border border-gray-300 rounded-md p-2 w-full focus:ring-2 focus:ring-indigo-500',
                'placeholder': 'e.g. Upcoming, Finished, Live'
            }),
        }

def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['home_team'].queryset = Club.objects.none()
        self.fields['away_team'].queryset = Club.objects.none()

        if 'league' in self.data:
            try:
                league_id = self.data.get('league')
                self.fields['home_team'].queryset = Club.objects.filter(league_id=league_id).order_by('name')
                self.fields['away_team'].queryset = Club.objects.filter(league_id=league_id).order_by('name')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            league = self.instance.league
            self.fields['home_team'].queryset = Club.objects.filter(league=league)
            self.fields['away_team'].queryset = Club.objects.filter(league=league)