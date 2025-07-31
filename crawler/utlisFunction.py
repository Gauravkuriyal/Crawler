import os
import phonenumbers
from django.core.exceptions import ValidationError

def handle_uploaded_file(f):
    ext = os.path.splitext(f.name)[1].lower()  # Get the extension and make it lowercase
    content_type = f.content_type.lower()

    # Define valid extensions and content types
    valid_extensions = {
        '.pdf': 'application/pdf',
        '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        '.xls': 'application/vnd.ms-excel',
        '.csv': 'text/csv',
        '.doc': 'application/msword',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        '.txt': 'text/plain',
        '.text': 'text/plain',
    }

    if ext not in valid_extensions:
        raise ValidationError('Unsupported file extension.')

    if content_type != valid_extensions[ext]:
        raise ValidationError('File content type does not match extension.')

    # Save the file
    with open(f'media/{f.name}', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

def filter_valid_phone_numbers(numbers):
    valid_numbers = set()
    for number in numbers:
        try:
            # Parse without specifying a default region
            parsed = phonenumbers.parse(number, None)  
            
            # Check if it's a valid and possible number
            if phonenumbers.is_possible_number(parsed) and phonenumbers.is_valid_number(parsed):
                formatted_number = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
                valid_numbers.add(formatted_number)
        
        except phonenumbers.NumberParseException as e:
            print("at end : ",e)
            continue  
        except Exception as e:
            continue
    print("at end : ", valid_numbers)
    return valid_numbers

# # Example usage:
# raw_numbers = {"+1-800-555-1234", "123456", "9786543210", "9783161484100", "+442071838750"}
# valid_phone_numbers = filter_valid_phone_numbers(raw_numbers)

# print("Valid Phone Numbers:", valid_phone_numbers)
