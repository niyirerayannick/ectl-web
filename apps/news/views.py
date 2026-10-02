"""Allow-listed news index and article detail views."""

from django.http import Http404
from django.views.generic import DetailView, ListView

from apps.core.views import HtmxFragmentMixin
from apps.news.models import Post

PUBLIC_POST_IDS = (2734, 2719)


class NewsListView(HtmxFragmentMixin, ListView):
	template_name = "news/list.html"
	context_object_name = "posts"
	paginate_by = 6
	partial_name = "news-list"

	def get_template_names(self):
		names = super().get_template_names()
		if self.request.htmx and not getattr(self.request.htmx, "history_restore_request", False):
			if self.request.htmx.boosted:
				return ["news/list.html#main"]
			return ["news/list.html#news-list"]
		return names

	def get_queryset(self):
		queryset = Post.objects.filter(status="publish", wp_id__in=PUBLIC_POST_IDS)
		category = self.request.GET.get("category")
		if category and category != "all":
			queryset = queryset.filter(category=category)
		return queryset.order_by("-published_at")


class NewsDetailView(HtmxFragmentMixin, DetailView):
	template_name = "news/detail.html"
	context_object_name = "post"
	slug_field = "slug"
	slug_url_kwarg = "slug"

	def get_queryset(self):
		return Post.objects.filter(status="publish", wp_id__in=PUBLIC_POST_IDS)

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		posts = list(Post.objects.filter(status="publish", wp_id__in=PUBLIC_POST_IDS).order_by("-published_at")[:5])
		context["recent_posts"] = [post for post in posts if post.pk != self.object.pk]
		return context
