from django.contrib.auth.decorators import login_required

# class LoginRequiredView(View):
#     @classmethod
#     def as_view(cls, **initkwargs):
#         return login_required(super().as_view(**initkwargs))


class LoginRequiredViewMixin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        return login_required(super().as_view(**initkwargs))