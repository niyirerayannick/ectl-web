from django.db import migrations, models


def populate_cover_alt(apps, schema_editor):
	Post = apps.get_model("news", "Post")
	Post.objects.filter(cover_alt="").exclude(cover="").update(cover_alt=models.F("title"))


class Migration(migrations.Migration):

	dependencies = [
		("news", "0001_initial"),
	]

	operations = [
		migrations.AddField(
			model_name="post",
			name="cover_alt",
			field=models.CharField(blank=True, max_length=300),
		),
		migrations.RunPython(populate_cover_alt, migrations.RunPython.noop),
	]