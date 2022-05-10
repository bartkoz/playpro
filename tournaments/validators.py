from django.utils.deconstruct import deconstructible
from rest_framework.exceptions import ValidationError


@deconstructible
class ImageSizeValidator:
    def __init__(self, size_in_mb):
        self.size_in_mb = size_in_mb

    def __call__(self, image):
        if image.size > self.size_in_mb * 1024 * 1024:
            raise ValidationError(
                "Image size cannot be greater than %(MB)sMB." % {"MB": self.size_in_mb}
            )

    def __eq__(self, other):
        return self.size_in_mb == getattr(other, "size_in_mb", None)
