from django.http import Http404


def dispatch_slug_path(*views):
    """
    Dispatch full path slug in iterating through a set of views.
    Http404 exceptions raised by a view lead to trying the next view
    in the list.

    This allows to plug different slug systems to the same root URL.

    Usages::

        # in urls.py
        path('<slug:slug_path>/', dispatch_slug_path(
            views.CategoryDetailView.as_view(),
            views.ArticleDetailView.as_view())),
        )
    """
    def wrapper(request, slug_path):
        args = []
        kwargs = {'slug_path': slug_path}

        not_found_exception = Http404
        for view in views:
            try:
                return view(request, *args, **kwargs)
            except Http404 as e:
                not_found_exception = e  # assign to use it outside of except block
                continue
        raise not_found_exception

    return wrapper
