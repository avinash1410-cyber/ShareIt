from django.test import TestCase
from rest_framework.test import APITestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile


class FileUploadTestCase(APITestCase):
    
    def test_successful_upload(self):
        url = reverse('upload')  # Replace with the actual URL name for file upload API
        # Use the full path to your test file
        file_path = '/home/avinash/Django_projects/EZ/fileShare/Actions/tests/test_files/filename.pptx'
        
        with open(file_path, 'rb') as f:
            file = SimpleUploadedFile(f.name, f.read(), content_type='application/vnd.ms-powerpoint')
            data = {'file': file}
            self.client.login(username='operational_user', password='password')  # Log in as operational user
            response = self.client.post(url, data, format='multipart')

        # Ensure that the response is a redirect (302) and follow the redirect
        self.assertEqual(response.status_code, 302)
        response = self.client.get(response.url)  # Follow the redirect

        # Now you can check for the message in the final response
        self.assertContains(response, 'File uploaded successfully')

    def test_unauthorized_user_upload(self):
        url = reverse('upload')  # Replace with the actual URL name for file upload API
        # Use the full path to your test file
        file_path = '/home/avinash/Django_projects/EZ/fileShare/Actions/tests/test_files/filename.pptx'
        
        with open(file_path, 'rb') as f:
            file = SimpleUploadedFile(f.name, f.read(), content_type='application/vnd.ms-powerpoint')
            data = {'file': file}
            self.client.login(username='client_user', password='password')  # Log in as a non-operational user (client)
            response = self.client.post(url, data, format='multipart')

        # Ensure that the response is a redirect (302) and follow the redirect
        self.assertEqual(response.status_code, 302)
        response = self.client.get(response.url)  # Follow the redirect
        
        # Now check for the error message
        self.assertContains(response, 'You are not authorized to access this page.')

    def test_invalid_file_type(self):
        url = reverse('upload')  # Replace with the actual URL name for file upload API
        # Use the full path to your invalid test file (e.g., text file)
        file_path = '/home/avinash/Django_projects/EZ/fileShare/Actions/tests/test_files/filename.pptx'
        
        with open(file_path, 'rb') as f:
            file = SimpleUploadedFile(f.name, f.read(), content_type='text/plain')
            data = {'file': file}
            self.client.login(username='operational_user', password='password')  # Log in as operational user
            response = self.client.post(url, data, format='multipart')

        # Ensure that the response is a redirect (302) and follow the redirect
        self.assertEqual(response.status_code, 302)
        response = self.client.get(response.url)  # Follow the redirect
        
        # Now check for the invalid file type error message
        self.assertContains(response, 'Invalid file type. Only pptx, docx, and xlsx files are allowed.')
