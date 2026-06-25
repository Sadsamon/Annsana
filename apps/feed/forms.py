from django import forms

from .models import Comment, Post


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    """Lets a single form field accept and clean a list of uploaded files."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            return [single_file_clean(d, initial) for d in data]
        return single_file_clean(data, initial)


class PostForm(forms.ModelForm):
    images = MultipleFileField(
        required=False, help_text="Add one or more photos (optional)."
    )

    class Meta:
        model = Post
        fields = ["caption", "location"]
        widgets = {
            "caption": forms.Textarea(
                attrs={
                    "rows": 3,
                    "maxlength": 2200,
                    "class": "w-full rounded-md border border-neutral-300 px-3 py-2",
                    "placeholder": "Share something…",
                }
            ),
            "location": forms.TextInput(
                attrs={"class": "w-full rounded-md border border-neutral-300 px-3 py-2"}
            ),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["body"]
        labels = {"body": ""}
        widgets = {
            "body": forms.TextInput(
                attrs={
                    "placeholder": "Add a comment…",
                    "class": "flex-1 rounded-md border border-neutral-300 px-3 py-1 text-sm",
                }
            ),
        }
