from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .models import TODO


class TODOModelTest(TestCase):
    """Test cases for the TODO model."""
    
    def test_create_todo_with_all_fields(self):
        """Test creating a TODO with all fields populated."""
        due_date = timezone.now() + timedelta(days=7)
        todo = TODO.objects.create(
            title="Test TODO",
            description="Test description",
            due_date=due_date
        )
        self.assertEqual(todo.title, "Test TODO")
        self.assertEqual(todo.description, "Test description")
        self.assertEqual(todo.due_date, due_date)
        self.assertFalse(todo.is_resolved)
        self.assertIsNotNone(todo.created_at)
        self.assertIsNotNone(todo.updated_at)
    
    def test_create_todo_with_only_title(self):
        """Test creating a TODO with only the required title field."""
        todo = TODO.objects.create(title="Minimal TODO")
        self.assertEqual(todo.title, "Minimal TODO")
        self.assertEqual(todo.description, "")
        self.assertIsNone(todo.due_date)
        self.assertFalse(todo.is_resolved)
    
    def test_todo_string_representation(self):
        """Test the string representation of a TODO."""
        todo = TODO.objects.create(title="My TODO")
        self.assertEqual(str(todo), "My TODO")
    
    def test_todo_default_is_resolved(self):
        """Test that is_resolved defaults to False."""
        todo = TODO.objects.create(title="New TODO")
        self.assertFalse(todo.is_resolved)
    
    def test_todo_ordering(self):
        """Test that TODOs are ordered by created_at descending."""
        todo1 = TODO.objects.create(title="First")
        todo2 = TODO.objects.create(title="Second")
        todo3 = TODO.objects.create(title="Third")
        
        todos = TODO.objects.all()
        self.assertEqual(todos[0], todo3)
        self.assertEqual(todos[1], todo2)
        self.assertEqual(todos[2], todo1)


class TODOViewTest(TestCase):
    """Test cases for TODO views."""
    
    def setUp(self):
        """Set up test client and sample data."""
        self.client = Client()
        self.todo1 = TODO.objects.create(
            title="Test TODO 1",
            description="Description 1"
        )
        self.todo2 = TODO.objects.create(
            title="Test TODO 2",
            description="Description 2",
            is_resolved=True
        )
    
    def test_home_view_displays_todos(self):
        """Test that home page displays all TODOs."""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test TODO 1")
        self.assertContains(response, "Test TODO 2")
        self.assertTemplateUsed(response, 'todos/home.html')
    
    def test_home_view_empty_list(self):
        """Test home page when no TODOs exist."""
        TODO.objects.all().delete()
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No TODOs yet")
    
    def test_create_todo_get(self):
        """Test GET request to create TODO page."""
        response = self.client.get(reverse('create_todo'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'todos/create.html')
    
    def test_create_todo_post_success(self):
        """Test creating a TODO via POST request."""
        data = {
            'title': 'New TODO',
            'description': 'New description',
        }
        response = self.client.post(reverse('create_todo'), data)
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertTrue(TODO.objects.filter(title='New TODO').exists())
    
    def test_create_todo_post_without_title(self):
        """Test that creating a TODO without title fails gracefully."""
        initial_count = TODO.objects.count()
        data = {
            'description': 'Description without title',
        }
        response = self.client.post(reverse('create_todo'), data)
        # Should not create a TODO without title
        self.assertEqual(TODO.objects.count(), initial_count)
    
    def test_edit_todo_get(self):
        """Test GET request to edit TODO page."""
        response = self.client.get(reverse('edit_todo', args=[self.todo1.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test TODO 1")
        self.assertTemplateUsed(response, 'todos/edit.html')
    
    def test_edit_todo_post_success(self):
        """Test editing a TODO via POST request."""
        data = {
            'title': 'Updated TODO',
            'description': 'Updated description',
        }
        response = self.client.post(
            reverse('edit_todo', args=[self.todo1.id]),
            data
        )
        self.assertEqual(response.status_code, 302)  # Redirect
        self.todo1.refresh_from_db()
        self.assertEqual(self.todo1.title, 'Updated TODO')
        self.assertEqual(self.todo1.description, 'Updated description')
    
    def test_edit_nonexistent_todo(self):
        """Test editing a TODO that doesn't exist."""
        response = self.client.get(reverse('edit_todo', args=[9999]))
        self.assertEqual(response.status_code, 404)
    
    def test_delete_todo_get(self):
        """Test GET request to delete confirmation page."""
        response = self.client.get(reverse('delete_todo', args=[self.todo1.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test TODO 1")
        self.assertTemplateUsed(response, 'todos/delete_confirm.html')
    
    def test_delete_todo_post_success(self):
        """Test deleting a TODO via POST request."""
        todo_id = self.todo1.id
        response = self.client.post(reverse('delete_todo', args=[todo_id]))
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertFalse(TODO.objects.filter(id=todo_id).exists())
    
    def test_delete_nonexistent_todo(self):
        """Test deleting a TODO that doesn't exist."""
        response = self.client.post(reverse('delete_todo', args=[9999]))
        self.assertEqual(response.status_code, 404)
    
    def test_toggle_resolved_todo(self):
        """Test toggling the resolved status of a TODO."""
        # Initially not resolved
        self.assertFalse(self.todo1.is_resolved)
        
        # Toggle to resolved
        response = self.client.post(reverse('toggle_resolved', args=[self.todo1.id]))
        self.assertEqual(response.status_code, 302)  # Redirect
        self.todo1.refresh_from_db()
        self.assertTrue(self.todo1.is_resolved)
        
        # Toggle back to not resolved
        response = self.client.post(reverse('toggle_resolved', args=[self.todo1.id]))
        self.assertEqual(response.status_code, 302)
        self.todo1.refresh_from_db()
        self.assertFalse(self.todo1.is_resolved)
    
    def test_toggle_nonexistent_todo(self):
        """Test toggling resolved status of non-existent TODO."""
        response = self.client.post(reverse('toggle_resolved', args=[9999]))
        self.assertEqual(response.status_code, 404)


class TODOIntegrationTest(TestCase):
    """Integration tests for complete TODO workflows."""
    
    def setUp(self):
        """Set up test client."""
        self.client = Client()
    
    def test_complete_todo_lifecycle(self):
        """Test creating, editing, resolving, and deleting a TODO."""
        # Create a TODO
        create_data = {
            'title': 'Integration Test TODO',
            'description': 'Test full lifecycle',
        }
        response = self.client.post(reverse('create_todo'), create_data)
        self.assertEqual(response.status_code, 302)
        
        todo = TODO.objects.get(title='Integration Test TODO')
        self.assertFalse(todo.is_resolved)
        
        # Edit the TODO
        edit_data = {
            'title': 'Updated Integration TODO',
            'description': 'Updated description',
        }
        response = self.client.post(reverse('edit_todo', args=[todo.id]), edit_data)
        self.assertEqual(response.status_code, 302)
        
        todo.refresh_from_db()
        self.assertEqual(todo.title, 'Updated Integration TODO')
        
        # Toggle resolved status
        response = self.client.post(reverse('toggle_resolved', args=[todo.id]))
        self.assertEqual(response.status_code, 302)
        
        todo.refresh_from_db()
        self.assertTrue(todo.is_resolved)
        
        # Delete the TODO
        response = self.client.post(reverse('delete_todo', args=[todo.id]))
        self.assertEqual(response.status_code, 302)
        
        self.assertFalse(TODO.objects.filter(id=todo.id).exists())
