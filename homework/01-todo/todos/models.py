from django.db import models


class TODO(models.Model):
    """
    Model representing a TODO item.
    """
    title = models.CharField(max_length=200, help_text="Title of the TODO")
    description = models.TextField(blank=True, help_text="Detailed description of the TODO")
    due_date = models.DateTimeField(null=True, blank=True, help_text="Due date for the TODO")
    is_resolved = models.BooleanField(default=False, help_text="Whether the TODO is completed")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "TODO"
        verbose_name_plural = "TODOs"

    def __str__(self):
        return self.title
